import io
import logging
import asyncio
import random
from typing import Optional, Dict, Any, List

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("AcademicTools")

API_KEYS_STR = os.getenv("GEMINI_API_KEYS", "")
API_KEYS = [k.strip() for k in API_KEYS_STR.split(",") if k.strip()]

CANDIDATE_MODELS: List[str] = [
    'gemini-3.5-flash-lite',
    'gemini-flash-lite-latest',
    'gemini-3.6-flash',
    'gemini-flash-latest'
]

async def request_ai_fast(prompt: str) -> str:
    """Request AI using rotation and fast multi-model cascade."""
    if not API_KEYS:
        return "⚠️ Sun'iy Intellekt kalitlari ulanmagan."
    
    shuffled = list(API_KEYS)
    random.shuffle(shuffled)
    
    for attempt, key in enumerate(shuffled):
        try:
            genai.configure(api_key=key)
        except Exception:
            continue
            
        for model_name in CANDIDATE_MODELS:
            try:
                model = genai.GenerativeModel(model_name)
                resp = await asyncio.wait_for(
                    asyncio.to_thread(model.generate_content, prompt),
                    timeout=20.0
                )
                if resp and resp.text:
                    return resp.text
            except Exception as e:
                err_str = str(e).lower()
                if "429" in err_str or "quota" in err_str or "404" in err_str:
                    continue
                continue
                
    return "⚠️ Kechirasiz, tarmoqda vaqtinchalik bandlik. Birozdan so'ng qayta urinib ko'ring."

async def solve_economic_problem(problem_text: str, lang: str = "uz") -> str:
    prompt = (
        f"Foydalanuvchining iqtisodiy savoliga yoki masalasiga juda qisqa, oddiy, tushunarli va lo'nda javob ber.\n\n"
        f"Savol/Masala:\n{problem_text}\n\n"
        f"Qat'iy qoidalar:\n"
        f"1. Ortiqcha salomlashish, kirish yoki suv gaplar (masalan: 'Assalomu alaykum, ushbu fundamental masala...') QAT'IYAN YOZILMASIN. To'g'ridan-to'g'ri mohiyatdan boshla.\n"
        f"2. Qisqa va lo'nda bo'lsin (maksimum 4-8 ta gap).\n"
        f"3. Hech qanday yulduzcha (**), panjara (###) yoki qalin harf ishlatma! Faqat oddiy toza matn bo'lsin.\n"
        f"4. Til: {'O‘zbek tili (Lotin)' if lang == 'uz' else 'Русский язык' if lang == 'ru' else 'English'}."
    )
    return await request_ai_fast(prompt)

async def generate_teacher_questions(topic: str, lang: str = "uz") -> str:
    prompt = (
        f"Talabaning '{topic}' mavzusi bo'yicha o'qituvchi berishi mumkin bo'lgan 3 ta eng asosiy qiyin savolni va ularning qisqa, aniq namunali javoblarini yozib ber.\n\n"
        f"Qoidalar:\n"
        f"1. Kirish gaplarsiz to'g'ridan-to'g'ri 1, 2, 3 qilib savol va javoblarni ber.\n"
        f"2. Hech qanday maxsus belgilarsiz (yulduzcha, panjara) toza oddiy matn bo'lsin.\n"
        f"3. Til: {'O‘zbek tili (Lotin)' if lang == 'uz' else 'Русский язык' if lang == 'ru' else 'English'}."
    )
    return await request_ai_fast(prompt)

async def summarize_article(article_text: str, lang: str = "uz") -> str:
    prompt = (
        f"Quyidagi matnning eng asosiy 3-4 ta xulosasini qisqa va lo'nda qilib yozib ber:\n\n"
        f"{article_text[:5000]}\n\n"
        f"Qoidalar: Ortiqcha so'zlarsiz, faqat eng muhim fikrlar, oddiy toza matn (yulduzchasiz)."
    )
    return await request_ai_fast(prompt)

async def proofread_text(draft_text: str, lang: str = "uz") -> str:
    prompt = (
        f"Quyidagi matndagi imlo va grammatika xatolarini tuzatib, ravon va ilmiy qilib qayta yozib ber:\n\n"
        f"{draft_text[:5000]}\n\n"
        f"Hech qanday izohlarsiz, faqat to'g'rilangan toza matnni qaytar (yulduzcha va belgilarsiz)."
    )
    return await request_ai_fast(prompt)

def generate_economic_chart(chart_type: str = "supply_demand", title: str = "Bozor Muvozanati") -> bytes:
    """Generate high-resolution economic charts using matplotlib in memory."""
    fig, ax = plt.subplots(figsize=(8, 5), dpi=120)
    
    if chart_type == "supply_demand":
        Q = np.linspace(1, 10, 100)
        D = 12 - Q      # Demand
        S = 2 + Q       # Supply
        
        ax.plot(Q, D, label='Talab egri chizig\'i (Demand - D)', color='crimson', linewidth=2.5)
        ax.plot(Q, S, label='Taklif egri chizig\'i (Supply - S)', color='dodgerblue', linewidth=2.5)
        
        # Equilibrium point (Q=5, P=7)
        ax.scatter([5], [7], color='darkgreen', s=100, zorder=5)
        ax.axhline(7, color='gray', linestyle='--', alpha=0.6)
        ax.axvline(5, color='gray', linestyle='--', alpha=0.6)
        ax.text(5.2, 7.2, "Muvozanat nuqtasi (E)\nP*=7, Q*=5", color='darkgreen', fontweight='bold')
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('Mahsulot miqdori (Q)', fontsize=11)
        ax.set_ylabel('Narx (P)', fontsize=11)
        ax.set_xlim(0, 11)
        ax.set_ylim(0, 13)
        ax.grid(True, linestyle=':', alpha=0.5)
        ax.legend(loc='upper right', frameon=True)
        
    elif chart_type == "gdp_growth":
        years = ['2020', '2021', '2022', '2023', '2024', '2025 (prognoz)']
        gdp = [1.9, 7.4, 5.7, 6.0, 6.4, 6.2]
        bars = ax.bar(years, gdp, color='royalblue', width=0.5, edgecolor='navy')
        
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.15, f"{yval}%", ha='center', va='bottom', fontweight='bold')
            
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_ylabel('YaIM o\'sish sur\'ati (%)', fontsize=11)
        ax.set_ylim(0, 9)
        ax.grid(axis='y', linestyle=':', alpha=0.5)
        
    elif chart_type == "phillips":
        U = np.linspace(3, 10, 100)
        I = 15 / (U - 1)  # Inflation vs Unemployment
        ax.plot(U, I, color='purple', linewidth=2.5, label='Fillips egri chizig\'i (Phillips Curve)')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('Ishsizlik darajasi (Unemployment - u %)', fontsize=11)
        ax.set_ylabel('Inflyatsiya darajasi (Inflation - \u03c0 %)', fontsize=11)
        ax.grid(True, linestyle=':', alpha=0.5)
        ax.legend()
    else:
        # Default Bar Chart
        categories = ['Sanoat', 'Qishloq xo\'jaligi', 'Xizmatlar', 'Qurilish']
        shares = [30, 24, 38, 8]
        ax.pie(shares, labels=categories, autopct='%1.1f%%', colors=['#4CAF50', '#FF9800', '#2196F3', '#9C27B0'], startangle=140)
        ax.set_title(title, fontsize=14, fontweight='bold')

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return buf.read()
