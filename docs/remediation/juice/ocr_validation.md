# CompliScan LM — PaddleOCR ONNX Perceptual Extraction Audit

## 1. Perceptual Engine Architecture
Perception is executed locally without network latency or external API dependencies using **PaddleOCR ONNX** (DBNet text detection + SVTR text recognition).

- **Execution Engine**: `paddleocr-onnx`
- **Inference Runtime**: CPU / DirectML ONNXRuntime
- **Output Artifact**: `OCRResult` containing an ordered list of `ocr_tokens` with normalized bounding polygons `[x1, y1, x2, y2]`, character-level confidence scores, and token indices (`0` to `N-1`).

---

## 2. Juice Dataset Perceptual Evaluation

### Image 1: `IMG_20260920_040854.jpg` (Principal Display Panel / Front)
- **SHA-256**: `7987f3a2fcc2601d82ebb79504ecbaee6f3c5964a31f63607728396fcda45a73`
- **Sharpness Score**: 407.9 (Classification: `USABLE`)
- **Tokens Extracted**: 34 tokens
- **Key Extracted Text**: `"Real"`, `"Fruit"`, `"Power"`, `"Mixed"`, `"Fruit"`, `"Juice"`, `"1000 ml"`, `"1L"`, `"No Added Preservatives"`

### Image 2: `IMG_20260920_040900.jpg` (Ingredients & Nutritional Panel)
- **SHA-256**: `d0891ea5c2d12522deb98ca8e259583fa259ad6306359dfab0a5eb274777ad00`
- **Sharpness Score**: 209.3 (Classification: `USABLE`)
- **Tokens Extracted**: 6 tokens
- **Key Extracted Text**: `"Mixed Fruit Beverage"`, `"Ingredients:"`, `"Water"`, `"Mixed Fruit Concentrate"`

### Image 3: `IMG_20260920_040906.jpg` (Manufacturer & Customer Care Panel)
- **SHA-256**: `95db45287da0969ecefff09dec87af5052488507b0395d1d08b4ddcd410730b8`
- **Sharpness Score**: 238.5 (Classification: `USABLE`)
- **Tokens Extracted**: 70 tokens
- **Key Extracted Text**: `"Manufactured & Marketed by Dabur India Limited"`, `"Regd. Office: 8/3, Asaf Ali Road, New Delhi 110002"`, `"Consumer Care Toll Free: 1800-103-1644"`, `"Email: daburcares@feedback.dabur"`, `"Kaushambi, Sahibabad, Ghaziabad 201010"`

### Image 4: `IMG_20260920_040922.jpg` (MRP & Date / Gable Top)
- **SHA-256**: `919b9530ea24a31f172b73fea330754e15c5349d0cdc4aca22f64d7812a3226c`
- **Sharpness Score**: 252.3 (Classification: `USABLE`)
- **Tokens Extracted**: 7 tokens
- **Key Extracted Text**: `"MRP Rs. 146.00"`, `"Incl. of all taxes"`, `"Mfd: 07/2026"`, `"Batch No: D2607"`

---

## 3. OCR Token Schema Sample
```json
{
  "token_index": 0,
  "text": "Real Fruit Power",
  "confidence": 0.982,
  "bounding_box": [124, 450, 480, 520],
  "normalized_box": [0.124, 0.450, 0.480, 0.520]
}
```
All tokens are persisted in `backend/app/models/ocr.py` (`ocr_results.tokens`) and mirrored in `post_remediation/image_X/ocr_tokens.json`.
