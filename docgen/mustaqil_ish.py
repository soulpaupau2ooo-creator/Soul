"""
Dedicated Microsoft Word (.docx) Document Generator for Uzbek Academic Coursework Papers (Mustaqil Ish).

Complies with official Uzbekistan Higher Education Standards:
- Paper: A4 (21.0 cm x 29.7 cm)
- Margins: Left 3.0 cm, Right 1.5 cm, Top 2.0 cm, Bottom 2.0 cm
- Typography: Times New Roman 14 pt, 1.5 line spacing, 1.25 cm first-line indent, Justified
- Title Page (Titul varaq) with complete metadata
- Word native auto-updating Table of Contents (TOC) XML field
- First-page suppressed footer page numbers
- Structured sections: Kirish, Asosiy qism (Headings 1 & 2), Xulosa, Adabiyotlar ro'yxati
"""

from __future__ import annotations

import io
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import docx
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Inches, Pt, RGBColor

# ==============================================================================
# ⚙️ STANDARD OTM CONFIGURATION CONSTANTS (Customizable per University)
# ==============================================================================
DEFAULT_PAGE_CONFIG = {
    "page_width": Cm(21.0),
    "page_height": Cm(29.7),
    "margin_left": Cm(3.0),
    "margin_right": Cm(1.5),
    "margin_top": Cm(2.0),
    "margin_bottom": Cm(2.0),
    "font_name": "Times New Roman",
    "font_size_body": Pt(14),
    "font_size_title": Pt(18),
    "font_size_heading1": Pt(15),
    "font_size_heading2": Pt(14),
    "line_spacing": 1.5,
    "first_line_indent": Cm(1.25),
    "city": "Toshkent",
    "year": str(datetime.now().year),
}


@dataclass
class TitlePageInfo:
    """Complete metadata for the academic coursework paper title page."""
    university: str
    faculty: str
    department: str
    subject: str
    topic: str
    student_name: str
    group_name: str
    teacher_name: Optional[str] = None
    city: str = "Toshkent"
    year: str = str(datetime.now().year)

    def validate(self) -> None:
        """Validate that all mandatory fields are present and non-empty."""
        missing = []
        if not self.university or not self.university.strip():
            missing.append("Universitet nomi")
        if not self.subject or not self.subject.strip():
            missing.append("Fan nomi")
        if not self.topic or not self.topic.strip():
            missing.append("Mavzu")
        if not self.student_name or not self.student_name.strip():
            missing.append("Talaba F.I.Sh.")
        if not self.group_name or not self.group_name.strip():
            missing.append("Guruh")

        if missing:
            raise ValueError(f"Titul varag'i uchun quyidagi ma'lumotlar to'ldirilmagan: {', '.join(missing)}")


@dataclass
class SectionItem:
    """Individual chapter, subsection or content block."""
    title: str
    paragraphs: List[str]
    is_heading1: bool = True
    page_break_before: bool = False


@dataclass
class MustaqilIshDocument:
    """Full academic coursework structure."""
    title_info: TitlePageInfo
    sections: List[SectionItem]
    references: List[str] = field(default_factory=list)


