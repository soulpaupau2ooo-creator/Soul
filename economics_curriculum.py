# ==============================================================================
# 📚 O'ZBEKISTON IQTISODIYOT FANLARI VA DOLZARB MAVZULAR ENSIKLOPEDIYASI
# ==============================================================================
# Barcha Oliy Ta'lim Muassasalari (TDIU, Moliya Instituti, JIDU, O'zMU)
# bakalavriat va magistratura o'quv dasturlari asosida tuzilgan to'liq baza.
# 30 ta asosiy iqtisodiyot fani va 300 ta saralangan dolzarb mustaqil ish mavzulari.
# ==============================================================================

from typing import Dict, Any, List, Optional

# 5 ta asosiy fakultet / yo'nalish
CATEGORIES: Dict[str, Dict[str, Any]] = {
    "nazariy": {
        "title": "🏛 1. Nazariy va Umumiy Iqtisodiyot",
        "description": "Fundamental iqtisodiy nazariyalar, makro va mikro tahlil, ekonometrika va modellashtirish.",
        "subjects": {
            "iqt_nazariya": "Iqtisodiyot nazariyasi",
            "makro": "Makroiqtisodiyot",
            "mikro": "Mikroiqtisodiyot",
            "talimotlar": "Iqtisodiy ta'limotlar tarixi",
            "ekonometrika": "Ekonometrika va modellashtirish",
            "statistika": "Ijtimoiy-iqtisodiy statistika"
        }
    },
    "moliya": {
        "title": "💰 2. Moliya, Bank va Soliq Tizimi",
        "description": "Korxona va davlat moliyasi, bank tizimi, soliq qonunchiligi, audit va qimmatli qog'ozlar.",
        "subjects": {
            "moliya": "Moliya va moliyaviy tahlil",
            "bank": "Bank ishi va kredit tizimi",
            "buxgalteriya": "Buxgalteriya hisobi va audit",
            "soliq": "Soliqlar va soliqqa tortish",
            "qimmatli_qogoz": "Qimmatli qog'ozlar va fond birjasi",
            "davlat_moliyasi": "Davlat byudjeti va g'aznachilik"
        }
    },
    "biznes": {
        "title": "🏢 3. Biznes, Menejment va Marketing",
        "description": "Kompaniyalarni strategik boshqarish, marketing strategiyalari, startaplar va HR menejment.",
        "subjects": {
            "menejment": "Menejment va strategik boshqaruv",
            "marketing": "Marketing va bozor tadqiqotlari",
            "tadbirkorlik": "Kichik biznes va tadbirkorlik",
            "korporativ": "Korporativ boshqaruv",
            "hr": "Inson resurslarini boshqarish (HR)",
            "loyihalar": "Biznes-reja va loyiha boshqaruvi"
        }
    },
    "tarmoq": {
        "title": "🌾 4. Tarmoqlar va Sanoat Iqtisodiyoti",
        "description": "Sanoat, agrar soha, transport logistikasi, mintaqaviy klasterlar va turizm iqtisodiyoti.",
        "subjects": {
            "sanoat": "Sanoat korxonalari iqtisodiyoti",
            "agrar": "Agrar iqtisodiyot va agrobiznes",
            "logistika": "Transport va logistika iqtisodiyoti",
            "mintaqaviy": "Mintaqaviy iqtisodiyot va klasterlar",
            "turizm": "Turizm va servis iqtisodiyoti",
            "yashil": "Yashil iqtisodiyot va ekologiya"
        }
    },
    "raqamli": {
        "title": "🌐 5. Raqamli Iqtisodiyot va Tashqi Iqtisodiyot",
        "description": "Axborot texnologiyalari, xalqaro savdo, FinTech, bojxona va milliy iqtisodiy xavfsizlik.",
        "subjects": {
            "raqamli_iqtisod": "Raqamli iqtisodiyot va IT",
            "xalqaro": "Xalqaro savdo va jahon iqtisodiyoti",
            "iqtisodiy_xavfsizlik": "Milliy iqtisodiy xavfsizlik",
            "fintech": "Moliyaviy texnologiyalar (FinTech)",
            "bojxona": "Bojxona ishi va tariflar",
            "jahon": "Jahon xo'jaligi va integratsiya"
        }
    }
}

