import io
from datetime import datetime
from typing import Dict, Any, List

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

class PDFOfficerBriefCompiler:
    """
    Module 8: Officer Dashboard & Reporting.
    Compiles an explainable, court-admissible PDF audit report with statutory citations,
    shortfall calculations, forensics findings, and chronological proof traces.
    """
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._init_custom_styles()

    def _init_custom_styles(self):
        self.title_style = ParagraphStyle(
            'GovTitle',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#0f172a')
        )
        self.subtitle_style = ParagraphStyle(
            'GovSubtitle',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#475569')
        )
        self.heading_style = ParagraphStyle(
            'SectionHeading',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=15,
            textColor=colors.HexColor('#1e293b'),
            spaceBefore=8,
            spaceAfter=4
        )
        self.body_style = ParagraphStyle(
            'TableBody',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#1e293b')
        )
        self.citation_style = ParagraphStyle(
            'CitationText',
            parent=self.styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=7,
            leading=9,
            textColor=colors.HexColor('#4338ca')
        )

    def compile_pdf_bytes(self, brief: Dict[str, Any]) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        elements = []

        # 1. Header Banner
        elements.append(Paragraph("ALL INDIA COUNCIL FOR TECHNICAL EDUCATION", self.title_style))
        elements.append(Paragraph("STATUTORY SCRUTINY COMMITTEE · DECISION-SUPPORT AUDIT BRIEF", self.subtitle_style))
        elements.append(Spacer(1, 4))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#312e81'), spaceAfter=8))

        # 2. Institution Meta & Executive Verdict
        verdict = brief.get("executive_verdict", "PENDING")
        verdict_color = colors.HexColor('#059669') if "APPROVED" in verdict else colors.HexColor('#dc2626')
        
        meta_table_data = [
            [
                Paragraph(f"<b>Application ID:</b> {brief.get('application_id')}", self.body_style),
                Paragraph(f"<b>Audit Date:</b> {brief.get('generated_at')}", self.body_style)
            ],
            [
                Paragraph(f"<b>Institution Name:</b> {brief.get('institution_name')}", self.body_style),
                Paragraph(f"<b>Executive Verdict:</b> <font color='{verdict_color.hexval()}'><b>{brief.get('verdict_badge')}</b></font>", self.body_style)
            ]
        ]
        meta_table = Table(meta_table_data, colWidths=[270, 270])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 10))

        # 3. Metrics Summary Table
        metrics = brief.get("summary_metrics", {})
        metrics_data = [
            ["Rules Evaluated", "Compliant Norms", "Deficiencies", "Timeline Paradoxes", "Forensics Flags", "Authority Mismatches"],
            [
                str(metrics.get("rules_evaluated", 0)),
                str(metrics.get("compliant_rules", 0)),
                str(metrics.get("deficient_rules", 0)),
                str(metrics.get("timeline_anomalies", 0)),
                str(metrics.get("forensic_tampering_flags", 0)),
                str(metrics.get("authority_mismatches", 0))
            ]
        ]
        metrics_table = Table(metrics_data, colWidths=[90]*6)
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e1b4b')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 7),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('FONTNAME', (0,1), (-1,1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,1), (-1,1), 9),
        ]))
        elements.append(metrics_table)
        elements.append(Spacer(1, 12))

        # 4. Deterministic Compliance Ledger
        elements.append(Paragraph("1. Deterministic Regulatory Compliance Ledger", self.heading_style))
        comp_data = [["Category / Rule", "Status", "Mandated Norm", "Institutional Claim", "Shortfall", "Statutory Citation"]]
        
        for item in brief.get("compliance_ledger", []):
            st = item.get("status", "")
            st_color = "#059669" if st == "COMPLIANT" else "#dc2626"
            comp_data.append([
                Paragraph(f"<b>{item.get('title')}</b>", self.body_style),
                Paragraph(f"<font color='{st_color}'><b>{st}</b></font>", self.body_style),
                Paragraph(str(item.get("required")), self.body_style),
                Paragraph(str(item.get("actual")), self.body_style),
                Paragraph(str(item.get("shortfall")), self.body_style),
                Paragraph(item.get("citation", ""), self.citation_style)
            ])

        comp_table = Table(comp_data, colWidths=[120, 65, 80, 85, 70, 120])
        comp_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 7.5),
            ('PADDING', (0,0), (-1,-1), 4),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        elements.append(comp_table)
        elements.append(Spacer(1, 12))

        # 5. Timeline Impossibility Paradoxes
        timeline_paradoxes = brief.get("timeline_paradoxes", [])
        if timeline_paradoxes:
            elements.append(Paragraph("2. Timeline Impossibility Traces (Allen's Interval Algebra)", self.heading_style))
            for p in timeline_paradoxes:
                trace_lines = "<br/>".join([f"• {t}" for t in p.get("proof_trace", [])])
                p_text = f"<b>Anomaly:</b> {p.get('event_a')} vs {p.get('event_b')} [{p.get('relation')}]<br/>" \
                         f"<b>Explanation:</b> {p.get('explanation')}<br/>" \
                         f"<b>Statutory Citation:</b> {p.get('citation')}<br/>" \
                         f"<b>Proof Trace:</b><br/>{trace_lines}"
                t_box = Table([[Paragraph(p_text, self.body_style)]], colWidths=[540])
                t_box.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fef2f2')),
                    ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#fca5a5')),
                    ('PADDING', (0,0), (-1,-1), 6),
                ]))
                elements.append(t_box)
                elements.append(Spacer(1, 5))
            elements.append(Spacer(1, 8))

        # 6. Document Forensics & ELA Splicing
        forensics = brief.get("forensics_ledger", [])
        if forensics:
            elements.append(Paragraph("3. Document Forensics & Pixel Manipulation Flags", self.heading_style))
            f_data = [["Document", "Verdict", "Fraud Score", "Tampering Findings"]]
            for f in forensics:
                findings_text = "<br/>".join([f"• <b>{item.get('title')}</b>: {item.get('desc')}" for item in f.get("findings", [])])
                f_data.append([
                    Paragraph(f.get("file_name", ""), self.body_style),
                    Paragraph(f"<font color='#dc2626'><b>{f.get('verdict')}</b></font>", self.body_style),
                    Paragraph(f"{int(float(f.get('fraud_score', 0))*100)}%", self.body_style),
                    Paragraph(findings_text, self.body_style)
                ])
            f_table = Table(f_data, colWidths=[120, 65, 55, 300])
            f_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
                ('PADDING', (0,0), (-1,-1), 4),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ]))
            elements.append(f_table)
            elements.append(Spacer(1, 12))

        # 7. Authority Verification Status
        elements.append(Paragraph("4. Issuing Authority Registry Cross-Checks", self.heading_style))
        auth_data = [["Authority", "Identifier", "Status", "Registry Discrepancy Note"]]
        for a in brief.get("authority_verification", []):
            st = a.get("status", "")
            st_color = "#059669" if st == "VERIFIED" else "#dc2626"
            auth_data.append([
                Paragraph(a.get("authority", ""), self.body_style),
                Paragraph(a.get("identifier", ""), self.body_style),
                Paragraph(f"<font color='{st_color}'><b>{st}</b></font>", self.body_style),
                Paragraph(a.get("details", ""), self.body_style)
            ])
        auth_table = Table(auth_data, colWidths=[140, 110, 80, 210])
        auth_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('PADDING', (0,0), (-1,-1), 4),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        elements.append(auth_table)
        elements.append(Spacer(1, 15))

        # 8. Digital Attestation Footer
        footer_text = f"Digitally Attested by Sakshya AICTE Regulatory Intelligence Engine · " \
                      f"Hash: {datetime.utcnow().strftime('%Y%m%d%H%M%S')}-AICTE-VERIFIED · " \
                      f"Final approval decisions remain exclusively with authorized AICTE Scrutiny Officers."
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#94a3b8'), spaceAfter=5))
        elements.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=self.styles['Normal'], fontSize=6.5, textColor=colors.HexColor('#64748b'), alignment=TA_CENTER)))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