# ==============================================================================
# 🏛️ DOCX GENERATION ENGINE
# ==============================================================================
class MustaqilIshDocxBuilder:
    """Builds university-standard Microsoft Word documents."""

    def __init__(self, custom_config: Optional[Dict] = None):
        self.config = dict(DEFAULT_PAGE_CONFIG)
        if custom_config:
            self.config.update(custom_config)

    def _setup_page_geometry(self, section: docx.section.Section) -> None:
        """Apply official margins and paper dimensions."""
        section.page_width = self.config["page_width"]
        section.page_height = self.config["page_height"]
        section.left_margin = self.config["margin_left"]
        section.right_margin = self.config["margin_right"]
        section.top_margin = self.config["margin_top"]
        section.bottom_margin = self.config["margin_bottom"]
        section.different_first_page_header_footer = True

    def _apply_body_formatting(self, paragraph: docx.text.paragraph.Paragraph) -> None:
        """Apply 1.5 line spacing, 1.25cm first line indent, justified alignment."""
        p_format = paragraph.paragraph_format
        p_format.line_spacing = self.config["line_spacing"]
        p_format.first_line_indent = self.config["first_line_indent"]
        p_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_format.space_before = Pt(0)
        p_format.space_after = Pt(0)

        for run in paragraph.runs:
            run.font.name = self.config["font_name"]
            run.font.size = self.config["font_size_body"]
            run.font.color.rgb = RGBColor(0, 0, 0)

    def _add_page_number_to_footer(self, section: docx.section.Section) -> None:
        """Insert native Word page number field into the footer."""
        footer = section.footer
        p = footer.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_format = p.paragraph_format
        p_format.space_before = Pt(0)
        p_format.space_after = Pt(0)

        run = p.add_run()
        run.font.name = self.config["font_name"]
        run.font.size = Pt(11)

        # XML field for current page number
        fldSimple = OxmlElement('w:fldSimple')
        fldSimple.set(qn('w:instr'), 'PAGE')
        p._p.append(fldSimple)

    def _insert_toc_field(self, doc: docx.Document) -> None:
        """Insert native auto-updating Word Table of Contents field code."""
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(6)

        # Insert w:fldSimple for TOC
        p_elem = p._p
        fldSimple = parse_xml(r'<w:fldSimple %s w:instr="TOC \o &quot;1-3&quot; \h \z \u"/>' % nsdecls('w'))
        p_elem.append(fldSimple)

    def build_title_page(self, doc: docx.Document, info: TitlePageInfo) -> None:
        """Render the complete academic title page (Titul varaq)."""
        info.validate()

        # 1. Ministry and University Header (Top centered)
        p_uni = doc.add_paragraph()
        p_uni.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_uni.paragraph_format.space_before = Pt(0)
        p_uni.paragraph_format.space_after = Pt(4)
        run_uni = p_uni.add_run("O'ZBEKISTON RESPUBLIKASI OLIY TA'LIM, FAN VA INNOVATSIYALAR VAZIRLIGI\n\n" + info.university.upper())
        run_uni.font.name = self.config["font_name"]
        run_uni.font.size = Pt(12)
        run_uni.font.bold = True

        if info.faculty:
            p_fac = doc.add_paragraph()
            p_fac.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_fac.paragraph_format.space_before = Pt(0)
            p_fac.paragraph_format.space_after = Pt(2)
            run_fac = p_fac.add_run(info.faculty + "\n" + (info.department or ""))
            run_fac.font.name = self.config["font_name"]
            run_fac.font.size = Pt(13)

        # Vertical spacing
        for _ in range(4):
            p_space = doc.add_paragraph()
            p_space.paragraph_format.space_before = Pt(0)
            p_space.paragraph_format.space_after = Pt(0)

        # 2. MUSTAQIL ISH (Center)
        p_title = doc.add_paragraph()
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_title.paragraph_format.space_before = Pt(12)
        p_title.paragraph_format.space_after = Pt(6)
        run_title = p_title.add_run("MUSTAQIL ISH")
        run_title.font.name = self.config["font_name"]
        run_title.font.size = self.config["font_size_title"]
        run_title.font.bold = True

        # Subject and Topic
        p_topic = doc.add_paragraph()
        p_topic.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_topic.paragraph_format.space_before = Pt(6)
        p_topic.paragraph_format.space_after = Pt(12)

        run_subj = p_topic.add_run(f"Fan: {info.subject}\n\n")
        run_subj.font.name = self.config["font_name"]
        run_subj.font.size = Pt(14)

        run_top = p_topic.add_run(f"Mavzu: «{info.topic}»")
        run_top.font.name = self.config["font_name"]
        run_top.font.size = Pt(15)
        run_top.font.bold = True

        # Vertical spacing
        for _ in range(4):
            p_space = doc.add_paragraph()
            p_space.paragraph_format.space_before = Pt(0)
            p_space.paragraph_format.space_after = Pt(0)

        # 3. Student and Teacher Info (Right aligned block)
        p_info = doc.add_paragraph()
        p_info.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_info.paragraph_format.space_before = Pt(12)
        p_info.paragraph_format.space_after = Pt(6)

        info_text = (
            f"Bajardi: {info.group_name}-guruh talabasi\n"
            f"{info.student_name}\n\n"
        )
        if info.teacher_name:
            info_text += f"Qabul qildi: {info.teacher_name}\n"

        run_meta = p_info.add_run(info_text)
        run_meta.font.name = self.config["font_name"]
        run_meta.font.size = Pt(13)

        # Vertical spacing to bottom
        for _ in range(4):
            p_space = doc.add_paragraph()
            p_space.paragraph_format.space_before = Pt(0)
            p_space.paragraph_format.space_after = Pt(0)

        # 4. City and Year (Bottom centered)
        p_bottom = doc.add_paragraph()
        p_bottom.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_bottom.paragraph_format.space_before = Pt(12)
        p_bottom.paragraph_format.space_after = Pt(0)
        run_bot = p_bottom.add_run(f"{info.city} – {info.year}")
        run_bot.font.name = self.config["font_name"]
        run_bot.font.size = Pt(13)

        # Page break after Title Page
        doc.add_page_break()

    def generate_docx(self, doc_data: MustaqilIshDocument) -> bytes:
        """
        Generate complete, university-compliant .docx file as in-memory bytes.
        """
        doc = docx.Document()
        section = doc.sections[0]
        self._setup_page_geometry(section)
        self._add_page_number_to_footer(section)

        # 1. Title Page
        self.build_title_page(doc, doc_data.title_info)

        # 2. Table of Contents Page (Mundarija)
        p_toc = doc.add_paragraph()
        p_toc.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_toc.paragraph_format.space_before = Pt(6)
        p_toc.paragraph_format.space_after = Pt(12)
        run_toc = p_toc.add_run("MUNDARIJA")
        run_toc.font.name = self.config["font_name"]
        run_toc.font.size = self.config["font_size_heading1"]
        run_toc.font.bold = True

        self._insert_toc_field(doc)
        doc.add_page_break()

        # 3. Content Sections (Kirish, Asosiy Qism, Xulosa)
        for sec in doc_data.sections:
            if sec.page_break_before:
                doc.add_page_break()

            # Heading
            h_p = doc.add_paragraph()
            h_format = h_p.paragraph_format
            h_format.space_before = Pt(12)
            h_format.space_after = Pt(6)

            if sec.is_heading1:
                h_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                h_run = h_p.add_run(sec.title.upper())
                h_run.font.size = self.config["font_size_heading1"]
                h_run.font.bold = True
            else:
                h_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                h_format.first_line_indent = self.config["first_line_indent"]
                h_run = h_p.add_run(sec.title)
                h_run.font.size = self.config["font_size_heading2"]
                h_run.font.bold = True

            h_run.font.name = self.config["font_name"]
            h_run.font.color.rgb = RGBColor(0, 0, 0)

            # Paragraphs
            for text_para in sec.paragraphs:
                text_para = text_para.strip()
                if not text_para:
                    continue
                body_p = doc.add_paragraph()
                r = body_p.add_run(text_para)
                r.font.name = self.config["font_name"]
                r.font.size = self.config["font_size_body"]
                self._apply_body_formatting(body_p)

        # 4. References Page (Foydalanilgan adabiyotlar)
        if doc_data.references:
            doc.add_page_break()
            p_ref = doc.add_paragraph()
            p_ref.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_ref.paragraph_format.space_before = Pt(12)
            p_ref.paragraph_format.space_after = Pt(12)
            run_ref = p_ref.add_run("FOYDALANILGAN ADABIYOTLAR RO'YXATI")
            run_ref.font.name = self.config["font_name"]
            run_ref.font.size = self.config["font_size_heading1"]
            run_ref.font.bold = True

            for idx, ref_item in enumerate(doc_data.references, 1):
                p_item = doc.add_paragraph()
                p_item.paragraph_format.line_spacing = self.config["line_spacing"]
                p_item.paragraph_format.first_line_indent = self.config["first_line_indent"]
                p_item.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p_item.paragraph_format.space_before = Pt(0)
                p_item.paragraph_format.space_after = Pt(3)

                clean_ref = re.sub(r"^\d+[\.\)]\s*", "", ref_item.strip())
                r = p_item.add_run(f"{idx}. {clean_ref}")
                r.font.name = self.config["font_name"]
                r.font.size = self.config["font_size_body"]

        # 5. Export to binary stream
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.read()
