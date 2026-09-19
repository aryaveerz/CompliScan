"""
CompliScan LM — Professional DOCX Inspection Report Service.
Generates an authoritative, editable regulatory inspection report directly from FinalAuditRecord.
Strictly maintains 1:1 data parity with the official PDF report.
"""

import io
from typing import Dict, Any, List
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

from backend.app.models.final_audit import FinalAuditRecord
from backend.app.core.errors import ValidationError


def _set_cell_background(cell, hex_color: str):
    """Set the background color of a table cell."""
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)


def _set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set internal cell padding (in twips, 1 pt = 20 twips)."""
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)


def _set_table_borders(table, color="CBD5E1", sz="4"):
    """Apply clean subtle borders to an entire table."""
    tblPr = table._element.xpath('w:tblPr')
    if tblPr:
        borders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            f'<w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:right w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:insideV w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'</w:tblBorders>'
        )
        tblPr[0].append(borders)


class DOCXReportService:
    """
    Service for generating formatted DOCX inspection reports directly from FinalAuditRecord.
    """

    @staticmethod
    def generate_docx_report(final_record: FinalAuditRecord) -> bytes:
        if not final_record:
            raise ValidationError("FinalAuditRecord is required to generate inspection report")

        doc = docx.Document()

        # Page Setup (Letter, 0.5 in margins for compact regulatory formatting)
        for section in doc.sections:
            section.page_width = Inches(8.5)
            section.page_height = Inches(11.0)
            section.top_margin = Inches(0.5)
            section.bottom_margin = Inches(0.5)
            section.left_margin = Inches(0.5)
            section.right_margin = Inches(0.5)

        # Set default font
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Calibri'
        font.size = Pt(9.5)
        font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)

        # ── 1. Header Banner ──────────────────────────────────────────────────
        p_sub = doc.add_paragraph()
        p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_sub.paragraph_format.space_before = Pt(0)
        p_sub.paragraph_format.space_after = Pt(2)
        r_sub = p_sub.add_run("LEGAL METROLOGY (PACKAGED COMMODITIES) RULES, 2011")
        r_sub.font.size = Pt(9)
        r_sub.font.bold = True
        r_sub.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

        p_title = doc.add_paragraph()
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_title.paragraph_format.space_before = Pt(0)
        p_title.paragraph_format.space_after = Pt(8)
        r_title = p_title.add_run("OFFICIAL REGULATORY INSPECTION & COMPLIANCE REPORT")
        r_title.font.size = Pt(14)
        r_title.font.bold = True
        r_title.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

        # ── 2. Inspection Context Snapshot Table ─────────────────────────────
        ctx = final_record.inspection_context_snapshot or {}
        t_ctx = doc.add_table(rows=4, cols=4)
        t_ctx.alignment = WD_TABLE_ALIGNMENT.CENTER
        _set_table_borders(t_ctx, "CBD5E1", "4")

        ctx_rows = [
            ("Inspection ID:", final_record.inspection_id, "Case Number:", ctx.get("case_number", "N/A")),
            ("Product Name:", ctx.get("product_name", "N/A"), "Origin Status:", ctx.get("origin_status", "UNKNOWN")),
            ("Rule-Set ID / Ver:", f"{final_record.rule_set_id} ({final_record.rule_set_version})", "Evaluation Ver:", final_record.evaluation_version),
            (
                "Finalized Timestamp:",
                final_record.finalized_at.strftime("%Y-%m-%d %H:%M:%S UTC") if final_record.finalized_at else "N/A",
                "Final Record ID:",
                final_record.id,
            ),
        ]

        for i, row in enumerate(t_ctx.rows):
            label1, val1, label2, val2 = ctx_rows[i]
            # Col 0 (Label 1)
            row.cells[0].text = label1
            row.cells[0].paragraphs[0].runs[0].font.bold = True
            row.cells[0].paragraphs[0].runs[0].font.size = Pt(8.5)
            _set_cell_background(row.cells[0], "F8FAFC")
            _set_cell_margins(row.cells[0], 60, 60, 100, 100)

            # Col 1 (Value 1)
            row.cells[1].text = str(val1)
            row.cells[1].paragraphs[0].runs[0].font.size = Pt(8.5)
            _set_cell_margins(row.cells[1], 60, 60, 100, 100)

            # Col 2 (Label 2)
            row.cells[2].text = label2
            row.cells[2].paragraphs[0].runs[0].font.bold = True
            row.cells[2].paragraphs[0].runs[0].font.size = Pt(8.5)
            _set_cell_background(row.cells[2], "F8FAFC")
            _set_cell_margins(row.cells[2], 60, 60, 100, 100)

            # Col 3 (Value 2)
            row.cells[3].text = str(val2)
            row.cells[3].paragraphs[0].runs[0].font.size = Pt(8.5)
            _set_cell_margins(row.cells[3], 60, 60, 100, 100)

        # Set column widths
        for row in t_ctx.rows:
            row.cells[0].width = Inches(1.5)
            row.cells[1].width = Inches(2.25)
            row.cells[2].width = Inches(1.5)
            row.cells[3].width = Inches(2.25)

        doc.add_paragraph().paragraph_format.space_after = Pt(4)

        # ── 3. Master Final Legal Determination Banner ───────────────────────
        is_compliant = final_record.final_decision in ("COMPLIANT", "PASS")
        dec_bg = "ECFDF5" if is_compliant else "FEF2F2"
        dec_border = "10B981" if is_compliant else "EF4444"
        dec_text_rgb = RGBColor(0x06, 0x5F, 0x46) if is_compliant else RGBColor(0x99, 0x1B, 0x1B)

        t_dec = doc.add_table(rows=2, cols=1)
        t_dec.alignment = WD_TABLE_ALIGNMENT.CENTER
        _set_table_borders(t_dec, dec_border, "8")
        _set_cell_background(t_dec.rows[0].cells[0], dec_bg)
        _set_cell_background(t_dec.rows[1].cells[0], dec_bg)
        _set_cell_margins(t_dec.rows[0].cells[0], 80, 40, 120, 120)
        _set_cell_margins(t_dec.rows[1].cells[0], 40, 80, 120, 120)
        t_dec.rows[0].cells[0].width = Inches(7.5)
        t_dec.rows[1].cells[0].width = Inches(7.5)

        p_d1 = t_dec.rows[0].cells[0].paragraphs[0]
        r_d1_lbl = p_d1.add_run("FINAL ADJUDICATED DETERMINATION: ")
        r_d1_lbl.font.bold = True
        r_d1_lbl.font.size = Pt(10.5)
        r_d1_val = p_d1.add_run(str(final_record.final_decision))
        r_d1_val.font.bold = True
        r_d1_val.font.size = Pt(11)
        r_d1_val.font.color.rgb = dec_text_rgb

        p_d2 = t_dec.rows[1].cells[0].paragraphs[0]
        r_d2_lbl = p_d2.add_run("Adjudication Rationale: ")
        r_d2_lbl.font.bold = True
        r_d2_lbl.font.size = Pt(9)
        r_d2_val = p_d2.add_run(str(final_record.final_rationale))
        r_d2_val.font.size = Pt(9)

        doc.add_paragraph().paragraph_format.space_after = Pt(4)

        # ── 4. Section 1: Evidence Inventory ─────────────────────────────────
        p_sec1 = doc.add_paragraph()
        p_sec1.paragraph_format.space_before = Pt(8)
        p_sec1.paragraph_format.space_after = Pt(4)
        r_sec1 = p_sec1.add_run("1. Evidence Inventory & Cryptographic Integrity Hashes")
        r_sec1.font.bold = True
        r_sec1.font.size = Pt(10.5)
        r_sec1.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

        evidence_list = final_record.evidence_snapshot or []
        t_ev = doc.add_table(rows=1 + len(evidence_list), cols=4)
        t_ev.alignment = WD_TABLE_ALIGNMENT.CENTER
        _set_table_borders(t_ev, "CBD5E1", "4")

        # Header
        ev_headers = ["Evidence ID", "Filename / View", "Size", "SHA-256 Integrity Hash (Tamper-Proof)"]
        for j, h in enumerate(ev_headers):
            cell = t_ev.rows[0].cells[j]
            cell.text = h
            cell.paragraphs[0].runs[0].font.bold = True
            cell.paragraphs[0].runs[0].font.size = Pt(8.5)
            _set_cell_background(cell, "E2E8F0")
            _set_cell_margins(cell, 60, 60, 80, 80)

        t_ev.rows[0].cells[0].width = Inches(1.1)
        t_ev.rows[0].cells[1].width = Inches(1.8)
        t_ev.rows[0].cells[2].width = Inches(0.8)
        t_ev.rows[0].cells[3].width = Inches(3.8)

        for i, ev in enumerate(evidence_list, start=1):
            row = t_ev.rows[i]
            row.cells[0].text = ev.get("id", "N/A")
            row.cells[1].text = f"{ev.get('original_filename', 'N/A')} ({ev.get('evidence_type', 'PRIMARY')})"
            row.cells[2].text = f"{ev.get('file_size_bytes', 0) // 1024} KB"
            row.cells[3].text = ev.get("sha256_hash", "N/A")

            for j in range(4):
                if row.cells[j].paragraphs[0].runs:
                    row.cells[j].paragraphs[0].runs[0].font.size = Pt(8)
                    if j == 3:
                        row.cells[j].paragraphs[0].runs[0].font.name = "Consolas"
                _set_cell_margins(row.cells[j], 40, 40, 80, 80)

            row.cells[0].width = Inches(1.1)
            row.cells[1].width = Inches(1.8)
            row.cells[2].width = Inches(0.8)
            row.cells[3].width = Inches(3.8)

        doc.add_paragraph().paragraph_format.space_after = Pt(4)

        # ── 5. Section 2: Applicability Assessment ───────────────────────────
        p_sec2 = doc.add_paragraph()
        p_sec2.paragraph_format.space_before = Pt(8)
        p_sec2.paragraph_format.space_after = Pt(4)
        r_sec2 = p_sec2.add_run("2. Mandatory Requirement Applicability")
        r_sec2.font.bold = True
        r_sec2.font.size = Pt(10.5)
        r_sec2.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

        app_list = final_record.applicability_snapshot or []
        t_app = doc.add_table(rows=1 + len(app_list), cols=4)
        t_app.alignment = WD_TABLE_ALIGNMENT.CENTER
        _set_table_borders(t_app, "CBD5E1", "4")

        app_headers = ["Requirement", "Applicability Status", "Statutory Citation", "Legal Basis / Rule Logic"]
        for j, h in enumerate(app_headers):
            cell = t_app.rows[0].cells[j]
            cell.text = h
            cell.paragraphs[0].runs[0].font.bold = True
            cell.paragraphs[0].runs[0].font.size = Pt(8.5)
            _set_cell_background(cell, "E2E8F0")
            _set_cell_margins(cell, 60, 60, 80, 80)

        t_app.rows[0].cells[0].width = Inches(1.6)
        t_app.rows[0].cells[1].width = Inches(1.3)
        t_app.rows[0].cells[2].width = Inches(1.4)
        t_app.rows[0].cells[3].width = Inches(3.2)

        for i, item in enumerate(app_list, start=1):
            row = t_app.rows[i]
            row.cells[0].text = item.get("requirement_name", "N/A")
            row.cells[1].text = item.get("status", "N/A")
            row.cells[2].text = item.get("rule_citation", "N/A")
            row.cells[3].text = item.get("basis", "N/A")

            for j in range(4):
                if row.cells[j].paragraphs[0].runs:
                    row.cells[j].paragraphs[0].runs[0].font.size = Pt(8)
                    if j == 0:
                        row.cells[j].paragraphs[0].runs[0].font.bold = True
                _set_cell_margins(row.cells[j], 40, 40, 80, 80)

            row.cells[0].width = Inches(1.6)
            row.cells[1].width = Inches(1.3)
            row.cells[2].width = Inches(1.4)
            row.cells[3].width = Inches(3.2)

        doc.add_paragraph().paragraph_format.space_after = Pt(4)

        # ── 6. Section 3: Compliance Findings vs Reviewer Adjudication ────────
        p_sec3 = doc.add_paragraph()
        p_sec3.paragraph_format.space_before = Pt(8)
        p_sec3.paragraph_format.space_after = Pt(4)
        r_sec3 = p_sec3.add_run("3. Compliance Evaluation vs Reviewer Adjudication")
        r_sec3.font.bold = True
        r_sec3.font.size = Pt(10.5)
        r_sec3.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

        findings_map = {f.get("requirement_name"): f for f in (final_record.compliance_findings_snapshot or [])}
        decisions_map = {d.get("requirement_name"): d for d in (final_record.reviewer_decisions_snapshot or [])}
        all_reqs = sorted(list(set(findings_map.keys()) | set(decisions_map.keys())))

        t_comp = doc.add_table(rows=1 + len(all_reqs), cols=5)
        t_comp.alignment = WD_TABLE_ALIGNMENT.CENTER
        _set_table_borders(t_comp, "CBD5E1", "4")

        comp_headers = [
            "Requirement",
            "Automated System Finding",
            "Reviewer Action",
            "Final Adjudicated Result",
            "Reviewer Rationale / Override Reason",
        ]
        for j, h in enumerate(comp_headers):
            cell = t_comp.rows[0].cells[j]
            cell.text = h
            cell.paragraphs[0].runs[0].font.bold = True
            cell.paragraphs[0].runs[0].font.size = Pt(8.5)
            _set_cell_background(cell, "E2E8F0")
            _set_cell_margins(cell, 60, 60, 80, 80)

        t_comp.rows[0].cells[0].width = Inches(1.4)
        t_comp.rows[0].cells[1].width = Inches(1.4)
        t_comp.rows[0].cells[2].width = Inches(1.1)
        t_comp.rows[0].cells[3].width = Inches(1.2)
        t_comp.rows[0].cells[4].width = Inches(2.4)

        for i, req in enumerate(all_reqs, start=1):
            f = findings_map.get(req, {})
            d = decisions_map.get(req, {})

            sys_res = f.get("result", "NOT_EVALUATED")
            rev_det = d.get("determination", "CONFIRMED")
            adj_res = d.get("adjudicated_result", sys_res)
            is_over = d.get("is_override", False)
            rat = d.get("rationale", f.get("reason", "No recorded rationale"))
            action_text = "OVERRIDE" if is_over else str(rev_det)

            row = t_comp.rows[i]
            row.cells[0].text = req
            row.cells[1].text = str(sys_res)
            row.cells[2].text = action_text
            row.cells[3].text = str(adj_res)
            row.cells[4].text = str(rat)

            for j in range(5):
                if row.cells[j].paragraphs[0].runs:
                    row.cells[j].paragraphs[0].runs[0].font.size = Pt(8)
                    if j in (0, 3):
                        row.cells[j].paragraphs[0].runs[0].font.bold = True
                _set_cell_margins(row.cells[j], 40, 40, 80, 80)

            row.cells[0].width = Inches(1.4)
            row.cells[1].width = Inches(1.4)
            row.cells[2].width = Inches(1.1)
            row.cells[3].width = Inches(1.2)
            row.cells[4].width = Inches(2.4)

        doc.add_paragraph().paragraph_format.space_after = Pt(6)

        # ── 7. Section 4: Official Certification & Archival Seal ─────────────
        t_sign = doc.add_table(rows=2, cols=2)
        t_sign.alignment = WD_TABLE_ALIGNMENT.CENTER
        _set_table_borders(t_sign, "94A3B8", "4")
        _set_cell_background(t_sign.rows[0].cells[0], "F1F5F9")
        _set_cell_background(t_sign.rows[0].cells[1], "F1F5F9")
        _set_cell_background(t_sign.rows[1].cells[0], "F8FAFC")
        _set_cell_background(t_sign.rows[1].cells[1], "F8FAFC")

        t_sign.rows[0].cells[0].text = "OFFICIAL REGULATORY CERTIFICATION"
        t_sign.rows[0].cells[0].paragraphs[0].runs[0].font.bold = True
        t_sign.rows[0].cells[0].paragraphs[0].runs[0].font.size = Pt(8.5)

        t_sign.rows[0].cells[1].text = "IMMUTABLE ARCHIVAL SEAL"
        t_sign.rows[0].cells[1].paragraphs[0].runs[0].font.bold = True
        t_sign.rows[0].cells[1].paragraphs[0].runs[0].font.size = Pt(8.5)

        t_sign.rows[1].cells[0].text = (
            "This report is generated from the immutable Legal Metrology FinalAuditRecord snapshot. "
            "All automated AI extractions and deterministic rules served strictly as regulatory assistance. "
            "The final legal determination herein represents the authoritative decision of the authorized Reviewer."
        )
        t_sign.rows[1].cells[0].paragraphs[0].runs[0].font.size = Pt(8)

        t_sign.rows[1].cells[1].text = (
            f"Finalized By User ID: {final_record.finalized_by_id}\n"
            f"Archival Record ID: {final_record.id}\n"
            f"Audit State: FINALIZED & READ_ONLY"
        )
        t_sign.rows[1].cells[1].paragraphs[0].runs[0].font.size = Pt(8)

        for r in t_sign.rows:
            r.cells[0].width = Inches(4.3)
            r.cells[1].width = Inches(3.2)
            _set_cell_margins(r.cells[0], 60, 60, 100, 100)
            _set_cell_margins(r.cells[1], 60, 60, 100, 100)

        # Output to buffer
        buffer = io.BytesIO()
        doc.save(buffer)
        return buffer.getvalue()
