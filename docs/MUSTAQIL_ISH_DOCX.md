# 📑 Mustaqil Ish Word (.docx) Tizimi va Sifat Darvozasi (Quality Gate)

Ushbu modul `soulbekbot` talabalari uchun O'zbekiston Respublikasi OTM davlat ta'lim standartiga to'liq mos keladigan professional Microsoft Word (.docx) mustaqil ish hujjatlarini shakllantiradi.

---

## 1. 📐 O'lchovlar va Tipografik Standartlar

| Parametr | OTM Standarti | Kodda Amalga Oshirilgan | Holat |
| :--- | :--- | :--- | :--- |
| **Qog'oz formati** | A4 (21.0 x 29.7 sm) | `Cm(21.0) x Cm(29.7)` | ✅ Tasdiqlangan |
| **Chap chegara (Left)** | 3.0 sm | `Cm(3.0)` | ✅ Tasdiqlangan |
| **O'ng chegara (Right)** | 1.5 sm | `Cm(1.5)` | ✅ Tasdiqlangan |
| **Yuqori chegara (Top)** | 2.0 sm | `Cm(2.0)` | ✅ Tasdiqlangan |
| **Pastki chegara (Bottom)** | 2.0 sm | `Cm(2.0)` | ✅ Tasdiqlangan |
| **Shrift nomi** | Times New Roman | `Times New Roman` | ✅ Tasdiqlangan |
| **Asosiy matn hajmi** | 14 pt | `Pt(14)` | ✅ Tasdiqlangan |
| **Sarlavha 1 hajmi** | 15 pt, Bold, Markazda | `Pt(15), Bold` | ✅ Tasdiqlangan |
| **Sarlavha 2 hajmi** | 14 pt, Bold, Chapda | `Pt(14), Bold` | ✅ Tasdiqlangan |
| **Qator oralig'i (Interval)** | 1.5 | `line_spacing = 1.5` | ✅ Tasdiqlangan |
| **Abzas chekinishi** | 1.25 sm | `first_line_indent = Cm(1.25)` | ✅ Tasdiqlangan |
| **Matn tekislash** | Ikki tomonlama (Justify) | `WD_ALIGN_PARAGRAPH.JUSTIFY` | ✅ Tasdiqlangan |
| **Mundarija (TOC)** | Avtomatik yangilanuvchi | Word XML Native TOC Field Code | ✅ Tasdiqlangan |
| **Sahifa raqamlash** | Pastki markazda | `PAGE` maydoni (Titul yashirilgan) | ✅ Tasdiqlangan |

---

## 2. 🏛️ Titul Varaq Tuzilishi

1. **Vazirlik va OTM nomi:** Bosh harflarda, markazda, 12-14 pt bold.
2. **Fakultet va Kafedra:** Markazda, 13 pt.
3. **MUSTAQIL ISH:** Sahifa o'rtasida, 18 pt bold.
4. **Fan va Mavzu:** Markazda, mavzu qo'shtirnoqda, 15 pt bold.
5. **Talaba va O'qituvchi Bloki:** O'ng tomonga tekislangan, guruh va F.I.Sh.
6. **Shahar va Yil:** Sahifa pastki markazida (Toshkent – 2026).
7. **Titul varaqdan so'ng majburiy Page Break.**

---

## 3. 📱 Telegram Orqali Yuborish (Kompyuter va Telefon)

- **Telegram usuli:** `sendDocument` (`answer_document`).
- **MIME turi:** `application/vnd.openxmlformats-officedocument.wordprocessingml.document`.
- **Fayl nomi:** `{mavzu}_OTM_standart.docx`.
- **Moslik:**
  - 💻 **Kompyuterda:** Microsoft Word, LibreOffice, WPS Office da 1 bosish bilan to'g'ri ochiladi.
  - 📱 **Telefonda (iOS / Android):** Telegram ichidagi hujjat ko'ruvchi yoki o'rnatilgan Word/WPS/Google Docs ilovalari orqali xatosiz ochiladi va chop etishga tayyor.

---

## 4. ⚙️ Foydalanuvchi Profili Boshqaruvi (`/malumotlarim`)

Foydalanuvchi botda `/malumotlarim` buyrug'i orqali o'zining:
- O'qiydigan universiteti
- Fakulteti va kafedrasi
- Guruh raqami
- F.I.Sh
- O'qituvchisi
ma'lumotlarini bir marta kiritib qo'yadi. Bot bu ma'lumotlarni bazada eslab qoladi va har bir mustaqil ishning titul varag'iga avtomatik joylaydi!