# 30 ta fan va ularning 10 tadan rasmiy OTM dolzarb mavzulari (Jami 300 ta mavzu)
KNOWLEDGE_BASE: Dict[str, Dict[str, Any]] = {
    # 🏛 1. Nazariy va Umumiy Iqtisodiyot
    "iqt_nazariya": {
        "title": "Iqtisodiyot nazariyasi",
        "category": "nazariy",
        "topics": [
            "Bozor iqtisodiyoti mexanizmi va uning amal qilish tamoyillari",
            "Iqtisodiy tizimlar va ularning rivojlanish qonuniyatlari",
            "Mulkchilik munosabatlari va O'zbekistonda xususiylashtirish jarayoni",
            "Ishlab chiqarish omillari va ulardan samarali foydalanish yo'llari",
            "Iqtisodiy o'sish modellari va unga ta'sir etuvchi omillar",
            "Raqobat va monopoliya: bozor tuzilmalari va davlat antimonopol siyosati",
            "Talab va taklif qonuni hamda bozor muvozanatining shakllanishi",
            "Milliy boylik va uning mamlakat iqtisodiyotidagi o'rni",
            "Aholi daromadlari va ijtimoiy tabaqalanish muammolari",
            "Bozor infratuzilmasining iqtisodiyotdagi ahamiyati"
        ]
    },
    "makro": {
        "title": "Makroiqtisodiyot",
        "category": "nazariy",
        "topics": [
            "Yalpi ichki mahsulot (YaIM) va uni hisoblash usullari tahlili",
            "Inflyatsiya jarayonlari: kelib chiqish sabablari va unga qarshi choralar",
            "O'zbekistonda ishsizlik darajasi va aholi bandligini ta'minlash siyosati",
            "Makroiqtisodiy muvozanat (AD-AS modeli) va uning barqarorligi",
            "Davlatning monetar (pul-kredit) siyosati va uning samaradorligi",
            "Fiskal (soliq-byudjet) siyosati va davlat byudjeti taqchilligi",
            "Fillips egri chizig'i: inflyatsiya va ishsizlik o'rtasidagi bog'liqlik",
            "IS-LM modeli orqali tovar va pul bozorlari muvozanatini tahlil qilish",
            "Iqtisodiy sikllar va inqirozlarga qarshi davlat makroiqtisodiy siyosati",
            "O'zbekistonning to'lov balansi va milliy valyuta kursi barqarorligi"
        ]
    },
    "mikro": {
        "title": "Mikroiqtisodiyot",
        "category": "nazariy",
        "topics": [
            "Iste'molchi xulq-atvori va naflilik nazariyasi (kardinal va ordinal)",
            "Talab va taklifning narx bo'yicha elastikligi va uning amaliy ahamiyati",
            "Ishlab chiqarish funksiyasi (Kobb-Duglas) va miqyos samaradorligi",
            "Korxonaning qisqa va uzoq muddatli xarajatlar tahlili",
            "Mukammal raqobat bozorida firmaning daromad maksimallashtirish strategiyasi",
            "Sof monopoliya va monopoliyaga qarshi narx tartibga solish",
            "Oligopoliya bozorida strategik harakatlar (Kurno va Bertran modellari)",
            "Monopolistik raqobat va mahsulot differensiatsiyasi",
            "Ishlab chiqarish omillari bozorlari (mehnat, kapital, yer)",
            "Tashqi ta'sirlar (eksternaliyalar) va jamoat tovarlari muammosi"
        ]
    },
    "talimotlar": {
        "title": "Iqtisodiy ta'limotlar tarixi",
        "category": "nazariy",
        "topics": [
            "Merkantilizm va fiziokratlar maktabining iqtisodiy qarashlari",
            "Klassik siyosiy iqtisod maktabi (Adam Smit va David Rikardo ta'limotlari)",
            "Marksistik iqtisodiy ta'limot va qo'shimcha qiymat nazariyasi",
            "Marjinalizm inqilobi va Avstriya iqtisodiy maktabi (Menjer, Böm-Baverk)",
            "Jon Meynard Keyns va keynschilik maktabining inqirozga qarshi ta'limoti",
            "Neoklassik sintez va zamonaviy iqtisodiy nazariyalar",
            "Monetarizm maktabi (Milton Fridmen) va pul nazariyasi",
            "Institutsionalizm va yangi institutsional iqtisodiyot (R.Kouz, D.Nort)",
            "Shumpeterning innovatsiyalar va tadbirkorlik nazariyasi",
            "Sharq mutafakkirlarining (Forobiy, Ibn Sino, Navoiy) iqtisodiy g'oyalari"
        ]
    },
    "ekonometrika": {
        "title": "Ekonometrika va modellashtirish",
        "category": "nazariy",
        "topics": [
            "Bir omilli chiziqli regressiya modeli va eng kichik kvadratlar usuli (OLS)",
            "Ko'p omilli regressiya tahlili va koeffitsiyentlar statistik ahamiyati (t, F)",
            "Multikollinearlik muammosi va uni bartaraf etish usullari",
            "Geteroskedastiklik: aniqlash testlari (White, Goldfeld-Quandt) va yechimlar",
            "Avtokorrelyatsiya hodisasi (Darbin-Uotson mezoni) va tuzatish choralari",
            "Vaqt qatorlari tahlili va statsionarlik (ADF testi, ARIMA modellari)",
            "Soxta (dummy) o'zgaruvchilardan iqtisodiy modellarda foydalanish",
            "Iqtisodiy jarayonlarni modellashtirishda panel ma'lumotlaridan foydalanish",
            "O'zbekiston YaIM o'sishini ekonometrik bashorat qilish modeli",
            "Iste'mol xarajatlarining daromadlarga bog'liqligini ekonometrik baholash"
        ]
    },
    "statistika": {
        "title": "Ijtimoiy-iqtisodiy statistika",
        "category": "nazariy",
        "topics": [
            "Statistik kuzatish usullari va tanlanma ma'lumotlarni umumlashtirish",
            "O'rtacha miqdorlar (arifmetik, geometrik, moda, mediana) va dispersiya",
            "Iqtisodiy indekslar nazariyasi (Laspeyres, Paashe, Fisher indekslari)",
            "Aholi dinamikasi va demografik jarayonlar statistik tahlili",
            "Mehnat bozori va ishchi kuchi statistikasi ko'rsatkichlari",
            "Milliy hisoblar tizimi (MHT) va uning asosiy makroiqtisodiy agregatlari",
            "Tashqi savdo statistikasi va eksport-import ko'rsatkichlari dinamikasi",
            "Korxonalarning moliyaviy holati va rentabellik darajasi statistikasi",
            "Inflyatsiya darajasini (iste'mol narxlari indeksi - CPI) hisoblash metodologiyasi",
            "Aholi turmush darajasi va qashshoqlikni baholash statistik ko'rsatkichlari"
        ]
    },

    # 💰 2. Moliya, Bank va Soliq Tizimi
    "moliya": {
        "title": "Moliya va moliyaviy tahlil",
        "category": "moliya",
        "topics": [
            "Korxona moliyaviy resurslari va ularni boshqarish strategiyasi",
            "Korxonaning moliyaviy barqarorligi va to'lov qobiliyatini baholash",
            "Aylanma mablag'lar aylanish tezligi va ulardan samarali foydalanish",
            "Korxonaning moliyaviy natijalari (foyda va rentabellik) tahlili",
            "Investitsion loyihalarning moliyaviy samaradorligini baholash (NPV, IRR, PI)",
            "Moliyaviy menejmentda leverej (operatsion va moliyaviy leverej) tahlili",
            "Dividend siyosati va aksiyadorlar manfaatlarini ta'minlash",
            "Korxonada inqirozga qarshi moliyaviy boshqaruv va bankrotlik xavfini baholash",
            "Xalqaro moliyaviy hisobot standartlari (XMHS/IFRS) ga o'tish amaliyoti",
            "Moliyaviy risklarni boshqarish va xedjirlash operatsiyalari"
        ]
    },
    "bank": {
        "title": "Bank ishi va kredit tizimi",
        "category": "moliya",
        "topics": [
            "O'zbekiston Respublikasi Markaziy bankining monetar siyosati va vositalari",
            "Tijorat banklarining aktiv operatsiyalari va kredit portfeli tahlili",
            "Bank depozit siyosati va aholi omonatlarini jalb qilish strategiyasi",
            "Tijorat banklarida kredit riskini boshqarish va muammoli kreditlar (NPL) bilan ishlash",
            "Raqamli banking va bank xizmatlarini transformatsiya qilish istiqbollari",
            "Bank tizimida likvidlik va to'lov qobiliyatini ta'minlash (Bazel III standartlari)",
            "Kichik biznes va tadbirkorlikni banklar orqali imtiyozli kreditlash",
            "Ipoteka kreditlash tizimi va uning uy-joy bozoridagi o'rni",
            "Islomiy bank ishi (Halol banking) va uni O'zbekistonda joriy etish imkoniyatlari",
            "Banklararo to'lov tizimlari va xalqaro to'lov tizimlari (SWIFT) integratsiyasi"
        ]
    },
    "buxgalteriya": {
        "title": "Buxgalteriya hisobi va audit",
        "category": "moliya",
        "topics": [
            "Buxgalteriya hisobining milliy standartlari (BHMS) va ularning XMHS bilan uyg'unlashuvi",
            "Buxgalteriya balansi tuzilishi va xo'jalik operatsiyalarining ta'siri",
            "Asosiy vositalar hisobi, eskirishi va amortizatsiya hisoblash usullari",
            "Ishlab chiqarish xarajatlari hisobi va mahsulot tannarxini kalkulyatsiya qilish",
            "Xodimlar mehnatiga haq to'lash hisobi va ushlab qolishlar mexanizmi",
            "Tayyor mahsulotlarni sotish va moliyaviy natijalarni hisobga olish",
            "Ichki audit tizimi va korxonada moliyaviy nazoratni tashkil etish",
            "Tashqi audit va auditorlik xulosasining moliyaviy hisobotdagi ahamiyati",
            "Soliq hisobi va buxgalteriya hisobi o'rtasidagi tafovutlar tahlili",
            "Elektron hisob-kitoblar va 1C buxgalteriya tizimini raqamlashtirish"
        ]
    },
    "soliq": {
        "title": "Soliqlar va soliqqa tortish",
        "category": "moliya",
        "topics": [
            "O'zbekiston Respublikasi Soliq kodeksining mazmun-mohiyati va islohotlar",
            "Qo'shilgan qiymat solig'i (QQS) mexanizmi va uning byudjetdagi ulushi",
            "Yuridik shaxslardan olinadigan foyda solig'i va amortizatsiya imtiyozlari",
            "Jismoniy shaxslardan olinadigan daromad solig'i (JSHODS) va uning ijtimoiy roli",
            "Aylanmadan olinadigan soliq va kichik biznesga berilgan yengilliklar",
            "Mol-mulk va yer soliqlari ma'muriyatchiligini takomillashtirish",
            "Soliq yukini baholash va uni kamaytirish orqali tadbirkorlikni rag'batlantirish",
            "Yashirin iqtisodiyotni qisqartirishda zamonaviy soliq nazorati (E-ijara, E-ombor)",
            "Xalqaro soliqqa tortish va ikki yoqlama soliqqa tortishning oldini olish",
            "Elektron soliq xizmatlari va soliq ma'muriyatchiligini raqamlashtirish"
        ]
    },
    "qimmatli_qogoz": {
        "title": "Qimmatli qog'ozlar va fond birjasi",
        "category": "moliya",
        "topics": [
            "O'zbekiston fond bozori ('Toshkent' RFB) faoliyati va uning rivojlanish bosqichlari",
            "Aksiyalar bozori va aksiyadorlik jamiyatlarida dividendlarni to'lash mexanizmi",
            "Korporativ va davlat obligatsiyalari: daromadlilik va investitsion jozibadorlik",
            "IPO va SPO jarayonlari orqali korxonalarga xalqaro sarmoyalarni jalb qilish",
            "Investitsion fondlar (PIF) va ularning moliya bozoridagi roli",
            "Qimmatli qog'ozlar portfeli nazariyasi (Markovis modeli va CAPM)",
            "Fond bozorida derivativlar (fyucherslar va opsionlar) bilan risklarni boshqarish",
            "Xalqaro suveren yevroobligatsiyalar chiqarish tajribasi",
            "Kriptoaktivlar va raqamli tokenlar aylanmasining qonuniy tartibga solinishi",
            "Boshlang'ich va ikkilamchi qimmatli qog'ozlar bozorida brokerlik faoliyati"
        ]
    },
    "davlat_moliyasi": {
        "title": "Davlat byudjeti va g'aznachilik",
        "category": "moliya",
        "topics": [
            "Davlat byudjeti daromadlar bazasini shakllantirish va soliq tushumlari tahlili",
            "Davlat xarajatlarining ijtimoiy yo'naltirilganligi (ta'lim, sog'liqni saqlash)",
            "Byudjet taqchilligi (defitsiti) va uni qoplash manbalari tahlili",
            "Davlat tashqi va ichki qarzini boshqarish strategiyasi",
            "G'aznachilik ijrosi tizimi va byudjet mablag'laridan maqsadli foydalanish",
            "Tashabbusli byudjet ('Open Budget') loyihasi va fuqarolik ishtiroki",
            "Davlat maqsadli jamg'armalari (Pensiya, Yo'l jamg'armasi) faoliyati",
            "Davlat xaridlari tizimi ('xarid.uz') va ochiqlik tamoyillari",
            "Mahalliy byudjetlar mustaqilligini oshirish va hududiy moliyalashtirish",
            "O'rta muddatli byudjetlashtirish tizimini joriy etish istiqbollari"
        ]
    },

    # 🏢 3. Biznes, Menejment va Marketing
    "menejment": {
        "title": "Menejment va strategik boshqaruv",
        "category": "biznes",
        "topics": [
            "Menejmentning asosiy funksiyalari (rejalashtirish, tashkil etish, motivatsiya, nazorat)",
            "Korxonaning strategik menejmenti: missiya, maqsad va SWOT tahlil",
            "Boshqaruv qarorlarini qabul qilish metodologiyasi va risklarni hisobga olish",
            "Liderlik uslublari va jamoani samarali boshqarish san'ati",
            "Tashkiliy tuzilmalar turlari (chiziqli, funksional, matritsali) va ularni optimallashtirish",
            "Korxonada o'zgarishlar menejmenti (Change Management) va qarshiliklarni yengish",
            "Zamonaviy yapon boshqaruv tajribasi (Kaizen, Kanban, Lean ishlab chiqarish)",
            "Vaqtni boshqarish (Time management) va rahbar mehnati unumdorligi",
            "Korxona samaradorligini baholashning zamonaviy ko'rsatkichlari (KPI va OKR)",
            "Biznesda inqirozga qarshi boshqaruv (Anti-crisis management) choralari"
        ]
    },
    "marketing": {
        "title": "Marketing va bozor tadqiqotlari",
        "category": "biznes",
        "topics": [
            "Marketing konsepsiyalari evolyutsiyasi va mijozga yo'naltirilganlik",
            "Marketing majmuasi (4P / 7P) va uning korxona strategiyasidagi o'rni",
            "Bozorni segmentatsiyalash, maqsadli auditoriyani tanlash va pozitsionirlash (STP)",
            "Iste'molchi xulq-atvori va xarid qilish to'g'risida qaror qabul qilish jarayoni",
            "Brending strategiyasi: brend kapitali va iste'molchi sodiqligini shakllantirish",
            "Raqamli marketing (Digital Marketing), SMM va kontekstli reklama vositalari",
            "Narxni shakllantirish strategiyalari (Skimming, Penetration, Psixologik narx)",
            "Yangi mahsulotni yaratish va bozorga chiqarish bosqichlari (Product Life Cycle)",
            "Bozor tadqiqotlari metodologiyasi (so'rovnomalar, fokus-guruhlar, tahlillar)",
            "B2B va B2C marketingining o'zaro farqlari va xususiyatlari"
        ]
    },
    "tadbirkorlik": {
        "title": "Kichik biznes va tadbirkorlik",
        "category": "biznes",
        "topics": [
            "Kichik tadbirkorlik subyektlarini tashkil etish va ro'yxatdan o'tkazish tartibi",
            "Biznes g'oyani shakllantirish va investitsion biznes-reja ishlab chiqish",
            "O'zbekistonda kichik biznesni davlat tomonidan qo'llab-quvvatlash tizimi",
            "Startap loyihalarni shakllantirish va venchur fondlardan sarmoya jalb qilish",
            "Franchayzing tizimi va uning tayyor biznes model sifatidagi afzalliklari",
            "Tadbirkorlikda moliyaviy xatarlar (risklar) va ularni minimallashtirish",
            "Oilaviy tadbirkorlik va hunarmandchilikni rivojlantirish imtiyozlari",
            "Ayollar va yoshlar tadbirkorligini moliyalashtirish mexanizmlari",
            "Kichik biznesda elektron tijoratdan foydalanish va savdo maydonchalari",
            "Kichik korxonalarda mahsulot sifatini ta'minlash va ISO standartlari"
        ]
    },
    "korporativ": {
        "title": "Korporativ boshqaruv",
        "category": "biznes",
        "topics": [
            "Aksiyadorlik jamiyatlarida korporativ boshqaruvning milliy va xalqaro modellari",
            "Kuzatuv kengashining korporativ nazoratdagi vakolatlari va mas'uliyati",
            "Ijroiya organi faoliyati va boshqaruv xarajatlarini nazorat qilish",
            "Manfaatdor tomonlar (Stakeholders) nazariyasi va aksiyadorlar huquqlarini himoya qilish",
            "Korporativ ziddiyatlar (mojarolar) va ularni hal etish mexanizmlari",
            "Korporativ ijtimoiy mas'uliyat (CSR) va kompaniya obro'si (reputatsiyasi)",
            "ESG (Environmental, Social, Governance) standartlarini joriy etish tajribasi",
            "Kompaniyalarni qo'shib olish va yutib yuborish (M&A) bitimlari tahlili",
            "Korporativ etika kodeksi va korrupsiyaga qarshi komplaens-nazorat",
            "Davlat ishtirokidagi korxonalarni xususiylashtirish va korporativ transformatsiya"
        ]
    },
    "hr": {
        "title": "Inson resurslarini boshqarish (HR)",
        "category": "biznes",
        "topics": [
            "Inson kapitali nazariyasi va uning zamonaviy korxonalardagi qimmati",
            "Kadrlarni rejalashtirish, tanlash va yollash (Recruitment & Selection)",
            "Xodimlarni motivatsiyalashning moddiy va nomoddiy usullari",
            "Xodimlar malakasini oshirish va korporativ o'qitish tizimi (T&D)",
            "Mehnat unumdorligini baholash va KPI asosida rag'batlantirish tizimi",
            "Korporativ madaniyatni shakllantirish va xodimlar sodiqligini oshirish",
            "Mehnat nizolari va ularni hal qilishning huquqiy-iqtisodiy asoslari",
            "Masofaviy ish (Remote work) va gibrid ish rejimini boshqarish xususiyatlari",
            "Xodimlarning emotsional charchashi (Burnout) va stress-menejment",
            "HR-analitika va inson resurslarini raqamli boshqarish dasturlari"
        ]
    },
    "loyihalar": {
        "title": "Biznes-reja va loyiha boshqaruvi",
        "category": "biznes",
        "topics": [
            "Investitsiya loyihalarini ishlab chiqish va biznes-reja tuzish metodikasi",
            "Loyihaning hayotiy sikli va bosqichlari (PMBOK standartlari asosida)",
            "Loyihaning moliyaviy-iqtisodiy asosnomasi (Texnik-iqtisodiy asosnoma - TIA)",
            "Agile va Scrum metodologiyalari yordamida loyihalarni boshqarish",
            "Loyiha byudjetini rejalashtirish va xarajatlarni nazorat qilish usullari",
            "Loyihaning vaqt me'yorlarini belgilash (Gantt diagrammasi va kritik yo'l usuli)",
            "Loyiha risklarini aniqlash, tahlil qilish va yumshatish choralari",
            "Loyiha jamoasini shakllantirish va manfaatdor tomonlar bilan aloqalar",
            "Davlat-xususiy sheriklik (DXSH / PPP) loyihalarini boshqarish xususiyatlari",
            "Loyihani yakunlash, natijalarni baholash va auditdan o'tkazish"
        ]
    },

    # 🌾 4. Tarmoqlar va Sanoat Iqtisodiyoti
    "sanoat": {
        "title": "Sanoat korxonalari iqtisodiyoti",
        "category": "tarmoq",
        "topics": [
            "O'zbekistonda sanoatlashuv jarayoni va ishlab chiqarish tarkibiy o'zgarishlari",
            "Sanoat korxonasida ishlab chiqarish quvvatlarini hisoblash va ulardan foydalanish",
            "Mahsulot tannarxini pasaytirish va xomashyo-energiya tejamkorligi yo'llari",
            "Og'ir sanoat (metallurgiya, neft-gaz, kimyo) korxonalari iqtisodiyoti",
            "To'qimachilik va yengil sanoat klasterlarining eksport salohiyati",
            "Mashinasozlik va avtomobilsozlik sanoatida lokalizatsiya dasturlari",
            "Sanoatda asosiy fondlarning yangilanish darajasi va modernizatsiya",
            "Sanoat korxonalari o'rtasida kooperatsiya aloqalari va autsorsing",
            "Maxsus iqtisodiy zonalar (MIZ) va kichik sanoat zonalarining sanoatdagi o'rni",
            "Sanoatda mehnat unumdorligini oshirish va xalqaro standartlarni joriy etish"
        ]
    },
    "agrar": {
        "title": "Agrar iqtisodiyot va agrobiznes",
        "category": "tarmoq",
        "topics": [
            "Qishloq xo'jaligida fermer, dehqon xo'jaliklari va tomorqa yer egalari faoliyati",
            "Agrar sohada zamonaviy paxta-to'qimachilik va g'allachilik klasterlari",
            "Suv resurslaridan tejamkor foydalanish (tomchilatib sug'orish) iqtisodiyoti",
            "Meva-sabzavot mahsulotlarini qayta ishlash va eksport salohiyatini oshirish",
            "Chorvachilik, parrandachilik va baliqchilik sohalarida rentabellik tahlili",
            "Oziq-ovqat xavfsizligini ta'minlashda agrar sohaning strategik roli",
            "Qishloq xo'jaligini davlat tomonidan subsidiyalash va imtiyozli kreditlash",
            "Agrar sohada yer munosabatlari va yer ijara huquqlarini bozorga kiritish",
            "Zamonaviy issiqxona xo'jaliklari (gidroponika) iqtisodiy samaradorligi",
            "Agrosug'urta mexanizmlari va tabiiy ofatlar oqibatlarini minimallashtirish"
        ]
    },
    "logistika": {
        "title": "Transport va logistika iqtisodiyoti",
        "category": "tarmoq",
        "topics": [
            "O'zbekistonning transport-tranzit salohiyati va xalqaro transport koridorlari",
            "Temir yo'l transporti iqtisodiyoti va yuk tashish tarif siyosati",
            "Avtomobil transporti sohasida xalqaro yuk tashuvlar (TIR) rentabelligi",
            "Havo transporti (aviatsiya) iqtisodiyoti va 'Ochiq osmon' rejimi afzalliklari",
            "Ta'minot zanjirini boshqarish (Supply Chain Management - SCM) tamoyillari",
            "Ombor logistikasi: tovar zaxiralarini boshqarish va optimallashtirish",
            "Multimodal (aralash) tashuvlar va logistika markazlari infratuzilmasi",
            "Xitoy-Qirg'iziston-O'zbekiston temir yo'li loyihasining iqtisodiy samaradorligi",
            "Logistika xarajatlarini pasaytirish orqali eksport mahsulotlari raqobatbardoshligini oshirish",
            "Yashil logistika (Green Logistics) va transportning atrof-muhitga ta'siri"
        ]
    },
    "mintaqaviy": {
        "title": "Mintaqaviy iqtisodiyot va klasterlar",
        "category": "tarmoq",
        "topics": [
            "Hududlarning ijtimoiy-iqtisodiy salohiyatini baholash va tabaqalanish muammolari",
            "Mintaqaviy sanoat klasterlari va ularning hududiy rivojlanishdagi o'rni",
            "Erkin iqtisodiy zonalar (Navoiy, Jizzax, Angren) faoliyati samaradorligi",
            "Hududlarga to'g'ridan-to'g'ri xorijiy investitsiyalarni jalb qilish geografiyasi",
            "Urbanizatsiya jarayonlari va yirik shaharlar agglomeratsiyasi iqtisodiyoti",
            "Qishloq joylarni kompleks rivojlantirish ('Obod qishloq' va 'Obod mahalla')",
            "Mintaqalararo iqtisodiy integratsiya va tovar ayirboshlash munosabatlari",
            "Depressiv (iqtisodiy orqada qolgan) tumanlarni ijtimoiy-iqtisodiy qo'llab-quvvatlash",
            "Hududlarda 'O'sish nuqtalari' (Drayver sohalar) ni aniqlash metodikasi",
            "Mintaqaviy mehnat resurslaridan oqilona foydalanish va ichki migratsiya"
        ]
    },
    "turizm": {
        "title": "Turizm va servis iqtisodiyoti",
        "category": "tarmoq",
        "topics": [
            "O'zbekistonning turizm salohiyati va jahon turizm bozoridagi o'rni",
            "Tarixiy va madaniy turizm (Samarqand, Buxoro, Xiva) infratuzilmasi",
            "Ziyorat turizmini rivojlantirish va Islom olami turistlarini jalb qilish",
            "Mehmonxona xo'jaligi iqtisodiyoti: xona fondi to'lish darajasi va daromadlilik",
            "Ekoturizm, agroturizm va tog' turizmining iqtisodiy istiqbollari",
            "Servis va xizmat ko'rsatish sohasining YaIMdagi ulushini oshirish yo'llari",
            "Turizm sohasiga xorijiy investitsiyalarni jalb qilish va soliq imtiyozlari",
            "Turizmda transport va aviachiptalar narxining raqobatbardoshligi tahlili",
            "O'zbekiston milliy turizm brendi va xalqaro PR targ'ibot strategiyasi",
            "Restoran va umumiy ovqatlanish korxonalari iqtisodiy samaradorligi"
        ]
    },
    "yashil": {
        "title": "Yashil iqtisodiyot va ekologiya",
        "category": "tarmoq",
        "topics": [
            "O'zbekistonning 2030 yilgacha Yashil iqtisodiyotga o'tish strategiyasi",
            "Qayta tiklanuvchi energiya manbalari (Quyosh va Shamol stansiyalari) iqtisodiyoti",
            "Energiya samaradorligi va sanoatda uglerod izini (CO2) kamaytirish yo'llari",
            "Yashil obligatsiyalar (Green Bonds) orqali ekologik loyihalarni moliyalashtirish",
            "Orol dengizi havzasida ekologik inqirozni yumshatishning iqtisodiy choralari",
            "Sirkulyar iqtisodiyot (Circular Economy) va chiqindilarni qayta ishlash rentabelligi",
            "Ekologik soliqlar va tabiatdan foydalanganlik uchun to'lovlar mexanizmi",
            "Yashil transport (elektromobillar va jamoat transporti) infratuzilmasi",
            "Qishloq xo'jaligida iqlim o'zgarishiga moslashuvchan agrotexnologiyalar",
            "Xalqaro yashil iqlim fondlari (GCF) grantlarini jalb qilish imkoniyatlari"
        ]
    },

    # 🌐 5. Raqamli Iqtisodiyot va Tashqi Iqtisodiyot
    "raqamli_iqtisod": {
        "title": "Raqamli iqtisodiyot va IT",
        "category": "raqamli",
        "topics": [
            "'Raqamli O'zbekiston - 2030' strategiyasi va uning amalga oshirilish bosqichlari",
            "Elektron tijorat (E-commerce) bozori rivojlanishi va qonuniy asoslari",
            "Sun'iy intellekt (AI) texnologiyalarining sohalar unumdorligiga ta'siri",
            "Katta ma'lumotlar (Big Data) va ulardan iqtisodiy tahlillarda foydalanish",
            "IT Park faoliyati va O'zbekistonning IT autsorsing (BPO) xabiga aylanishi",
            "Davlat xizmatlarini raqamlashtirish (my.gov.uz) orqali byurokratiyani kamaytirish",
            "Bulutli texnologiyalar (Cloud Computing) va korxona xarajatlarini tejash",
            "Kiberxavfsizlik va raqamli iqtisodiyotda ma'lumotlar maxfiyligini saqlash",
            "Blokcheyn texnologiyasi va uning iqtisodiyotning turli jabhalarida qo'llanilishi",
            "Raqamli savdo platformalari (Marketplace) ning kichik biznesga ta'siri"
        ]
    },
    "xalqaro": {
        "title": "Xalqaro savdo va jahon iqtisodiyoti",
        "category": "raqamli",
        "topics": [
            "O'zbekistonning Jahon Savdo Tashkilotiga (JST / WTO) a'zo bo'lish jarayoni va oqibatlari",
            "Xalqaro savdo nazariyalari (absolyut va qiyosiy ustunliklar nazariyasi)",
            "Tashqi savdo balansi tahlili: eksport tarkibini diversifikatsiya qilish yo'llari",
            "Proteksionizm va erkin savdo (Free trade) siyosatlarining ijobiy va salbiy tomonlari",
            "Xalqaro savdoda notarif to'siqlar (kvotalar, litsenziyalar, texnik standartlar)",
            "Yevropa Ittifoqining GSP+ preferensiyalar tizimidan foydalanish samaradorligi",
            "Markaziy Osiyo davlatlari o'rtasida mintaqaviy savdo-iqtisodiy integratsiya",
            "Global qiymat zanjirlari (Global Value Chains) va unga milliy korxonalarning qo'shilishi",
            "Xalqaro investitsiyalar oqimi va transmilliy korporatsiyalar (TMK) strategiyasi",
            "Xalqaro iqtisodiy sanksiyalar va ularning jahon ta'minot zanjirlariga ta'siri"
        ]
    },
    "iqtisodiy_xavfsizlik": {
        "title": "Milliy iqtisodiy xavfsizlik",
        "category": "raqamli",
        "topics": [
            "Milliy iqtisodiy xavfsizlikning mezonlari, chegaraviy (porog) ko'rsatkichlari",
            "Oziq-ovqat xavfsizligi va mamlakatning oziq-ovqat mustaqilligini ta'minlash",
            "Energetika xavfsizligi: tabiiy gaz, elektr energiyasi va muqobil manbalar",
            "Moliyaviy va bank xavfsizligi: kapitalning noqonuniy chiqib ketishiga qarshi kurash",
            "Yashirin (norasmiy) iqtisodiyot ko'lamini qisqartirish strategiyalari",
            "Tashqi iqtisodiy xavflar va jahon bozorlaridagi narx tebranishlaridan himoyalanish",
            "Texnologik va axborot xavfsizligini ta'minlashning iqtisodiy omillari",
            "Demografik xavfsizlik va mehnat bozoridagi nomutanosibliklar tahlili",
            "Iqtisodiy xavfsizlikni ta'minlashda davlat zaxiralari va suveren fondlarning roli",
            "Korrupsiyaga qarshi kurashish va shaffoflikni oshirishning iqtisodiy samaradorligi"
        ]
    },
    "fintech": {
        "title": "Moliyaviy texnologiyalar (FinTech)",
        "category": "raqamli",
        "topics": [
            "O'zbekistonda FinTech ekotizimi: rivojlanish bosqichlari va tartibga solish ('Regulatory Sandbox')",
            "Milliy to'lov tizimlari (HUMO, Uzcard) va kontaktsiz to'lovlar evolyutsiyasi",
            "Neobanklar va raqamli bank ilovalari faoliyati iqtisodiyoti",
            "P2P pul o'tkazmalari bozori va to'lov xizmatlarini ko'rsatuvchi tashkilotlar",
            "Kriptovalyutalar va kriptobirjalar faoliyatini O'zbekistonda qonuniy tartibga solish",
            "Skoring tizimlari va kredit berishda sun'iy intellektdan foydalanish",
            "Kraudfanding (Crowdfunding) va kraudlending orqali startaplarni moliyalashtirish",
            "BNPL ('Hozir xarid qil, keyin to'la') xizmatlari va iste'molchilar xulq-atvori",
            "RegTech va SupTech: moliyaviy nazoratni avtomatlashtirish vositalari",
            "Ochiq banking (Open Banking API) va uning moliyaviy xizmatlar raqobatidagi o'rni"
        ]
    },
    "bojxona": {
        "title": "Bojxona ishi va tariflar",
        "category": "raqamli",
        "topics": [
            "O'zbekiston Bojxona kodeksi va bojxona-tarif tartibga solish tamoyillari",
            "Bojxona to'lovlari (import bojlari, aksiz solig'i, QQS, bojxona yig'imlari) hisobi",
            "Bojxona rasmiylashtiruvi rejimlarini qo'llash amaliyoti (erkin muomala, eksport, tranzit)",
            "Tovarlarning bojxona qiymatini aniqlash usullari va nizolarni bartaraf etish",
            "Bojxona ma'muriyatchiligida avtomatlashtirilgan xavflarni boshqarish tizimi (XBT)",
            "'Yashil', 'Sariq', 'Ko'k' va 'Qizil' yo'laklar orqali bojxona nazoratini optimallashtirish",
            "Jahon Bojxona Tashkiloti (WCO) standartlari va O'zbekiston bojxona islohotlari",
            "Kontrabandaga qarshi kurash va tovarlarning noqonuniy aylanmasini to'xtatish",
            "Tashqi iqtisodiy faoliyat tovar nomenklaturasi (TIF TN) asosida tovarlarni kodlashtirish",
            "Elektron deklaratsiyalash va 'Yagona darcha' bojxona axborot tizimi"
        ]
    },
    "jahon": {
        "title": "Jahon xo'jaligi va integratsiya",
        "category": "raqamli",
        "topics": [
            "Zamonaviy jahon xo'jaligining tuzilishi, markazlari va rivojlanish qonuniyatlari",
            "Global iqtisodiy integratsiya jarayonlari (Yevropa Ittifoqi, NAFTA, ASEAN, ShHT)",
            "Xalqaro valyuta tizimi (Bretton-Vuds, Yamayka) va AQSH dollari gegemonligi",
            "Xalqaro Valyuta Jamg'armasi (XVJ / IMF) va Jahon Banki guruhining global roli",
            "BRICS iqtisodiy blokining kengayishi va jahon savdo arxitekturasidagi o'zgarishlar",
            "Xitoyning 'Bir makon, bir yo'l' (Belt and Road) global investitsion tashabbusi",
            "Rivojlangan va rivojlanayotgan mamlakatlar o'rtasidagi iqtisodiy tengsizlik muammosi",
            "Jahon xomashyo va energetika bozorlari (OPEC+ va neft narxlari dinamikasi)",
            "Global demografik siljishlar va xalqaro mehnat migratsiyasining iqtisodiy oqibatlari",
            "Kelajak iqtisodiyoti: to'rtinchi sanoat inqilobi (Industry 4.0) va global mehnat taqsimoti"
        ]
    }
}

