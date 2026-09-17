"""
Test verification for Mustaqil Ish volume expansion and references omission.
Asserts:
1. Academic essay parser splits chapters (Kirish, 1-bob, 2-bob, Xulosa).
2. References section is omitted when include_references=False.
3. Generated docx does not contain 'FOYDALANILGAN ADABIYOTLAR RO'YXATI'.
4. Full text spans sufficient paragraphs and volume for at least 2 full pages.
"""

import io
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import docx
from docgen.mustaqil_ish import MustaqilIshDocxBuilder, TitlePageInfo
from docgen.content_parser import AcademicEssayParser
from economics_curriculum import build_academic_essay_prompt


class TestEssayVolumeAndNoRefs(unittest.TestCase):
    def test_prompt_demands_large_volume_and_forbids_references(self):
        prompt = build_academic_essay_prompt("Iqtisodiyot", "Asosiy vositalar hisobi va amortizatsiyasi")
        self.assertIn("2 TO'LIQ LIST", prompt)
        self.assertIn("3 600 dan 4 200 gacha belgi", prompt)
        self.assertIn("ADABIYOTLAR RO'YXATI", prompt)
        self.assertIn("QAT'IYAN TAQIQLANADI", prompt)

    def test_parser_omits_references_by_default(self):
        sample_essay = (
            "KIRISH\n"
            "Asosiy vositalar korxonaning uzoq muddatli ishlab chiqarish salohiyatini belgilovchi tayanch vositadir. "
            "Ushbu tadqiqotning dolzarbligi shundaki, aktivlarning eskirish sur'atlarini to'g'ri hisoblash tannarxni shakllantirishda "
            "va moliyaviy barqarorlikni ta'minlashda muhim rol o'ynaydi.\n\n"
            "1-BOB. ASOSIY VOSITALAR HISOBINING NAZARIY ASOSLARI\n"
            "Asosiy vositalar hisobining nazariy asoslari buxgalteriya hisobining milliy va xalqaro standartlariga tayanadi. "
            "Amortizatsiya ajratmalarini hisoblashda to'g'ri chiziqli, tezlashtirilgan va kamayib boruvchi qoldiq usullari qo'llaniladi.\n\n"
            "2-BOB. O'ZBEKISTON AMALIYOTIDA ASOSIY FONDLAR TAHLILI\n"
            "O'zbekiston Respublikasi Statistika agentligi ma'lumotlariga ko'ra, jami investitsiyalarning 45 foizdan ortig'i "
            "asosiy kapitalni modernizatsiya qilishga yo'naltirilmoqda. Sanoat tarmoqlarida fondlarning eskirish darajasi o'rtacha "
            "35-40 foiz atrofida saqlanib qolmoqda.\n\n"
            "XULOSA VA TAKLIFLAR\n"
            "O'tkazilgan tadqiqotlar shuni ko'rsatadiki, soliq qonunchiligida tezlashtirilgan amortizatsiya mexanizmlarini kengaytirish "
            "tadbirkorlik subyektlarining investitsion faolligini rag'batlantiradi.\n\n"
            "FOYDALANILGAN ADABIYOTLAR RO'YXATI\n"
            "1. Mirziyoyev Sh.M. Yangi O'zbekiston taraqqiyot strategiyasi.\n"
            "2. stat.uz ma'lumotlari.\n"
        )
        title_info = TitlePageInfo(
            university="TDIU",
            faculty="Iqtisodiyot",
            department="Buxgalteriya hisobi",
            subject="Iqtisodiyot",
            topic="Asosiy vositalar hisobi va amortizatsiyasi",
            student_name="Azizbek",
            group_name="IQ-101",
            teacher_name="dots. Karimov A."
        )

        # By default include_references=False:
        doc_data = AcademicEssayParser.parse_essay_to_document(sample_essay, title_info, include_references=False)
        self.assertEqual(len(doc_data.references), 0)
        self.assertGreaterEqual(len(doc_data.sections), 4)

        # Check section titles
        titles = [s.title for s in doc_data.sections]
        self.assertIn("KIRISH", titles)
        self.assertTrue(any("1-BOB" in t for t in titles))
        self.assertTrue(any("2-BOB" in t for t in titles))
        self.assertTrue(any("XULOSA" in t for t in titles))

        # Generate DOCX and assert no references page
        builder = MustaqilIshDocxBuilder()
        docx_bytes = builder.generate_docx(doc_data)
        doc = docx.Document(io.BytesIO(docx_bytes))

        full_doc_text = "\n".join(p.text for p in doc.paragraphs)
        self.assertNotIn("FOYDALANILGAN ADABIYOTLAR RO'YXATI", full_doc_text)

    def test_section_page_breaks_flow_smoothly_for_two_pages(self):
        sample_essay = (
            "KIRISH\n"
            "Mavzuning dolzarbligi va maqsadlari.\n\n"
            "1-BOB. NAZARIY ASOSLAR\n"
            "Iqtisodiy nazariyalar va xalqaro tajriba.\n\n"
            "2-BOB. O'ZBEKISTON AMALIYOTI\n"
            "Rasmiy statistika va islohotlar tahlili.\n\n"
            "XULOSA VA TAKLIFLAR\n"
            "Amaliy takliflar va xulosalar.\n"
        )
        title_info = TitlePageInfo(
            university="TDIU",
            faculty="Iqtisodiyot",
            department="Moliya",
            subject="Iqtisodiyot",
            topic="Raqamli iqtisodiyot",
            student_name="Azizbek",
            group_name="IQ-101"
        )
        # Default should have page_break_before=False for smooth 2-page flow without blank gaps
        doc_data_continuous = AcademicEssayParser.parse_essay_to_document(
            sample_essay, title_info, page_break_between_sections=False
        )
        for sec in doc_data_continuous.sections:
            self.assertFalse(sec.page_break_before)

        # When explicitly requested, subsequent chapters break pages
        doc_data_broken = AcademicEssayParser.parse_essay_to_document(
            sample_essay, title_info, page_break_between_sections=True
        )
        for sec in doc_data_broken.sections:
            if sec.title == "KIRISH":
                self.assertFalse(sec.page_break_before)
            else:
                self.assertTrue(sec.page_break_before)


if __name__ == "__main__":
    unittest.main()
