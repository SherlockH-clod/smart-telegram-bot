"""Smart yordamchi Telegram bot (Claude AI asosida)."""

import base64
import logging
import os
from collections import defaultdict, deque

import anthropic
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-5-5")
CLAUDE_EFFORT = os.getenv("CLAUDE_EFFORT", "medium")  # low | medium | high | xhigh | max
MAX_HISTORY = int(os.getenv("MAX_HISTORY", "20"))
ALLOWED_USERS = {
    int(uid) for uid in os.getenv("ALLOWED_USERS", "").replace(" ", "").split(",") if uid
}

SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "Sen aqlli va do'stona yordamchisan. Foydalanuvchi qaysi tilda yozsa, "
    "o'sha tilda javob ber (odatda o'zbek tilida). Javoblaring aniq, foydali "
    "va lo'nda bo'lsin. Telegram'da o'qilishi qulay bo'lishi uchun oddiy matn "
    "va qisqa ro'yxatlardan foydalan.",
)

TELEGRAM_LIMIT = 4096

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("smart-bot")

client = anthropic.AsyncAnthropic()  # ANTHROPIC_API_KEY muhit o'zgaruvchisidan olinadi

# Har bir foydalanuvchi uchun suhbat tarixi (faqat matn, xotirada saqlanadi)
histories: dict[int, deque] = defaultdict(lambda: deque(maxlen=MAX_HISTORY))


def is_allowed(update: Update) -> bool:
    return not ALLOWED_USERS or update.effective_user.id in ALLOWED_USERS


def split_message(text: str, limit: int = TELEGRAM_LIMIT) -> list[str]:
    """Uzun javobni Telegram chegarasiga mos bo'laklarga ajratadi."""
    chunks = []
    while len(text) > limit:
        cut = text.rfind("\n", 0, limit)
        if cut <= 0:
            cut = limit
        chunks.append(text[:cut])
        text = text[cut:].lstrip("\n")
    if text:
        chunks.append(text)
    return chunks


def build_messages(user_id: int, content) -> list[dict]:
    """Tarix + yangi xabar. Tarix doim 'user' bilan boshlanishi kerak."""
    history = list(histories[user_id])
    while history and history[0]["role"] != "user":
        history.pop(0)
    return history + [{"role": "user", "content": content}]


async def ask_claude(user_id: int, content, history_text: str) -> str:
    messages = build_messages(user_id, content)
    try:
        response = await client.beta.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            messages=messages,
            output_config={"effort": CLAUDE_EFFORT},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
    except anthropic.AuthenticationError:
        log.error("ANTHROPIC_API_KEY noto'g'ri")
        return "⚠️ Server sozlamalarida xatolik (API kalit). Administratorga murojaat qiling."
    except anthropic.RateLimitError:
        return "⏳ Hozir so'rovlar ko'p. Birozdan keyin qayta urinib ko'ring."
    except anthropic.BadRequestError as e:
        log.error("Bad request: %s", e.message)
        return "⚠️ So'rovda xatolik yuz berdi. /new buyrug'i bilan suhbatni yangilab ko'ring."
    except anthropic.APIStatusError as e:
        log.error("API xatosi %s: %s", e.status_code, e.message)
        return "⚠️ AI xizmatida vaqtinchalik nosozlik. Keyinroq urinib ko'ring."
    except anthropic.APIConnectionError:
        return "🌐 AI xizmatiga ulanib bo'lmadi. Keyinroq urinib ko'ring."

    if response.stop_reason == "refusal":
        return "🙅 Kechirasiz, bu so'rovga javob bera olmayman."

    answer = "".join(b.text for b in response.content if b.type == "text").strip()
    if not answer:
        answer = "🤔 Javob topilmadi, savolni boshqacha berib ko'ring."
    elif response.stop_reason == "max_tokens":
        answer += "\n\n…(javob juda uzun bo'lgani uchun qisqartirildi)"

    histories[user_id].append({"role": "user", "content": history_text})
    histories[user_id].append({"role": "assistant", "content": answer})
    return answer


async def reply_long(update: Update, text: str) -> None:
    for chunk in split_message(text):
        await update.message.reply_text(chunk)


# ---------- Buyruqlar ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed(update):
        await update.message.reply_text("⛔ Sizga bu botdan foydalanishga ruxsat berilmagan.")
        return
    name = update.effective_user.first_name or "do'stim"
    await update.message.reply_text(
        f"Assalomu alaykum, {name}! 👋\n\n"
        "Men sizning aqlli yordamchingizman. Menga istalgan savol bering, "
        "matn yozdiring, tarjima qildiring yoki rasm yuboring — tahlil qilib beraman.\n\n"
        "Buyruqlar uchun /help ni bosing."
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📖 <b>Buyruqlar</b>\n\n"
        "/start — botni ishga tushirish\n"
        "/new — yangi suhbat boshlash (tarixni tozalash)\n"
        "/help — yordam\n\n"
        "💡 <b>Imkoniyatlar</b>\n"
        "• Savollarga javob berish\n"
        "• Matn yozish, tahrirlash, tarjima\n"
        "• Kod yozish va tushuntirish\n"
        "• Rasmlarni tahlil qilish (rasmga izoh qo'shishingiz mumkin)\n"
        "• Oldingi xabarlarni eslab qoladi",
        parse_mode=ParseMode.HTML,
    )


async def new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    histories.pop(update.effective_user.id, None)
    await update.message.reply_text("🧹 Suhbat tarixi tozalandi. Yangi savol bering!")


# ---------- Xabarlar ----------

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed(update):
        return
    text = update.message.text
    await context.bot.send_chat_action(update.effective_chat.id, ChatAction.TYPING)
    answer = await ask_claude(update.effective_user.id, text, text)
    await reply_long(update, answer)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed(update):
        return
    await context.bot.send_chat_action(update.effective_chat.id, ChatAction.TYPING)

    photo = update.message.photo[-1]  # eng katta o'lcham
    tg_file = await photo.get_file()
    data = await tg_file.download_as_bytearray()
    caption = update.message.caption or "Bu rasmda nima bor? Batafsil tushuntirib ber."

    content = [
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": base64.standard_b64encode(bytes(data)).decode(),
            },
        },
        {"type": "text", "text": caption},
    ]
    answer = await ask_claude(update.effective_user.id, content, f"[Rasm yuborildi] {caption}")
    await reply_long(update, answer)


async def handle_other(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed(update):
        return
    await update.message.reply_text("Hozircha men matn va rasmlarni tushunaman 🙂")


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.exception("Kutilmagan xato", exc_info=context.error)


def main() -> None:
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("new", new_chat))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(~filters.COMMAND, handle_other))
    app.add_error_handler(on_error)

    log.info("Bot ishga tushdi (model: %s)", CLAUDE_MODEL)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