# ==============================================================================
# 📊 O'ZBEKISTON RESPUBLIKASI RASMIY MAKROIQTIQODIY MA'LUMOTNOMASI
# ==============================================================================
# Manbalar: O'zbekiston Respublikasi Prezidenti huzuridagi Statistika agentligi (stat.uz),
# O'zbekiston Respublikasi Markaziy banki (cbu.uz), Iqtisodiyot va moliya vazirligi.
# ==============================================================================
UZBEKISTAN_MACRO_INDICATORS: Dict[str, Any] = {
    "gdp_nominal": "110+ mlrd AQSH dollari (2024-2025)",
    "gdp_growth": "6.2% - 6.5% yillik real o'sish sur'ati",
    "gdp_per_capita": "3,000+ AQSH dollari (2030 yilga maqsad: 4,000 $)",
    "inflation_rate": "9.5% - 9.8% (CPI - iste'mol narxlari indeksi)",
    "cbu_policy_rate": "13.5% yillik (Markaziy bank asosiy stavkasi)",
    "foreign_trade_turnover": "65+ mlrd AQSH dollari",
    "export_volume": "25.5 mlrd AQSH dollari (Oltin, to'qimachilik, mis, oziq-ovqat, IT xizmatlar)",
    "import_volume": "39.5 mlrd AQSH dollari (Mashina va uskunalar, sanoat tovarlari, kimyo)",
    "population": "37.5+ million kishi (mehnatga layoqatli aholi: 60%+)",
    "top_trade_partners": "Xitoy (25.3%), Rossiya (22.1%), Qozog'iston (7.8%), Turkiya (5.2%), Janubiy Koreya",
    "industry_growth": "7.2% yillik o'sish",
    "agriculture_growth": "4.1% yillik o'sish",
    "services_growth": "12.8% yillik o'sish",
    "state_budget_social_share": "Davlat byudjeti xarajatlarining 50%+ ijtimoiy soha (ta'lim, tibbiyot) ga yo'naltirilgan",
    "strategy_2030": "'O'zbekiston - 2030' strategiyasi: YaIMni 160 mlrd dollarga yetkazish, daromadlarni oshirish, sanoat klasterlari va yashil energetika ulushini 40% ga chiqarish."
}

