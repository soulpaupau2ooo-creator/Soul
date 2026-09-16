"""
Uzbek Text Normalization Engine for High-Quality Text-to-Speech (TTS).

This module performs deterministic multi-stage linguistic and orthographic
transformations tailored specifically for Uzbek Latin speech synthesis.
It handles numbers, currencies, dates, abbreviations, Cyrillic transliteration,
acronym phonetization, and markdown cleanup.
"""

from __future__ import annotations

import json
import os
import re
from typing import Dict, List, Optional, Tuple

# --- LINGUISTIC CONSTANTS ---

CARDINAL_UNITS: Dict[int, str] = {
    0: "nol",
    1: "bir",
    2: "ikki",
    3: "uch",
    4: "to'rt",
    5: "besh",
    6: "olti",
    7: "yetti",
    8: "sakkiz",
    9: "to'qqiz",
}

CARDINAL_TENS: Dict[int, str] = {
    10: "o'n",
    20: "yigirma",
    30: "o'ttiz",
    40: "qirq",
    50: "ellik",
    60: "oltmish",
    70: "yetmish",
    80: "sakson",
    90: "to'qson",
}

SCALE_NAMES: List[Tuple[int, str]] = [
    (1_000_000_000_000, "trillion"),
    (1_000_000_000, "milliard"),
    (1_000_000, "million"),
    (1_000, "ming"),
    (100, "yuz"),
]

MONTHS_UZ: Dict[int, str] = {
    1: "yanvar",
    2: "fevral",
    3: "mart",
    4: "aprel",
    5: "may",
    6: "iyun",
    7: "iyul",
    8: "avgust",
    9: "sentabr",
    10: "oktabr",
    11: "noyabr",
    12: "dekabr",
}

CYRILLIC_TO_LATIN_MAP: Dict[str, str] = {
    "А": "A", "а": "a",
    "Б": "B", "б": "b",
    "В": "V", "в": "v",
    "Г": "G", "г": "g",
    "Д": "D", "д": "d",
    "Е": "E", "е": "e",
    "Ё": "Yo", "ё": "yo",
    "Ж": "J", "ж": "j",
    "З": "Z", "з": "z",
    "И": "I", "и": "i",
    "Й": "Y", "й": "y",
    "К": "K", "к": "k",
    "Л": "L", "л": "l",
    "М": "M", "м": "m",
    "Н": "N", "н": "n",
    "О": "O", "о": "o",
    "П": "P", "п": "p",
    "Р": "R", "р": "r",
    "С": "S", "с": "s",
    "Т": "T", "т": "t",
    "У": "U", "у": "u",
    "Ф": "F", "ф": "f",
    "Х": "X", "х": "x",
    "Ц": "Ts", "ц": "ts",
    "Ч": "Ch", "ч": "ch",
    "Ш": "Sh", "ш": "sh",
    "Щ": "Sh", "щ": "sh",
    "Ъ": "ʼ", "ъ": "ʼ",
    "Ы": "I", "ы": "i",
    "Ь": "", "ь": "",
    "Э": "E", "э": "e",
    "Ю": "Yu", "ю": "yu",
    "Я": "Ya", "я": "ya",
    "Ў": "Oʻ", "ў": "oʻ",
    "Қ": "Q", "қ": "q",
    "Ғ": "Gʻ", "ғ": "gʻ",
    "Ҳ": "H", "ҳ": "h",
}

UZBEK_LETTER_PHONEMES: Dict[str, str] = {
    "A": "A", "B": "Be", "D": "De", "E": "E", "F": "Ef", "G": "Ge",
    "H": "Ha", "I": "I", "J": "Je", "K": "Ka", "L": "El", "M": "Em",
    "N": "En", "O": "O", "P": "Pe", "Q": "Qa", "R": "Er", "S": "Es",
    "T": "Te", "U": "U", "V": "Ve", "X": "Iks", "Y": "Ye", "Z": "Zet",
    "SH": "She", "CH": "Che", "Oʻ": "Oʻ", "Gʻ": "Gʻ",
}

