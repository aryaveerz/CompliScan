"""
CompliScan LM — OCR Perception Service.
PaddleOCR PP-OCRv4 detection and recognition pipeline via ONNX Runtime.
Produces structured perception tokens with original-coordinate bounding boxes.
Strictly decoupled from downstream semantic extraction and legal compliance.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import io
from typing import List, Optional, Dict, Any
import numpy as np
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.core.errors import AnalysisError
from backend.app.models.evidence import EvidenceAsset
from backend.app.models.ocr import OCRResult


OCR_ENGINE_NAME = "paddleocr-onnx"
OCR_ENGINE_VERSION = "rapidocr-onnxruntime==1.2.3+onnxruntime==1.30.0"
PROCESSING_VERSION = "v1.0"


@dataclass
class OCRRawResult:
    tokens: List[Dict[str, Any]]
    full_text: str
    total_tokens: int
    ocr_engine: str
    ocr_engine_version: str
    processing_version: str


class OCRService:
    """
    Perception service implementing the PaddleOCR PP-OCRv4 pipeline.
    """

    _engine = None

    @classmethod
    def get_engine(cls):
        """Lazy initialization of RapidOCR ONNX inference engine."""
        if cls._engine is None:
            from rapidocr_onnxruntime import RapidOCR
            cls._engine = RapidOCR()
        return cls._engine

    @classmethod
    def process_image_bytes(
        cls,
        content: bytes,
        mime_type: str = "image/jpeg",
    ) -> OCRRawResult:
        """
        Execute PP-OCRv4 text detection and recognition on raw image bytes.

        - Operates on immutable in-memory copy without altering original evidence bytes.
        - Transforms detected bounding boxes to original image pixel coordinates.
        - Preserves literal character sequences without semantic normalization.
        """
        try:
            with Image.open(io.BytesIO(content)) as pil_img:
                # Ensure RGB mode for NumPy conversion
                if pil_img.mode != "RGB":
                    converted_img = pil_img.convert("RGB")
                else:
                    converted_img = pil_img.copy()

                img_np = np.array(converted_img)
        except Exception as e:
            raise AnalysisError(f"Failed to decode image bytes for OCR: {str(e)}")

        engine = cls.get_engine()
        raw_output, _elapse = engine(img_np)

        tokens: List[Dict[str, Any]] = []

        if raw_output:
            for idx, item in enumerate(raw_output):
                # item format: [box_points, text, confidence]
                box_points, text, score = item
                confidence_val = float(score) if score is not None else 0.0

                # Ensure 4-point structure [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
                points_clean = []
                for pt in box_points:
                    points_clean.append([round(float(pt[0]), 2), round(float(pt[1]), 2)])

                token_dict = {
                    "token_index": idx,
                    "line_index": idx,
                    "text": str(text),
                    "confidence": round(confidence_val, 4),
                    "bounding_box": {
                        "points": points_clean,
                        "coordinate_space": "original_image",
                    },
                }
                tokens.append(token_dict)

        full_text = "\n".join(t["text"] for t in tokens) if tokens else ""

        return OCRRawResult(
            tokens=tokens,
            full_text=full_text,
            total_tokens=len(tokens),
            ocr_engine=OCR_ENGINE_NAME,
            ocr_engine_version=OCR_ENGINE_VERSION,
            processing_version=PROCESSING_VERSION,
        )

    @classmethod
    async def persist_ocr_result(
        cls,
        db: AsyncSession,
        evidence: EvidenceAsset,
        raw_result: OCRRawResult,
    ) -> OCRResult:
        """
        Persist OCR perception tokens idempotently by (evidence_id, processing_version).
        """
        now = datetime.now(timezone.utc)

        stmt = select(OCRResult).where(
            OCRResult.evidence_id == evidence.id,
            OCRResult.processing_version == raw_result.processing_version,
        )
        existing = (await db.execute(stmt)).scalar_one_or_none()

        if existing:
            existing.ocr_engine = raw_result.ocr_engine
            existing.ocr_engine_version = raw_result.ocr_engine_version
            existing.processing_blocked = False
            existing.block_reason = None
            existing.total_tokens = raw_result.total_tokens
            existing.full_text = raw_result.full_text
            existing.tokens = raw_result.tokens
            existing.updated_at = now
            await db.flush()
            return existing

        new_result = OCRResult(
            evidence_id=evidence.id,
            inspection_id=evidence.inspection_id,
            ocr_engine=raw_result.ocr_engine,
            ocr_engine_version=raw_result.ocr_engine_version,
            processing_version=raw_result.processing_version,
            processing_blocked=False,
            block_reason=None,
            total_tokens=raw_result.total_tokens,
            full_text=raw_result.full_text,
            tokens=raw_result.tokens,
            created_at=now,
            updated_at=now,
        )
        db.add(new_result)
        await db.flush()
        return new_result

    @classmethod
    async def persist_blocked_result(
        cls,
        db: AsyncSession,
        evidence: EvidenceAsset,
        block_reason: str,
    ) -> OCRResult:
        """
        Persist an engineering blocked state when image quality gating rejects the asset.
        Does not produce compliance findings or legal determinations.
        """
        now = datetime.now(timezone.utc)

        stmt = select(OCRResult).where(
            OCRResult.evidence_id == evidence.id,
            OCRResult.processing_version == PROCESSING_VERSION,
        )
        existing = (await db.execute(stmt)).scalar_one_or_none()

        if existing:
            existing.ocr_engine = OCR_ENGINE_NAME
            existing.ocr_engine_version = OCR_ENGINE_VERSION
            existing.processing_blocked = True
            existing.block_reason = block_reason
            existing.total_tokens = 0
            existing.full_text = None
            existing.tokens = []
            existing.updated_at = now
            await db.flush()
            return existing

        new_result = OCRResult(
            evidence_id=evidence.id,
            inspection_id=evidence.inspection_id,
            ocr_engine=OCR_ENGINE_NAME,
            ocr_engine_version=OCR_ENGINE_VERSION,
            processing_version=PROCESSING_VERSION,
            processing_blocked=True,
            block_reason=block_reason,
            total_tokens=0,
            full_text=None,
            tokens=[],
            created_at=now,
            updated_at=now,
        )
        db.add(new_result)
        await db.flush()
        return new_result
