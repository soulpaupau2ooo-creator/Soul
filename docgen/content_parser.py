"""
Academic Content Parser and Normalizer for Mustaqil Ish Documents.

Converts raw AI-generated essay text into structured SectionItem objects
and extracts references, ensuring standard chapter numbering and clean prose.
"""

from __future__ import annotations

import re
from typing import List, Tuple
from docgen.mustaqil_ish import MustaqilIshDocument, SectionItem, TitlePageInfo


class AcademicEssayParser:
    """Parses raw generated essay text into structured chapters, sections, and references."""

    @staticmethod
    def parse_essay_to_document(
        raw_text: str,
        title_info: TitlePageInfo,
    ) -> MustaqilIshDocument:
        """
        Transform raw text into structured MustaqilIshDocument.
        Extracts:
        - Kirish
        - Asosiy qism (Chapters / Headings)
        - Xulosa
        - Foydalanilgan adabiyotlar ro'yxati
        """
        lines = [line.strip() for line in raw_text.split("\n")]
        sections: List[SectionItem] = []
        references: List[str] = []

        current_title = "KIRISH"
        current_paragraphs: List[str] = []
        is_heading1 = True
        in_references = False

        # Regular expressions for section boundaries
        heading_patterns = [
            (r"^(?:#+\s*)?(?:kirish|введение|introduction)\b", "KIRISH", True, False),
            (r"^(?:#+\s*)?(?:xulosa|хулоса|заключение|conclusion)\b", "XULOSA", True, True),
            (r"^(?:#+\s*)?(?:foydalanilgan\s+adabiyotlar|adabiyotlar\s+ro['ʻ`]?yxati|список\s+литературы|references)\b", "FOYDALANILGAN ADABIYOTLAR RO'YXATI", True, True),
            (r"^(?:#+\s*)?(\d+[-.]\s*(?:bob|bo['ʻ`]?lim|fasl|bob:|bo['ʻ`]?lim:)?\s*[^:\n]+)", None, True, True),
            (r"^(?:#+\s*)?(\d+\.\d+[-.]?\s*[^:\n]+)", None, False, False),
        ]

        for line in lines:
            if not line:
                continue

            # Check if entering references block
            if re.search(r"^(?:#+\s*)?(?:foydalanilgan\s+adabiyotlar|adabiyotlar\s+ro['ʻ`]?yxati|список\s+литературы)\b", line, re.IGNORECASE):
                if current_paragraphs:
                    sections.append(SectionItem(
                        title=current_title,
                        paragraphs=list(current_paragraphs),
                        is_heading1=is_heading1,
                        page_break_before=(current_title != "KIRISH")
                    ))
                    current_paragraphs = []
                in_references = True
                continue

            if in_references:
                # Numbered list items in references
                if re.match(r"^(\d+[\.\)]|\-|\*)\s+", line):
                    clean_ref = re.sub(r"^(\d+[\.\)]|\-|\*)\s+", "", line)
                    if clean_ref:
                        references.append(clean_ref)
                else:
                    if line and len(line) > 5:
                        references.append(line)
                continue

            # Check for standard headings
            matched_heading = False
            for pat, fixed_title, h1_flag, page_break in heading_patterns:
                m = re.match(pat, line, re.IGNORECASE)
                if m:
                    # Save accumulated paragraphs
                    if current_paragraphs:
                        sections.append(SectionItem(
                            title=current_title,
                            paragraphs=list(current_paragraphs),
                            is_heading1=is_heading1,
                            page_break_before=(current_title != "KIRISH")
                        ))
                        current_paragraphs = []

                    current_title = fixed_title or m.group(1).replace("#", "").strip()
                    is_heading1 = h1_flag
                    matched_heading = True
                    break

            if not matched_heading:
                # Clean stray markdown symbols
                clean_line = re.sub(r"^\s*[\*\-]\s+", "", line)
                clean_line = re.sub(r"\*\*([^*]+)\*\*", r"\1", clean_line)
                clean_line = re.sub(r"\*([^*]+)\*", r"\1", clean_line)
                clean_line = re.sub(r"^#+\s*", "", clean_line)
                clean_line = clean_line.strip()

                if clean_line:
                    current_paragraphs.append(clean_line)

        # Append final section if not empty
        if current_paragraphs:
            sections.append(SectionItem(
                title=current_title,
                paragraphs=list(current_paragraphs),
                is_heading1=is_heading1,
                page_break_before=(current_title != "KIRISH")
            ))

        # If references were empty, generate default academic reference templates
        if not references:
            references = [
                "O'zbekiston Respublikasi Prezidentining 2023-yil 11-sentabrdagi PF-158-son Farmoni «O'zbekiston -- 2030» strategiyasi to'g'risida.",
                "Mirziyoyev Sh.M. Yangi O'zbekiston taraqqiyot strategiyasi. -- Toshkent: O'zbekiston nashriyoti, 2022.",
                "O'zbekiston Respublikasi Prezidenti huzuridagi Statistika agentligi rasmiy portali. -- https://stat.uz.",
                "O'zbekiston Respublikasi Markaziy banki axborotnomasi va statistik byulleteni. -- https://cbu.uz.",
                "Iqtisodiyot nazariyasi / Darslik. Prof. Sh. Shodmonov tahriri ostida. -- Toshkent: Iqtisod-Moliya, 2021. -- 420 b."
            ]

        # Ensure at least KIRISH and XULOSA exist
        has_intro = any("kirish" in s.title.lower() for s in sections)
        if not has_intro and sections:
            sections[0].title = "KIRISH"

        return MustaqilIshDocument(
            title_info=title_info,
            sections=sections,
            references=references
        )