ACRONYMS_MAP: Dict[str, str] = {
    "AQSH": "A-Q-She",
    "AQSh": "A-Q-She",
    "BMT": "Be-Em-Te",
    "MDH": "Em-De-Ha",
    "YAIM": "Yalpi ichki mahsulot",
    "YaIM": "Yalpi ichki mahsulot",
    "OAV": "O-A-Ve",
    "JSSV": "Je-Es-Es-Ve",
    "OTM": "O-Te-Me",
    "IIV": "I-I-Ve",
    "DTM": "De-Te-Me",
    "FVV": "Fe-Ve-Ve",
    "DXA": "De-Iks-A",
    "YHXK": "Yo-Ha-Iks-Ka",
    "YHXQ": "Yo-Ha-Iks-Qa",
    "MB": "Markaziy bank",
    "STIR": "Es-Te-I-Er",
    "PINFL": "Pin-ef-el",
    "IT": "Ayti",
    "AI": "Sun'iy intellekt",
}

ABBREVIATIONS_MAP: Dict[str, str] = {
    "va h.k.": "va hokazo",
    "va boshq.": "va boshqalar",
    "v.b.": "va boshqalar",
    "sh.k.": "shu kabi",
    "mas.": "masalan",
    "prof.": "professor",
    "dots.": "dotsent",
    "akad.": "akademik",
    "sh.": "shahri",
    "t.": "tumani",
    "v.": "viloyati",
    "ko'ch.": "ko'chasi",
    "k-si": "ko'chasi",
    "uy.": "uyi",
    "xon.": "xonadoni",
}

UNITS_MAP: Dict[str, str] = {
    "km": "kilometr",
    "m": "metr",
    "sm": "santimetr",
    "mm": "millimetr",
    "kg": "kilogramm",
    "g": "gramm",
    "t": "tonna",
    "l": "litr",
    "ml": "millilitr",
    "mlrd": "milliard",
    "mln": "million",
    "ming": "ming",
    "soat": "soat",
    "daq": "daqiqa",
    "sek": "sekund",
    "kv.m": "kvadrat metr",
    "kv.km": "kvadrat kilometr",
    "ga": "gektar",
    "°C": "gradus selsiy",
    "C": "selsiy",
    "%": "foiz",
}


