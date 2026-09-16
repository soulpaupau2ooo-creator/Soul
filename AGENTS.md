# 🏛️ Soulbekbot Loyiha Konstitutsiyasi (AGENTS.md)

## 📌 Loyiha Haqida
O'zbekiston talabalari uchun 30 ta OTM iqtisodiyot fani va 300 ta mavzu bo'yicha mustaqil ish yozib beruvchi, rasmiy statistika (stat.uz, cbu.uz) bilan boyituvchi va Microsoft Azure Speech AI neyron ovozlarida (Madina & Sardor) audio o'qib beruvchi professional Telegram bot (`@Soulbekbot`).

---

## ⚡ Bajaruvchi Agent Uchun Qat'iy Qoidalar (Hard Rules)

1. **🔴 MAJBURIY AVTO-PUSH (DOIMIY TALAB):**
   - **Har safar foydalanuvchi biror buyruq berganda yoki topshiriq bajarilganda, barcha o'zgarishlar DARHOL GitHub ga `git push origin main` qilinishi SHART!**
   - Git yo'li: `C:\Users\Azizbek\AppData\Local\Programs\Git\cmd\git.exe`
   - Ketma-ketlik:
     ```powershell
     & 'C:\Users\Azizbek\AppData\Local\Programs\Git\cmd\git.exe' add .
     & 'C:\Users\Azizbek\AppData\Local\Programs\Git\cmd\git.exe' commit -m "<aniq tavsif>"
     & 'C:\Users\Azizbek\AppData\Local\Programs\Git\cmd\git.exe' push origin main
     ```
   - Hech qachon o'zgarishlarni faqat lokalda qoldirib, xabar berib to'xtash mumkin emas. Push — har bir taskning yakuniy majburiy bosqichidir.

2. **🚫 ZERO LAZY CODE (0% Qisqartirish):**
   - Hech qanday `// TODO` yoki chala kodlar bo'lmasligi kerak.
   - 100% Strict Type Safety.

3. **🛡️ DEFENSIVE ARXITEKTURA:**
   - Hech qachon sirlarni (API kalitlar, GitHub tokenlar) gitga commit qilma.
   - Har bir yangi kod `py_compile` va `unittest` bilan tekshiriladi.
