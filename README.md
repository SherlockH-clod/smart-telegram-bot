# 🤖 Smart Yordamchi — Telegram Bot

Claude AI asosida ishlaydigan aqlli Telegram yordamchi bot.

## ✨ Imkoniyatlar

- 💬 Istalgan savolga javob beradi (o'zbek, rus, ingliz va boshqa tillarda)
- 🧠 Suhbatni eslab qoladi (har bir foydalanuvchi uchun alohida)
- 🖼 Rasmlarni tahlil qiladi (rasmga izoh/savol yozish mumkin)
- ✍️ Matn yozish, tarjima, kod yozish va tushuntirish
- 🔒 Faqat tanlangan foydalanuvchilarga ruxsat berish imkoniyati
- 📏 Uzun javoblarni avtomatik bo'laklarga bo'lib yuboradi

## 📋 Buyruqlar

| Buyruq   | Vazifasi                        |
|----------|---------------------------------|
| `/start` | Botni ishga tushirish           |
| `/new`   | Yangi suhbat (tarixni tozalash) |
| `/help`  | Yordam                          |

## 🚀 O'rnatish

### 1. Kalitlarni oling
- **Telegram token:** Telegram'da [@BotFather](https://t.me/BotFather) → `/newbot`
- **Anthropic API kalit:** [console.anthropic.com](https://console.anthropic.com) → API Keys

### 2. Loyihani yuklab oling
```bash
git clone https://github.com/<USERNAME>/smart-telegram-bot.git
cd smart-telegram-bot
```

### 3. Kutubxonalarni o'rnating (Python 3.10+)
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
```

### 4. `.env` faylini yarating
```bash
cp .env.example .env
```
So'ng `.env` ichiga `TELEGRAM_BOT_TOKEN` va `ANTHROPIC_API_KEY` ni yozing.

### 5. Ishga tushiring
```bash
python bot.py
```

## ⚙️ Sozlamalar (`.env`)

| O'zgaruvchi          | Tavsif                                                      | Standart          |
|----------------------|-------------------------------------------------------------|-------------------|
| `TELEGRAM_BOT_TOKEN` | BotFather tokeni (majburiy)                                 | —                 |
| `ANTHROPIC_API_KEY`  | Anthropic API kaliti (bo'sh bo'lsa — demo rejim)            | —                 |
| `DEMO_MODE`          | `true` — API kalitsiz demo rejimni majburan yoqish          | `false`           |
| `CLAUDE_MODEL`       | Model nomi                                                  | `claude-opus-5-5` |
| `CLAUDE_EFFORT`      | Fikrlash darajasi: `low`/`medium`/`high`/`xhigh`/`max`      | `medium`          |
| `MAX_HISTORY`        | Eslab qolinadigan xabarlar soni                             | `20`              |
| `ALLOWED_USERS`      | Ruxsat berilgan Telegram ID'lar (vergul bilan), bo'sh = hamma | —               |
| `SYSTEM_PROMPT`      | Bot xarakterini o'zgartirish uchun ko'rsatma                | o'zbekcha prompt  |

> 💡 Arzonroq va tezroq ishlashi uchun `CLAUDE_EFFORT=low` yoki `CLAUDE_MODEL=claude-haiku-5-5` qo'ying.

## 🧪 Demo rejim (API kalitsiz)

`ANTHROPIC_API_KEY` bo'sh bo'lsa yoki `DEMO_MODE=true` bo'lsa, bot AI'siz ishlaydi —
faqat `TELEGRAM_BOT_TOKEN` yetarli. Demo rejimda bot:

- salomlashadi va xayrlashadi 👋
- hisoblaydi: `12*7+5`, `2^10`, `(15+5)/4` 🧮
- soat va sanani aytadi 🕐
- latifa va qiziqarli fakt aytadi 😄

Har bir javob oxirida `🧪 Demo rejim` belgisi turadi. Kod: [`dummy.py`](dummy.py).

## 🐳 Docker orqali

```bash
docker build -t smart-bot .
docker run -d --env-file .env --name smart-bot smart-bot
```

## ☁️ Serverga joylash

`Procfile` mavjud — Railway, Render yoki Heroku'da **worker** sifatida ishga tushiring
va muhit o'zgaruvchilarini (Environment Variables) panel orqali kiriting.

## 📝 Eslatma

Suhbat tarixi xotirada saqlanadi — bot qayta ishga tushganda tozalanadi.

## 📄 Litsenziya

MIT