class UzbekTextNormalizer:
    """Enterprise-grade normalizer converting raw text into TTS-ready Uzbek speech."""

    def __init__(self, foreign_words_path: Optional[str] = None):
        self.foreign_words: Dict[str, str] = {}
        default_dict_path = foreign_words_path or os.path.join(
            os.path.dirname(__file__), "foreign_words.json"
        )
        if os.path.exists(default_dict_path):
            try:
                with open(default_dict_path, "r", encoding="utf-8") as f:
                    self.foreign_words = json.load(f)
            except Exception:
                self.foreign_words = {}

    # --- STAGE 1: CLEANUP ---

    def clean_markdown_and_noise(self, text: str) -> str:
        """Strip markdown formatting, tables, noisy characters, URLs, and emails."""
        if not text:
            return ""

        # Remove invisible/zero-width chars
        text = re.sub(r"[\u200B-\u200D\uFEFF\u00AD]", "", text)

        # Replace markdown table rows (lines with pipes |)
        table_lines_cleaned = []
        for line in text.split("\n"):
            stripped = line.strip()
            if stripped.startswith("|") and stripped.endswith("|"):
                # Table separator row (|---|---|) -> ignore
                if re.match(r"^\|[\s\-:|]+\|$", stripped):
                    continue
                # Extract text items from table row
                cells = [c.strip() for c in stripped.split("|") if c.strip()]
                if cells:
                    table_lines_cleaned.append(". ".join(cells) + ".")
            else:
                table_lines_cleaned.append(line)
        text = "\n".join(table_lines_cleaned)

        # Replace URLs
        text = re.sub(r"https?://\S+|www\.\S+", "havola", text)

        # Replace Email addresses
        text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "elektron pochta manzili", text)

        # Remove code blocks
        text = re.sub(r"```[\s\S]*?```", " ", text)
        text = re.sub(r"`([^`]+)`", r"\1", text)

        # Strip markdown headers (#, ##, ###)
        text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)

        # Strip markdown links [label](url) -> label
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)

        # Strip bold and italics (*, _, ~)
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
        text = re.sub(r"\*([^*]+)\*", r"\1", text)
        text = re.sub(r"__([^_]+)__", r"\1", text)
        text = re.sub(r"~~([^~]+)~~", r"\1", text)

        # Remove blockquotes
        text = re.sub(r"^>\s+", "", text, flags=re.MULTILINE)

        # Remove emojis
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "\U0001F900-\U0001F9FF"  # supplemental symbols
            "\U0001FA70-\U0001FAFF"
            "]+",
            flags=re.UNICODE,
        )
        text = emoji_pattern.sub(" ", text)

        # Collapse repeated punctuation: !!! -> !, ??? -> ?, .... -> ...
        text = re.sub(r"!{2,}", "!", text)
        text = re.sub(r"\?{2,}", "?", text)
        text = re.sub(r"\.{4,}", "...", text)

        # Collapse whitespace
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    # --- STAGE 2: APOSTROPHE NORMALIZATION ---

    def normalize_apostrophes(self, text: str) -> str:
        """
        Normalize Uzbek Latin specific letters Oʻ, Gʻ and the tutuq belgisi (apostrophe).
        Standardizes various typed quotes (', `, ‘, ’, ´) to clean standard apostrophe.
        Edge-TTS voices (uz-UZ-MadinaNeural and uz-UZ-SardorNeural) pronounce best
        with standard clean apostrophe (') or modifier turned comma (ʻ).
        """
        # Unified replacement for variants of apostrophe
        # U+02BB (ʻ), U+02BC (ʼ), U+2018 (‘), U+2019 (’), U+0060 (`), U+00B4 (´) -> '
        text = re.sub(r"[ʻʼ‘’`´]", "'", text)

        # Ensure correct spacing around apostrophes in O' and G'
        text = re.sub(r"\b([oOgG])\s+'", r"\1'", text)
        return text

    # --- STAGE 3: SCRIPT HANDLING (CYRILLIC TO LATIN) ---

    def transliterate_cyrillic(self, text: str) -> str:
        """Transliterate Uzbek Cyrillic into standard Uzbek Latin."""
        if not text:
            return ""

        # Check if text contains Cyrillic characters
        if not re.search(r"[\u0400-\u04FF]", text):
            return text

        # Handle contextual 'Е' / 'е' (Ye at word start or after vowel)
        def replace_e(match: re.Match) -> str:
            prefix = match.group(1)
            char = match.group(2)
            is_upper = char == "Е"
            if not prefix or re.search(r"[аеёиоуэюяАЕЁИОУЭЮЯ\s\b\.,!?:;\-]", prefix):
                return prefix + ("Ye" if is_upper else "ye")
            return prefix + ("E" if is_upper else "e")

        text = re.sub(r"(^|[\s\b\.,!?:;\-аеёиоуэюяАЕЁИОУЭЮЯ])([Ее])", replace_e, text)

        # Multi-character mappings
        multi_chars = [
            ("Ў", "O'"), ("ў", "o'"),
            ("Ғ", "G'"), ("ғ", "g'"),
            ("Ш", "Sh"), ("ш", "sh"),
            ("Ч", "Ch"), ("ч", "ch"),
            ("Ё", "Yo"), ("ё", "yo"),
            ("Ю", "Yu"), ("ю", "yu"),
            ("Я", "Ya"), ("ya", "ya"),
            ("Ц", "Ts"), ("ц", "ts"),
        ]
        for cyr, lat in multi_chars:
            text = text.replace(cyr, lat)

        # Single characters
        result = []
        for char in text:
            result.append(CYRILLIC_TO_LATIN_MAP.get(char, char))
        return "".join(result)

    # --- STAGE 4: NUMBERS TO UZBEK WORDS ---

    def integer_to_uzbek(self, n: int) -> str:
        """Convert any positive integer (up to 999 999 999 999) to Uzbek words."""
        if n == 0:
            return "nol"
        if n < 0:
            return "minus " + self.integer_to_uzbek(abs(n))

        parts: List[str] = []

        # Billions, Millions, Thousands, Hundreds
        for scale_val, scale_name in SCALE_NAMES:
            count = n // scale_val
            if count > 0:
                if scale_val == 100:
                    if count == 1:
                        parts.append("yuz")
                    else:
                        parts.append(self.integer_to_uzbek(count) + " yuz")
                else:
                    parts.append(self.integer_to_uzbek(count) + " " + scale_name)
                n %= scale_val

        # Tens
        tens_val = (n // 10) * 10
        if tens_val in CARDINAL_TENS:
            parts.append(CARDINAL_TENS[tens_val])
            n %= 10

        # Units
        if n in CARDINAL_UNITS and n > 0:
            parts.append(CARDINAL_UNITS[n])

        return " ".join(parts).strip()

    def make_ordinal(self, words: str) -> str:
        """Apply the Uzbek ordinal suffix (-inchi / -nchi) correctly."""
        words = words.strip()
        if not words:
            return ""

        # Determine last word
        last_word = words.split()[-1].lower()

        # If ends in vowel: -nchi (ikki -> ikkinchi, olti -> oltinchi, yetti -> yettinchi)
        if last_word.endswith(("a", "e", "i", "o", "u")):
            return words + "nchi"
        else:
            return words + "inchi"

    def normalize_numbers(self, text: str) -> str:
        """Replace all numeric constructs (cardinals, ordinals, dates, percentages, currencies)."""
        if not text:
            return ""

        # 1. Dates: DD.MM.YYYY or DD/MM/YYYY -> {yil}-yil {kun}-inchi {oy}
        def date_replacer(match: re.Match) -> str:
            day = int(match.group(1))
            month = int(match.group(2))
            year = int(match.group(3))
            month_name = MONTHS_UZ.get(month, "")
            if 1 <= day <= 31 and month_name:
                year_words = self.make_ordinal(self.integer_to_uzbek(year))
                day_words = self.make_ordinal(self.integer_to_uzbek(day))
                return f"{year_words} yil {day_words} {month_name}"
            return match.group(0)

        text = re.sub(r"\b([0-3]?[0-9])[\./]([0-1]?[0-9])[\./](\d{4})\b", date_replacer, text)

        # 2. Years with suffixes: 2024-yil, 1991-yilda, 2030-yilga, 2025-yildan
        def year_suffix_replacer(match: re.Match) -> str:
            year = int(match.group(1))
            suffix = match.group(2)
            year_words = self.make_ordinal(self.integer_to_uzbek(year))
            return f"{year_words} {suffix}"

        text = re.sub(r"\b(\d{4})-(yil[a-z]*)\b", year_suffix_replacer, text)

        # 3. Time: 14:30 -> soat o'n to'rtdan o'ttiz daqiqa o'tdi
        def time_replacer(match: re.Match) -> str:
            hour = int(match.group(1))
            minute = int(match.group(2))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                h_words = self.integer_to_uzbek(hour)
                if minute == 0:
                    return f"soat {h_words}"
                elif minute == 30:
                    return f"soat {h_words} yarim"
                else:
                    m_words = self.integer_to_uzbek(minute)
                    return f"soat {h_words} dan {m_words} daqiqa o'tdi"
            return match.group(0)

        text = re.sub(r"\b([0-2]?[0-9]):([0-5][0-9])\b", time_replacer, text)

        # 4. Percentages: 6,5% or 25% -> ... foiz
        def percent_replacer(match: re.Match) -> str:
            num_str = match.group(1).replace(" ", "")
            if "," in num_str or "." in num_str:
                parts = re.split(r"[,.]", num_str)
                whole = self.integer_to_uzbek(int(parts[0]))
                dec_val = parts[1]
                dec_word = "o'ndan" if len(dec_val) == 1 else "yuzdan" if len(dec_val) == 2 else "mingdan"
                dec_num = self.integer_to_uzbek(int(dec_val))
                return f"{whole} butun {dec_word} {dec_num} foiz"
            else:
                return f"{self.integer_to_uzbek(int(num_str))} foiz"

        text = re.sub(r"\b(\d+(?:[\s,.]\d+)?)\s*%", percent_replacer, text)

        # 5. Currency: $100, 5000 so'm, €50
        def dollar_replacer(match: re.Match) -> str:
            val = int(match.group(1).replace(" ", "").replace(",", "").replace(".", ""))
            return f"{self.integer_to_uzbek(val)} dollar"

        text = re.sub(r"\$(\d+(?:[\s,.]\d+)*)\b", dollar_replacer, text)

        def euro_replacer(match: re.Match) -> str:
            val = int(match.group(1).replace(" ", "").replace(",", "").replace(".", ""))
            return f"{self.integer_to_uzbek(val)} yevro"

        text = re.sub(r"€(\d+(?:[\s,.]\d+)*)\b", euro_replacer, text)

        # 6. Decimals: 6,5 or 112.5 -> olti butun o'ndan besh
        def decimal_replacer(match: re.Match) -> str:
            whole_str = match.group(1).replace(" ", "")
            dec_str = match.group(2)
            whole_num = int(whole_str)
            dec_num = int(dec_str)
            dec_scale = "o'ndan" if len(dec_str) == 1 else "yuzdan" if len(dec_str) == 2 else "mingdan"
            return f"{self.integer_to_uzbek(whole_num)} butun {dec_scale} {self.integer_to_uzbek(dec_num)}"

        text = re.sub(r"\b(\d+)[,.](\d{1,3})\b", decimal_replacer, text)

        # 7. Thousands-separated numbers: 1 500 000 or 1,500,000
        def thousands_replacer(match: re.Match) -> str:
            clean_num = re.sub(r"[\s,.]", "", match.group(0))
            if clean_num.isdigit():
                return self.integer_to_uzbek(int(clean_num))
            return match.group(0)

        text = re.sub(r"\b\d{1,3}(?:[\s,]\d{3})+\b", thousands_replacer, text)

        # 8. Ranges: 5-10 -> besh dan o'n gacha (BEFORE ordinals!)
        def range_replacer(match: re.Match) -> str:
            n1 = int(match.group(1))
            n2 = int(match.group(2))
            w1 = self.integer_to_uzbek(n1)
            w2 = self.integer_to_uzbek(n2)
            return f"{w1} dan {w2} gacha"

        text = re.sub(r"\b(\d+)\s*-\s*(\d+)\b", range_replacer, text)

        # 9. Ordinals with hyphens: 1-inchi, 2-nchi, 10-sinf, 3-uy
        def ordinal_replacer(match: re.Match) -> str:
            num = int(match.group(1))
            suffix = match.group(2) or ""
            words = self.make_ordinal(self.integer_to_uzbek(num))
            if suffix in ["inchi", "nchi"]:
                return words
            return f"{words} {suffix}".strip()

        text = re.sub(r"\b(\d+)-(inchi|nchi|sinf|uy|bo'lim|bob|mavzu)\b", ordinal_replacer, text)

        # 10. Remaining standalone integers
        def standalone_integer_replacer(match: re.Match) -> str:
            num = int(match.group(0))
            return self.integer_to_uzbek(num)

        text = re.sub(r"\b\d+\b", standalone_integer_replacer, text)

        return text

    # --- STAGE 5: ABBREVIATIONS AND ACRONYMS ---

    def expand_abbreviations_and_acronyms(self, text: str) -> str:
        """Expand common abbreviations and phonetize all-caps acronyms."""
        if not text:
            return ""

        # Common phrase abbreviations
        for abbr, expansion in ABBREVIATIONS_MAP.items():
            pattern = r"\b" + re.escape(abbr)
            text = re.sub(pattern, expansion, text, flags=re.IGNORECASE)

        # Temperature handling explicitly
        text = re.sub(r"(?:°C|gradus\s*C|\b°\b)", "gradus selsiy", text)

        # Compound units with dots or slashes first (e.g. kv.m, kv.km, km/soat)
        text = re.sub(r"\bkv\.m\b", "kvadrat metr", text)
        text = re.sub(r"\bkv\.km\b", "kvadrat kilometr", text)
        text = re.sub(r"\bkm/s(?:oat)?\b", "kilometr soat", text)

        # Standalone units - sort by length descending to prevent substring collisions
        sorted_units = sorted(UNITS_MAP.items(), key=lambda x: len(x[0]), reverse=True)
        for unit, expansion in sorted_units:
            if unit in ["kv.m", "kv.km", "°C", "C"]:
                continue
            text = re.sub(rf"\b{re.escape(unit)}\b", expansion, text)

        # Acronyms mapping
        for acronym, phoneme in ACRONYMS_MAP.items():
            text = re.sub(rf"\b{re.escape(acronym)}\b", phoneme, text)

        # Unknown uppercase acronyms (2-5 letters) -> spell with Uzbek letter names
        def spell_acronym(match: re.Match) -> str:
            word = match.group(0)
            # Skip if common normal word
            if word in ["VA", "BU", "SHU", "ENG"]:
                return word.lower()
            letters = []
            for ch in word:
                letters.append(UZBEK_LETTER_PHONEMES.get(ch, ch))
            return "-".join(letters)

        text = re.sub(r"\b[A-Z]{2,5}\b", spell_acronym, text)

        return text

    # --- STAGE 6: FOREIGN WORDS PHONETIZATION ---

    def replace_foreign_words(self, text: str) -> str:
        """Replace well-known foreign/IT words with their phonetic Uzbek spelling."""
        if not text or not self.foreign_words:
            return text

        for word, phonetic in self.foreign_words.items():
            pattern = rf"\b{re.escape(word)}\b"
            text = re.sub(pattern, phonetic, text, flags=re.IGNORECASE)

        return text

    # --- STAGE 7: PROSODY PREPARATION ---

    def prepare_prosody(self, text: str) -> str:
        """
        Structure text for natural pauses and terminal intonation.
        Breaks overly long sentences at clause boundaries.
        """
        if not text:
            return ""

        # Ensure sentence terminal punctuation
        text = text.strip()
        if text and not text[-1] in ".!?:":
            text += "."

        # Break very long sentences (> 200 chars) at punctuation or conjunctions
        paragraphs = text.split("\n")
        processed_paragraphs = []

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            sentences = re.split(r"(?<=[.!?])\s+", para)
            clean_sentences = []
            for sent in sentences:
                sent = sent.strip()
                if len(sent) > 220:
                    # Break at conjunctions or comma
                    parts = re.split(r"(?<=,)\s+", sent)
                    clean_sentences.append(" ".join(parts))
                else:
                    clean_sentences.append(sent)

            processed_paragraphs.append(" ".join(clean_sentences))

        return "\n\n".join(processed_paragraphs)

    # --- FULL PIPELINE ---

    def normalize(self, text: str) -> str:
        """
        Execute the full 7-stage normalization pipeline in strict deterministic order.
        """
        if not text or not text.strip():
            return ""

        # 1. Cleanup markdown, urls, emails, noisy characters
        t = self.clean_markdown_and_noise(text)

        # 2. Cyrillic to Latin transliteration
        t = self.transliterate_cyrillic(t)

        # 3. Foreign words phonetization
        t = self.replace_foreign_words(t)

        # 4. Numbers, currencies, dates, percentages to words
        t = self.normalize_numbers(t)

        # 5. Abbreviations and acronyms
        t = self.expand_abbreviations_and_acronyms(t)

        # 6. Apostrophes normalization
        t = self.normalize_apostrophes(t)

        # 7. Prosody preparation
        t = self.prepare_prosody(t)

        return t
