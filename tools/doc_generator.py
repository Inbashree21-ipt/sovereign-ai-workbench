"""
Document Generation Tool (Bridge for Member 5's Deliverables)
Produces actual enterprise files (Word .docx and Excel .xlsx) instead of plain chat text.
Uses:
- Pure-Python OpenXML packager for .docx (100% reliable, zero external C-dependencies)
- openpyxl for .xlsx spreadsheets
"""

import os
import zipfile
from xml.sax.saxutils import escape
from pathlib import Path
from typing import Dict, Any, List, Optional
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

from tools.base import BaseTool, ToolResult
from config import DELIVERABLES_DIR


def create_docx_file(output_path: Path, title: str, sections: List[Dict[str, str]]):
    """
    Creates a valid Microsoft Word (.docx) file using standard OpenXML and zipfile.
    sections is a list of {"heading": str, "body": str}.
    """
    body_xml_parts = []

    # Title paragraph
    body_xml_parts.append(
        f'<w:p>'
        f'  <w:pPr><w:jc w:val="center"/><w:spacing w:after="300"/></w:pPr>'
        f'  <w:r>'
        f'    <w:rPr><w:b/><w:sz w:val="48"/><w:color w:val="1F497D"/></w:rPr>'
        f'    <w:t>{escape(title)}</w:t>'
        f'  </w:r>'
        f'</w:p>'
    )

    # Sub-header / metadata
    body_xml_parts.append(
        f'<w:p>'
        f'  <w:pPr><w:jc w:val="center"/><w:spacing w:after="400"/></w:pPr>'
        f'  <w:r>'
        f'    <w:rPr><w:i/><w:sz w:val="20"/><w:color w:val="595959"/></w:rPr>'
        f'    <w:t>Sovereign On-Premise AI Workbench — Verified Deliverable</w:t>'
        f'  </w:r>'
        f'</w:p>'
    )

    # Sections
    for sec in sections:
        heading = sec.get("heading", "")
        body = sec.get("body", "")

        if heading:
            body_xml_parts.append(
                f'<w:p>'
                f'  <w:pPr><w:spacing w:before="240" w:after="120"/></w:pPr>'
                f'  <w:r>'
                f'    <w:rPr><w:b/><w:sz w:val="28"/><w:color w:val="2E74B5"/></w:rPr>'
                f'    <w:t>{escape(heading)}</w:t>'
                f'  </w:r>'
                f'</w:p>'
            )

        # Paragraphs in body
        paragraphs = [p.strip() for p in body.split("\n") if p.strip()]
        for p_text in paragraphs:
            body_xml_parts.append(
                f'<w:p>'
                f'  <w:pPr><w:spacing w:after="140"/><w:line w:line="276" w:lineRule="auto"/></w:pPr>'
                f'  <w:r>'
                f'    <w:rPr><w:sz w:val="22"/><w:color w:val="333333"/></w:rPr>'
                f'    <w:t>{escape(p_text)}</w:t>'
                f'  </w:r>'
                f'</w:p>'
            )

    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">\n'
        '  <w:body>\n'
        + "\n".join(body_xml_parts) +
        '\n    <w:sectPr>\n'
        '      <w:pgSz w:w="12240" w:h="15840"/>\n'
        '      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/>\n'
        '    </w:sectPr>\n'
        '  </w:body>\n'
        '</w:document>'
    )

    content_types_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
        '  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
        '  <Default Extension="xml" ContentType="application/xml"/>\n'
        '  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>\n'
        '</Types>'
    )

    rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        '  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>\n'
        '</Relationships>'
    )

    # Write ZIP
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types_xml)
        zf.writestr("_rels/.rels", rels_xml)
        zf.writestr("word/document.xml", document_xml)


class GenerateDocumentTool(BaseTool):
    name = "generate_deliverable"
    description = (
        "Generates actual office deliverable files (.docx Word approval notes or .xlsx Excel workbooks) "
        "and saves them in the confidential deliverables folder."
    )
    parameters = {
        "type": "object",
        "properties": {
            "format": {
                "type": "string",
                "enum": ["docx", "xlsx"],
                "description": "Output format: 'docx' for approval notes / reports, or 'xlsx' for spreadsheet deliverables.",
            },
            "filename": {
                "type": "string",
                "description": "Base filename (e.g. 'Approval_Note_Pipeline_Inspection.docx').",
            },
            "title": {
                "type": "string",
                "description": "Document title or heading.",
            },
            "sections": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "heading": {"type": "string"},
                        "body": {"type": "string"},
                    },
                    "required": ["heading", "body"],
                },
                "description": "List of sections for Word .docx output.",
            },
            "table_data": {
                "type": "array",
                "items": {"type": "object"},
                "description": "List of row dictionaries for Excel .xlsx output.",
            },
        },
        "required": ["format", "filename", "title"],
    }

    def run(self, **kwargs) -> ToolResult:
        doc_format = kwargs.get("format", "docx").lower()
        filename = kwargs.get("filename", "deliverable")
        title = kwargs.get("title", "Industrial Deliverable")
        sections = kwargs.get("sections", [])
        table_data = kwargs.get("table_data", [])

        if not filename.endswith(f".{doc_format}"):
            filename = f"{filename}.{doc_format}"

        output_path = DELIVERABLES_DIR / filename

        try:
            if doc_format == "docx":
                # Generate Word document
                create_docx_file(output_path, title, sections)
                size = output_path.stat().st_size
                return ToolResult(
                    success=True,
                    output=(
                        f"Successfully generated Word deliverable: '{filename}' ({size:,} bytes).\n"
                        f"Location: workspace/deliverables/{filename}\n"
                        f"Sections included: {len(sections)}."
                    ),
                    data={"filename": filename, "format": "docx", "path": str(output_path), "size": size},
                )

            elif doc_format == "xlsx":
                # Generate Excel workbook
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.title = "Summary"

                # Title
                ws.append([title])
                ws.cell(row=1, column=1).font = Font(size=16, bold=True, color="1F497D")

                # Table headers and rows
                if table_data and isinstance(table_data, list):
                    headers = list(table_data[0].keys())
                    ws.append([])  # Blank row
                    ws.append(headers)
                    header_row_idx = 3

                    # Style headers
                    header_fill = PatternFill(start_color="2E74B5", end_color="2E74B5", fill_type="solid")
                    header_font = Font(color="FFFFFF", bold=True)
                    for col_idx in range(1, len(headers) + 1):
                        cell = ws.cell(row=header_row_idx, column=col_idx)
                        cell.fill = header_fill
                        cell.font = header_font
                        cell.alignment = Alignment(horizontal="center")

                    # Rows
                    for row_dict in table_data:
                        ws.append([row_dict.get(h, "") for h in headers])

                wb.save(str(output_path))
                size = output_path.stat().st_size
                return ToolResult(
                    success=True,
                    output=(
                        f"Successfully generated Excel deliverable: '{filename}' ({size:,} bytes).\n"
                        f"Location: workspace/deliverables/{filename}"
                    ),
                    data={"filename": filename, "format": "xlsx", "path": str(output_path), "size": size},
                )
            else:
                return ToolResult(success=False, output="", error=f"Unsupported format '{doc_format}'.")

        except Exception as e:
            return ToolResult(success=False, output="", error=f"Deliverable generation failed: {str(e)}")
