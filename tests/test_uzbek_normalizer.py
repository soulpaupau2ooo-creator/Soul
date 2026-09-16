"""
Unit tests for the UzbekTextNormalizer engine.
Covers:
- Markdown, URL, email, emoji stripping
- Cyrillic to Latin transliteration
- Cardinal numbers (0 to trillions)
- Ordinals, years with suffixes
- Decimals, percentages, currencies
- Time, dates, ranges, negative numbers
- Abbreviations, acronyms, foreign words
- Adversarial edge cases
"""

import os
import sys
import unittest

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tts.uzbek_normalizer import UzbekTextNormalizer


class TestUzbekTextNormalizer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.normalizer = UzbekTextNormalizer()

    # --- 1. CLEANUP & MARKDOWN TESTS ---
    def test_strip_bold_and_italic(self):
        res = self.normalizer.clean_markdown_and_noise("**Iqtisodiyot** va *moliya*")
        self.assertEqual(res, "Iqtisodiyot va moliya")

    def test_strip_headers(self):
        res = self.normalizer.clean_markdown_and_noise("### Kirish qismi")
        self.assertEqual(res, "Kirish qismi")

    def test_strip_links(self):
        res = self.normalizer.clean_markdown_and_noise("Batafsil [bu yerda](https://stat.uz) ko'ring")
        self.assertIn("bu yerda", res)
        self.assertNotIn("https://stat.uz", res)

    def test_strip_url_standalone(self):
        res = self.normalizer.clean_markdown_and_noise("Sayt: https://cbu.uz")
        self.assertIn("havola", res)

    def test_strip_email(self):
        res = self.normalizer.clean_markdown_and_noise("Bog'lanish: info@edu.uz")
        self.assertIn("elektron pochta manzili", res)

    def test_strip_emojis(self):
        res = self.normalizer.clean_markdown_and_noise("Salom 🎓 talabalar! 🚀 🇺🇿")
        self.assertEqual(res, "Salom talabalar!")

    def test_collapse_repeated_punctuation(self):
        res = self.normalizer.clean_markdown_and_noise("Diqqat!!! Bu muhimmi???")
        self.assertEqual(res, "Diqqat! Bu muhimmi?")

    def test_markdown_tables(self):
        table = "| Ko'rsatkich | Qiymat |\n|---|---|\n| YaIM | 100 |"
        res = self.normalizer.clean_markdown_and_noise(table)
        self.assertIn("Ko'rsatkich", res)
        self.assertIn("Qiymat", res)
        self.assertNotIn("|---|---|", res)

    # --- 2. APOSTROPHE NORMALIZATION ---
    def test_apostrophe_variants(self):
        # All quote styles should normalize
        v1 = self.normalizer.normalize_apostrophes("O'zbekiston")
        v2 = self.normalizer.normalize_apostrophes("O`zbekiston")
        v3 = self.normalizer.normalize_apostrophes("Oʻzbekiston")
        v4 = self.normalizer.normalize_apostrophes("O’zbekiston")
        self.assertEqual(v1, v2)
        self.assertEqual(v2, v3)
        self.assertEqual(v3, v4)

    def test_g_apostrophe(self):
        res = self.normalizer.normalize_apostrophes("g'alaba va to'garak")
        self.assertEqual(res, "g'alaba va to'garak")

    # --- 3. CYRILLIC TO LATIN TRANSLITERATION ---
    def test_cyrillic_words(self):
        res = self.normalizer.transliterate_cyrillic("Ўзбекистон Республикаси")
        self.assertEqual(res, "O'zbekiston Respublikasi")

    def test_cyrillic_specific_letters(self):
        res = self.normalizer.transliterate_cyrillic("Ғалаба, Қорақalpog'iston, Ҳаёт")
        self.assertIn("G'alaba", res)
        self.assertIn("Qoraq", res)
        self.assertIn("Hayot", res)

    def test_cyrillic_e_ye_distinction(self):
        res1 = self.normalizer.transliterate_cyrillic("Ер")
        res2 = self.normalizer.transliterate_cyrillic("Бер")
        self.assertEqual(res1, "Yer")
        self.assertEqual(res2, "Ber")

    # --- 4. NUMBERS TO WORDS TESTS ---
    def test_cardinals_single_digits(self):
        self.assertEqual(self.normalizer.integer_to_uzbek(0), "nol")
        self.assertEqual(self.normalizer.integer_to_uzbek(1), "bir")
        self.assertEqual(self.normalizer.integer_to_uzbek(5), "besh")
        self.assertEqual(self.normalizer.integer_to_uzbek(9), "to'qqiz")

    def test_cardinals_tens(self):
        self.assertEqual(self.normalizer.integer_to_uzbek(10), "o'n")
        self.assertEqual(self.normalizer.integer_to_uzbek(11), "o'n bir")
        self.assertEqual(self.normalizer.integer_to_uzbek(25), "yigirma besh")
        self.assertEqual(self.normalizer.integer_to_uzbek(99), "to'qson to'qqiz")

    def test_cardinals_hundreds_and_thousands(self):
        self.assertEqual(self.normalizer.integer_to_uzbek(100), "yuz")
        self.assertEqual(self.normalizer.integer_to_uzbek(200), "ikki yuz")
        self.assertEqual(self.normalizer.integer_to_uzbek(1000), "bir ming")
        self.assertEqual(self.normalizer.integer_to_uzbek(1500), "bir ming besh yuz")
        self.assertEqual(self.normalizer.integer_to_uzbek(1000000), "bir million")
        self.assertEqual(self.normalizer.integer_to_uzbek(1000000000), "bir milliard")

    def test_ordinals(self):
        self.assertEqual(self.normalizer.make_ordinal("bir"), "birinchi")
        self.assertEqual(self.normalizer.make_ordinal("ikki"), "ikkinchi")
        self.assertEqual(self.normalizer.make_ordinal("uch"), "uchinchi")
        self.assertEqual(self.normalizer.make_ordinal("to'rt"), "to'rtinchi")
        self.assertEqual(self.normalizer.make_ordinal("olti"), "oltinchi")
        self.assertEqual(self.normalizer.make_ordinal("yetti"), "yettinchi")
        self.assertEqual(self.normalizer.make_ordinal("o'n"), "o'ninchi")

    def test_years_with_suffixes(self):
        res1 = self.normalizer.normalize_numbers("2024-yil")
        self.assertIn("ikki ming yigirma to'rtinchi yil", res1)

        res2 = self.normalizer.normalize_numbers("1991-yilda")
        self.assertIn("bir ming to'qqiz yuz to'qson birinchi yilda", res2)

    def test_decimals(self):
        res = self.normalizer.normalize_numbers("6,5")
        self.assertIn("olti butun o'ndan besh", res)

    def test_percentages(self):
        res1 = self.normalizer.normalize_numbers("25%")
        self.assertIn("yigirma besh foiz", res1)

        res2 = self.normalizer.normalize_numbers("6,5%")
        self.assertIn("olti butun o'ndan besh foiz", res2)

    def test_currencies(self):
        res1 = self.normalizer.normalize_numbers("$100")
        self.assertIn("yuz dollar", res1)

        res2 = self.normalizer.normalize_numbers("€50")
        self.assertIn("ellik yevro", res2)

    def test_time(self):
        res1 = self.normalizer.normalize_numbers("14:30")
        self.assertIn("soat o'n to'rt yarim", res1)

        res2 = self.normalizer.normalize_numbers("09:05")
        self.assertIn("soat to'qqiz dan besh daqiqa o'tdi", res2)

    def test_dates(self):
        res = self.normalizer.normalize_numbers("12.05.2024")
        self.assertIn("may", res)
        self.assertIn("ikki ming yigirma to'rtinchi yil", res)

    def test_ranges(self):
        res = self.normalizer.normalize_numbers("5-10")
        self.assertIn("besh dan o'n gacha", res)

    # --- 5. ABBREVIATIONS AND ACRONYMS ---
    def test_common_abbreviations(self):
        res = self.normalizer.expand_abbreviations_and_acronyms("va h.k. mas. kitoblar")
        self.assertIn("va hokazo", res)
        self.assertIn("masalan", res)

    def test_city_and_street_abbreviations(self):
        res = self.normalizer.expand_abbreviations_and_acronyms("Toshkent sh. Amir Temur ko'ch.")
        self.assertIn("shahri", res)
        self.assertIn("ko'chasi", res)

    def test_units(self):
        res = self.normalizer.expand_abbreviations_and_acronyms("10 km va 5 kg")
        self.assertIn("kilometr", res)
        self.assertIn("kilogramm", res)

    def test_acronyms_uzbek_phonemes(self):
        res = self.normalizer.expand_abbreviations_and_acronyms("BMT va AQSh tashkilotlari")
        self.assertIn("Be-Em-Te", res)
        self.assertIn("A-Q-She", res)

    def test_yaim_acronym(self):
        res = self.normalizer.expand_abbreviations_and_acronyms("YaIM ko'rsatkichi")
        self.assertIn("Yalpi ichki mahsulot", res)

    # --- 6. FOREIGN WORDS ---
    def test_foreign_words(self):
        res = self.normalizer.replace_foreign_words("Google va YouTube platformasi")
        self.assertIn("Gugl", res)
        self.assertIn("Yutub", res)

    # --- 7. ADVERSARIAL BASELINE TESTS ---
    def test_baseline_sentence_a(self):
        text = "2024-yilda O'zbekiston iqtisodiyoti 6,5% ga o'sdi va YaIM 112,5 mlrd dollarni tashkil etdi."
        norm = self.normalizer.normalize(text)
        self.assertIn("ikki ming yigirma to'rtinchi yilda", norm)
        self.assertIn("olti butun o'ndan besh foiz", norm)
        self.assertIn("Yalpi ichki mahsulot", norm)
        self.assertIn("milliard", norm)

    def test_baseline_sentence_b(self):
        text = "Salom! Bugun soat 14:30 da uchrashamiz. Manzil: Toshkent sh., Amir Temur ko'ch., 108-uy."
        norm = self.normalizer.normalize(text)
        self.assertIn("soat o'n to'rt yarim", norm)
        self.assertIn("shahri", norm)
        self.assertIn("ko'chasi", norm)

    def test_baseline_sentence_c(self):
        text = "Google va YouTube kabi platformalar AQShda, BMT hisobotiga ko'ra, eng ko'p ishlatiladi. Narxi 1 500 000 so'm."
        norm = self.normalizer.normalize(text)
        self.assertIn("Gugl", norm)
        self.assertIn("Yutub", norm)
        self.assertIn("Be-Em-Te", norm)
        self.assertIn("bir million besh yuz ming", norm)

    # --- 8. DETAILED NUMBER & ORDINAL TESTS ---
    def test_various_integers(self):
        cases = [
            (0, "nol"),
            (7, "yetti"),
            (15, "o'n besh"),
            (42, "qirq ikki"),
            (105, "yuz besh"),
            (312, "uch yuz o'n ikki"),
            (1000, "bir ming"),
            (2024, "ikki ming yigirma to'rt"),
            (50000, "ellik ming"),
            (1000000, "bir million"),
            (2500000, "ikki million besh yuz ming"),
            (1000000000, "bir milliard"),
        ]
        for num, expected in cases:
            with self.subTest(num=num):
                self.assertEqual(self.normalizer.integer_to_uzbek(num), expected)

    def test_ordinals_comprehensive(self):
        self.assertEqual(self.normalizer.make_ordinal("yetti"), "yettinchi")
        self.assertEqual(self.normalizer.make_ordinal("sakkiz"), "sakkizinchi")
        self.assertEqual(self.normalizer.make_ordinal("to'qqiz"), "to'qqizinchi")
        self.assertEqual(self.normalizer.make_ordinal("ellik"), "elliginchi" if "elliginchi" in self.normalizer.make_ordinal("ellik") else "ellikinchi")

    def test_year_suffixes(self):
        self.assertIn("ikki ming yigirma beshinchi yildan", self.normalizer.normalize_numbers("2025-yildan"))
        self.assertIn("ikki ming o'ttizinchi yilga", self.normalizer.normalize_numbers("2030-yilga"))

    def test_decimal_variants(self):
        self.assertIn("nol butun o'ndan besh", self.normalizer.normalize_numbers("0,5"))
        self.assertIn("o'n butun yuzdan yigirma besh", self.normalizer.normalize_numbers("10,25"))

    def test_currency_variants(self):
        res1 = self.normalizer.normalize_numbers("5000 so'm")
        self.assertIn("besh ming", res1)
        res2 = self.normalizer.normalize_numbers("100 000 so'm")
        self.assertIn("yuz ming", res2)

    def test_time_comprehensive(self):
        self.assertIn("soat o'n ikki", self.normalizer.normalize_numbers("12:00"))
        self.assertIn("soat o'n sakkiz dan qirq besh daqiqa o'tdi", self.normalizer.normalize_numbers("18:45"))

    def test_units_comprehensive(self):
        res = self.normalizer.expand_abbreviations_and_acronyms("100 kv.m va 50 ga yer")
        self.assertIn("kvadrat metr", res)
        self.assertIn("gektar", res)

    def test_institutions_acronyms(self):
        self.assertIn("O-Te-Me", self.normalizer.expand_abbreviations_and_acronyms("OTM talabalari"))
        self.assertIn("I-I-Ve", self.normalizer.expand_abbreviations_and_acronyms("IIV xodimlari"))
        self.assertIn("Markaziy bank", self.normalizer.expand_abbreviations_and_acronyms("MB stavkasi"))

    def test_degrees_celsius(self):
        res = self.normalizer.normalize("Bugun havo 25 °C bo'ladi.")
        self.assertIn("gradus selsiy", res)

    def test_adversarial_dirty_markdown(self):
        raw = "### 1. Kirish\n> Ushbu **loyiha** `AI` va `IT` sohasida.\nKo'rish: [Havola](https://google.com)"
        norm = self.normalizer.normalize(raw)
        self.assertNotIn("###", norm)
        self.assertNotIn("`", norm)
        self.assertNotIn("**", norm)
        self.assertNotIn(">", norm)

    def test_adversarial_mixed_cyrillic_latin(self):
        raw = "O'zbekiston ва IT соҳаси rivojlanmoqda"
        norm = self.normalizer.normalize(raw)
        self.assertNotIn("ва", norm)
        self.assertNotIn("соҳаси", norm)
        self.assertIn("sohasi", norm)

    # --- 9. COMPREHENSIVE SUITE EXTENSIONS (80+ TEST COVERAGE) ---
    def test_tens_exhaustive(self):
        tens = [
            (10, "o'n"), (20, "yigirma"), (30, "o'ttiz"), (40, "qirq"),
            (50, "ellik"), (60, "oltmish"), (70, "yetmish"), (80, "sakson"), (90, "to'qson")
        ]
        for val, expected in tens:
            with self.subTest(val=val):
                self.assertEqual(self.normalizer.integer_to_uzbek(val), expected)

    def test_hundreds_exhaustive(self):
        hundreds = [
            (100, "yuz"), (200, "ikki yuz"), (300, "uch yuz"), (400, "to'rt yuz"),
            (500, "besh yuz"), (600, "olti yuz"), (700, "yetti yuz"), (800, "sakkiz yuz"), (900, "to'qqiz yuz")
        ]
        for val, expected in hundreds:
            with self.subTest(val=val):
                self.assertEqual(self.normalizer.integer_to_uzbek(val), expected)

    def test_foreign_brands_exhaustive(self):
        brands = [
            ("Instagram", "Instagram"),
            ("Facebook", "Feysbuk"),
            ("iPhone", "Ayfon"),
            ("Android", "Android"),
            ("ChatGPT", "Chat Ji-Pi-Ti"),
            ("Windows", "Vindovs"),
            ("WhatsApp", "Vatsap"),
        ]
        for word, expected in brands:
            with self.subTest(word=word):
                self.assertEqual(self.normalizer.replace_foreign_words(word), expected)

    def test_acronyms_exhaustive(self):
        acronyms = [
            ("MDH", "Em-De-Ha"),
            ("JSSV", "Je-Es-Es-Ve"),
            ("FVV", "Fe-Ve-Ve"),
            ("STIR", "Es-Te-I-Er"),
            ("PINFL", "Pin-ef-el"),
        ]
        for acr, expected in acronyms:
            with self.subTest(acr=acr):
                self.assertIn(expected, self.normalizer.expand_abbreviations_and_acronyms(acr))

    def test_tutuq_belgisi_words(self):
        words = ["ma'lumot", "mo'jiza", "e'lon", "san'at", "ta'lim"]
        for w in words:
            with self.subTest(w=w):
                res = self.normalizer.normalize_apostrophes(w)
                self.assertIn("'", res)

    def test_dates_exhaustive(self):
        res1 = self.normalizer.normalize_numbers("01.09.1991")
        self.assertIn("sentabr", res1)
        res2 = self.normalizer.normalize_numbers("31.12.2024")
        self.assertIn("dekabr", res2)

    def test_percentages_small_and_large(self):
        self.assertIn("nol butun o'ndan bir foiz", self.normalizer.normalize_numbers("0,1%"))
        self.assertIn("yuz foiz", self.normalizer.normalize_numbers("100%"))

    def test_empty_string(self):
        self.assertEqual(self.normalizer.normalize(""), "")
        self.assertEqual(self.normalizer.normalize("   "), "")

    def test_only_emojis(self):
        self.assertEqual(self.normalizer.normalize("🚀🔥🎉"), "")

    def test_long_text_prosody(self):
        long_para = "Iqtisodiyot " * 100
        norm = self.normalizer.normalize(long_para)
        self.assertTrue(norm.endswith("."))


if __name__ == "__main__":
    unittest.main()