def get_category_subjects(cat_id: str) -> Dict[str, str]:
    """Berilgan kategoriya bo'yicha fanlar ro'yxatini qaytaradi."""
    if cat_id in CATEGORIES:
        return CATEGORIES[cat_id]["subjects"]
    return {}

def get_subject_info(subj_id: str) -> Optional[Dict[str, Any]]:
    """Fan haqida to'liq ma'lumotni qaytaradi."""
    return KNOWLEDGE_BASE.get(subj_id)

def get_subject_topics(subj_id: str) -> List[str]:
    """Fanning barcha 10 ta tayyor mavzulari ro'yxatini qaytaradi."""
    subj = KNOWLEDGE_BASE.get(subj_id)
    if subj:
        return subj.get("topics", [])
    return []

def search_subjects_or_topics(query: str) -> List[Dict[str, str]]:
    """Kalit so'z bo'yicha barcha fanlar va mavzular ichidan qidirish."""
    results: List[Dict[str, str]] = []
    q_lower = query.lower().strip()
    if not q_lower:
        return results
        
    for subj_id, data in KNOWLEDGE_BASE.items():
        subj_title = data["title"]
        if q_lower in subj_title.lower():
            results.append({"type": "subject", "id": subj_id, "title": subj_title, "match": subj_title})
        for topic in data.get("topics", []):
            if q_lower in topic.lower():
                results.append({"type": "topic", "id": subj_id, "title": subj_title, "match": topic})
                if len(results) >= 15:
                    return results
    return results

