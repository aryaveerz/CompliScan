"""
CompliScan LM — Professional PDF Inspection Report Service.
Generates an authoritative, immutable regulatory inspection report directly from FinalAuditRecord.
Strictly distinguishes automated system findings from human reviewer adjudications.
"""

import io
from datetime import datetime
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable,
)
from reportlab.lib.units import inch

from backend.app.models.final_audit import FinalAuditRecord
from backend.app.core.errors import ValidationError


class PDFReportService:

    @staticmethod
    def generate_pdf_report(final_record: FinalAuditRecord) -> bytes:
        if not final_record:
            raise ValidationError("FinalAuditRecord is required to generate inspection report")

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()

        # Custom Typography Styles
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=20,
            textColor=colors.HexColor('#0f172a'),
            alignment=1, # Center
        )
        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=13,
            textColor=colors.HexColor('#475569'),
            alignment=1,
        )
        section_heading = ParagraphStyle(
            'SectionHeading',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=15,
            textColor=colors.HexColor('#1e3a8a'),
            spaceBefore=12,
            spaceAfter=6,
        )
        body_style = ParagraphStyle(
            'ReportBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#1e293b'),
        )
        body_bold = ParagraphStyle(
            'ReportBodyBold',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#0f172a'),
        )
        table_cell_style = ParagraphStyle(
            'TableCell',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#1e293b'),
        )
        table_cell_bold = ParagraphStyle(
            'TableCellBold',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#0f172a'),
        )
        callout_style = ParagraphStyle(
            'CalloutText',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            textColor=colors.HexColor('#0f172a'),
        )

        story = []

        # 1. Header Banner
        story.append(Paragraph("LEGAL METROLOGY (PACKAGED COMMODITIES) RULES, 2011", subtitle_style))
        story.append(Paragraph("OFFICIAL REGULATORY INSPECTION & COMPLIANCE REPORT", title_style))
        story.append(Spacer(1, 4))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e3a8a'), spaceAfter=10))

        # 2. Inspection Context Snapshot
        ctx = final_record.inspection_context_snapshot or {}
        overview_data = [
            [
                Paragraph("<b>Inspection ID:</b>", table_cell_style),
                Paragraph(final_record.inspection_id, table_cell_style),
                Paragraph("<b>Case Number:</b>", table_cell_style),
                Paragraph(ctx.get("case_number", "N/A"), table_cell_style),
            ],
            [
                Paragraph("<b>Product Name:</b>", table_cell_style),
                Paragraph(ctx.get("product_name", "N/A"), table_cell_style),
                Paragraph("<b>Origin Status:</b>", table_cell_style),
                Paragraph(ctx.get("origin_status", "UNKNOWN"), table_cell_style),
            ],
            [
                Paragraph("<b>Rule-Set ID / Version:</b>", table_cell_style),
                Paragraph(f"{final_record.rule_set_id} ({final_record.rule_set_version})", table_cell_style),
                Paragraph("<b>Evaluation Version:</b>", table_cell_style),
                Paragraph(final_record.evaluation_version, table_cell_style),
            ],
            [
                Paragraph("<b>Finalized Timestamp:</b>", table_cell_style),
                Paragraph(final_record.finalized_at.strftime("%Y-%m-%d %H:%M:%S UTC") if final_record.finalized_at else "N/A", table_cell_style),
                Paragraph("<b>Final Record ID:</b>", table_cell_style),
                Paragraph(final_record.id, table_cell_style),
            ],
        ]
        t_overview = Table(overview_data, colWidths=[1.4*inch, 2.3*inch, 1.4*inch, 2.3*inch])
        t_overview.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(t_overview)
        story.append(Spacer(1, 8))

        # 3. Master Final Legal Determination Banner
        is_compliant = final_record.final_decision in ("COMPLIANT", "PASS")
        dec_bg = colors.HexColor('#ecfdf5') if is_compliant else colors.HexColor('#fef2f2')
        dec_border = colors.HexColor('#10b981') if is_compliant else colors.HexColor('#ef4444')
        dec_text_color = colors.HexColor('#065f46') if is_compliant else colors.HexColor('#991b1b')

        decision_banner_data = [
            [
                Paragraph(f"<b>FINAL ADJUDICATED DETERMINATION:</b> <font color='{dec_text_color.hexval()}'><b>{final_record.final_decision}</b></font>", ParagraphStyle('DecHeader', parent=body_bold, fontSize=11, leading=14)),
            ],
            [
                Paragraph(f"<b>Adjudication Rationale:</b> {final_record.final_rationale}", callout_style),
            ],
        ]
        t_decision = Table(decision_banner_data, colWidths=[7.4*inch])
        t_decision.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), dec_bg),
            ('BOX', (0,0), (-1,-1), 1, dec_border),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(t_decision)
        story.append(Spacer(1, 8))

        # 4. Evidence Integrity Inventory
        story.append(Paragraph("1. Evidence Inventory & Cryptographic Integrity Hashes", section_heading))
        ev_data = [
            [
                Paragraph("<b>Evidence ID</b>", table_cell_bold),
                Paragraph("<b>Filename / View</b>", table_cell_bold),
                Paragraph("<b>Size</b>", table_cell_bold),
                Paragraph("<b>SHA-256 Integrity Hash (Change Detection)</b>", table_cell_bold),
            ]
        ]
        evidence_list = final_record.evidence_snapshot or []
        for ev in evidence_list:
            ev_data.append([
                Paragraph(ev.get("id", "N/A"), table_cell_style),
                Paragraph(f"{ev.get('original_filename', 'N/A')}<br/>({ev.get('evidence_type', 'PRIMARY')})", table_cell_style),
                Paragraph(f"{ev.get('file_size_bytes', 0) // 1024} KB", table_cell_style),
                Paragraph(f"<font name='Courier' size=7>{ev.get('sha256_hash', 'N/A')}</font>", table_cell_style),
            ])
        t_ev = Table(ev_data, colWidths=[1.1*inch, 1.8*inch, 0.7*inch, 3.8*inch])
        t_ev.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(t_ev)
        story.append(Spacer(1, 8))

        # 5. Applicability Assessment
        story.append(Paragraph("2. Mandatory Requirement Applicability", section_heading))
        app_data = [
            [
                Paragraph("<b>Requirement</b>", table_cell_bold),
                Paragraph("<b>Applicability Status</b>", table_cell_bold),
                Paragraph("<b>Statutory Citation</b>", table_cell_bold),
                Paragraph("<b>Legal Basis / Rule Logic</b>", table_cell_bold),
            ]
        ]
        app_list = final_record.applicability_snapshot or []
        for app_item in app_list:
            app_data.append([
                Paragraph(app_item.get("requirement_name", "N/A"), table_cell_bold),
                Paragraph(app_item.get("status", "N/A"), table_cell_style),
                Paragraph(app_item.get("rule_citation", "N/A"), table_cell_style),
                Paragraph(app_item.get("basis", "N/A"), table_cell_style),
            ])
        t_app = Table(app_data, colWidths=[1.6*inch, 1.3*inch, 1.3*inch, 3.2*inch])
        t_app.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(t_app)
        story.append(Spacer(1, 8))

        # 6. Compliance Evaluation & Reviewer Adjudication (Separation Guaranteed)
        story.append(Paragraph("3. Compliance Evaluation vs Reviewer Adjudication", section_heading))
        comp_data = [
            [
                Paragraph("<b>Requirement</b>", table_cell_bold),
                Paragraph("<b>Automated System Finding</b>", table_cell_bold),
                Paragraph("<b>Reviewer Action</b>", table_cell_bold),
                Paragraph("<b>Final Adjudicated Result</b>", table_cell_bold),
                Paragraph("<b>Reviewer Rationale / Override Reason</b>", table_cell_bold),
            ]
        ]
        findings_map = {f.get("requirement_name"): f for f in (final_record.compliance_findings_snapshot or [])}
        decisions_map = {d.get("requirement_name"): d for d in (final_record.reviewer_decisions_snapshot or [])}

        all_reqs = sorted(list(set(findings_map.keys()) | set(decisions_map.keys())))
        for req in all_reqs:
            f = findings_map.get(req, {})
            d = decisions_map.get(req, {})

            sys_res = f.get("result", "NOT_EVALUATED")
            rev_det = d.get("determination", "CONFIRMED")
            adj_res = d.get("adjudicated_result", sys_res)
            is_over = d.get("is_override", False)
            rat = d.get("rationale", f.get("reason", "No recorded rationale"))

            action_text = f"<b>OVERRIDE</b>" if is_over else f"{rev_det}"

            comp_data.append([
                Paragraph(req, table_cell_bold),
                Paragraph(f"<font color='{colors.HexColor('#475569').hexval()}'>{sys_res}</font>", table_cell_style),
                Paragraph(action_text, table_cell_style),
                Paragraph(f"<b>{adj_res}</b>", table_cell_style),
                Paragraph(rat, table_cell_style),
            ])

        t_comp = Table(comp_data, colWidths=[1.4*inch, 1.4*inch, 1.1*inch, 1.2*inch, 2.3*inch])
        t_comp.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(t_comp)
        story.append(Spacer(1, 10))

        # 7. Legal Metrology Officer Sign-Off & Audit Certification
        sign_off_data = [
            [
                Paragraph("<b>OFFICIAL REGULATORY CERTIFICATION</b>", table_cell_bold),
                Paragraph("<b>IMMUTABLE ARCHIVAL SEAL</b>", table_cell_bold),
            ],
            [
                Paragraph(
                    "This report is generated from the immutable Legal Metrology FinalAuditRecord snapshot. "
                    "All automated AI extractions and deterministic rules served strictly as regulatory assistance. "
                    "The final legal determination herein represents the authoritative decision of the authorized Reviewer.",
                    table_cell_style,
                ),
                Paragraph(
                    f"<b>Finalized By User ID:</b> {final_record.finalized_by_id}<br/>"
                    f"<b>Archival Record ID:</b> {final_record.id}<br/>"
                    f"<b>Audit State:</b> FINALIZED & READ_ONLY",
                    table_cell_style,
                ),
            ],
        ]
        t_sign = Table(sign_off_data, colWidths=[4.2*inch, 3.2*inch])
        t_sign.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f1f5f9')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#94a3b8')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(KeepTogether([t_sign]))

        doc.build(story)
        return buffer.getvalue()