def get_macro_stats_text(lang: str = "uz") -> str:
    """O'zbekiston iqtisodiyoti bo'yicha rasmiy statistik ma'lumotnoma matni."""
    m = UZBEKISTAN_MACRO_INDICATORS
    if lang == "ru":
        return (
            "📊 Официальный макроэкономический справочник Республики Узбекистан:\n\n"
            f"• Номинальный ВВП: {m['gdp_nominal']}\n"
            f"• Темп роста ВВП: {m['gdp_growth']}\n"
            f"• ВВП на душу населения: {m['gdp_per_capita']}\n"
            f"• Уровень инфляции (ИПЦ): {m['inflation_rate']}\n"
            f"• Основная ставка ЦБ: {m['cbu_policy_rate']}\n"
            f"• Внешнеторговый оборот: {m['foreign_trade_turnover']}\n"
            f"  - Экспорт: {m['export_volume']}\n"
            f"  - Импорт: {m['import_volume']}\n"
            f"• Население: {m['population']}\n"
            f"• Основные торговые партнеры: {m['top_trade_partners']}\n"
            f"• Рост отраслей: Промышленность {m['industry_growth']}, Сельское хоз-во {m['agriculture_growth']}, Услуги {m['services_growth']}\n\n"
            f"🎯 Стратегия 'Узбекистан - 2030': {m['strategy_2030']}\n\n"
            "🏛 Официальные источники: stat.uz, cbu.uz."
        )
    return (
        "📊 O'zbekiston Respublikasi rasmiy makroiqtisodiy statistik ma'lumotnomasi:\n\n"
        f"• Yalpi ichki mahsulot (YaIM): {m['gdp_nominal']}\n"
        f"• YaIMning yillik real o'sishi: {m['gdp_growth']}\n"
        f"• Aholi jon boshiga YaIM: {m['gdp_per_capita']}\n"
        f"• Inflyatsiya darajasi (CPI): {m['inflation_rate']}\n"
        f"• Markaziy bank asosiy qayta moliyalash stavkasi: {m['cbu_policy_rate']}\n"
        f"• Tashqi savdo aylanmasi: {m['foreign_trade_turnover']}\n"
        f"  - Eksport: {m['export_volume']}\n"
        f"  - Import: {m['import_volume']}\n"
        f"• Aholi soni: {m['population']}\n"
        f"• Asosiy savdo hamkorlar: {m['top_trade_partners']}\n"
        f"• Tarmoqlar o'sishi: Sanoat {m['industry_growth']}, Qishloq xo'jaligi {m['agriculture_growth']}, Xizmatlar {m['services_growth']}\n\n"
        f"🎯 'O'zbekiston - 2030' strategiyasi maqsadi: {m['strategy_2030']}\n\n"
        "🏛 Rasmiy manbalar: stat.uz, cbu.uz."
    )

def build_academic_essay_prompt(subject_title: str, topic: str, lang: str = "uz") -> str:
    """
    O'zbekiston Respublikasi OTM davlat ta'lim standarti bo'yicha
    aynan 2 to'liq sahifa (2 ta list, taxminan 3 600 - 4 200 belgi / 550 - 650 so'z)
    hajmida ixcham, chuqur tahliliy va professional akademik mustaqil ish yaratish prompti.
    """
    lang_name = "O'zbek tili (Lotin alifbosi)"
    if lang == "uz_cyr":
        lang_name = "Ўзбек тили (Кирилл алифбоси)"
    elif lang == "ru":
        lang_name = "Русский язык"
    elif lang == "en":
        lang_name = "English"

    prompt = (
        f"Sen O'zbekistonning eng nufuzli iqtisodiyot universiteti (Toshkent Davlat Iqtisodiyot Universiteti, JIDU) "
        f"bosh ilmiy rahbari, professori va talabalar uchun oliy toifali mustaqil ishlar bo'yicha bosh maslahatchisisan.\n\n"
        f"VAZIFA: '{subject_title}' fani bo'yicha «{topic}» mavzusida OTM standarti talablariga to'liq mos keluvchi, "
        f"ilmiy, chuqur tahliliy va Wordda (Times New Roman 14pt, 1.5 interval) AYNAN 2 TO'LIQ LIST / SAHIFA "
        f"(umumiy hajmi qat'iy 3 600 dan 4 200 gacha belgi, ya'ni taxminan 550 - 650 so'zdan iborat) MUKAMMAL MUSTAQIL ISH yozib ber.\n\n"
        f"QAT'IY STRUKTURA VA BO'LIMLAR (Har bir bo'lim alohida qatordan toza sarlavha bilan boshlansin):\n\n"
        f"KIRISH\n"
        f"- Mavzuning dolzarbligi va bugungi kundagi ilmiy-amaliy ahamiyati;\n"
        f"- Tadqiqotning maqsadi va belgilangan asosiy vazifalari.\n"
        f"(Kirish qismi 2 ta to'liq, mazmundor xatboshidan iborat bo'lsin, umumiy hajmi ~600 - 700 belgi).\n\n"
        f"1-BOB. MAVZUNING NAZARIY-USLUBIY ASOSLARI VA XALQARO TAJRIBA\n"
        f"- Mavzuga oid asosiy iqtisodiy tushunchalar, qonuniyatlar va nazariy yondashuvlar;\n"
        f"- Rivojlangan xorijiy davlatlarning ilg'or tajribasi va zamonaviy xalqaro amaliyot tahlili.\n"
        f"(1-bob 2-3 ta chuqur, tahliliy xatboshidan iborat bo'lsin, umumiy hajmi ~1 200 - 1 400 belgi).\n\n"
        f"2-BOB. O'ZBEKISTON IQTISODIYOTIDAGI AMALIY HOLAT, STATISTIK TAHLIL VA MUAMMOLAR\n"
        f"- O'zbekiston Respublikasi Statistika agentligi (stat.uz) va Markaziy bank (cbu.uz) rasmiy ma'lumotlari asosidagi real ko'rsatkichlar (YaIM o'sishi, soha ko'rsatkichlari, dinamika va aniq raqamlar);\n"
        f"- «O'zbekiston – 2030» strategiyasi doirasida amalga oshirilayotgan tub islohotlar va sohada mavjud amaliy muammolar tahlili.\n"
        f"(2-bob 2-3 ta boy statistik va tahliliy xatboshidan iborat bo'lsin, umumiy hajmi ~1 200 - 1 400 belgi).\n\n"
        f"XULOSA VA TAKLIFLAR\n"
        f"- Tadqiqot va tahlil natijalari bo'yicha tizimli ilmiy xulosalar;\n"
        f"- O'zbekiston iqtisodiyoti amaliyotiga tatbiq etish va mavjud muammolarni hal etish bo'yicha 3-4 ta aniq, amaliy taklif va tavsiyalar.\n"
        f"(Xulosa qismi 2 ta to'liq xatboshidan iborat bo'lsin, umumiy hajmi ~600 - 700 belgi).\n\n"
        f"QAT'IY CHEKLOV VA TALABLAR:\n"
        f"1. 🚫 MATN OXIRIDA ADABIYOTLAR RO'YXATI YOKI FOYDALANILGAN MANBALARNI YOZISH QAT'IYAN TAQIQLANADI! (Hech qanday 'Foydalanilgan adabiyotlar' yoki 'References' bo'limi kiritilmasin, hujjat faqat XULOSA VA TAKLIFLAR bilan yakunlansin!).\n"
        f"2. 🚫 HAJM CHEKLOVI: Matn haddan tashqari cho'zilib ketmasin va juda qisqa bo'lib qolmasin. Aynan 2 ta listga (3 600 - 4 200 belgi) qat'iy rioya qilinsin!\n"
        f"3. 🚫 Hech qanday markdown panjara (#, ##, ###) yoki yulduzchalar (**) ishlatilmasin. Sarlavhalar faqat katta harflarda (KIRISH, 1-BOB..., 2-BOB..., XULOSA VA TAKLIFLAR) toza matn sifatida yozilsin.\n"
        f"4. 🚫 Ortiqcha kirish so'zlari, salomlashish yoki 'Marhamat, tayyor' kabi jumlalar mutlaqo yozilmasin. To'g'ridan-to'g'ri 'KIRISH' sarlavhasi bilan boshlansin.\n\n"
        f"Til: {lang_name}."
    )
    return prompt
