"""Demo rejim: API kalitsiz oddiy qoidalar asosida javob beruvchi yordamchi.

Haqiqiy AI emas — botni sinab ko'rish uchun mo'ljallangan.
"""

import ast
import operator
import random
import re
from datetime import datetime

DEMO_NOTE = "\n\n🧪 (Demo rejim — haqiqiy AI ulanmagan)"

GREETINGS = ("salom", "assalom", "hello", "hi", "привет", "здравствуй", "hayrli kun")
THANKS = ("rahmat", "raxmat", "spasibo", "спасибо", "thanks", "thank you")
BYES = ("xayr", "hayr", "ko'rishguncha", "пока", "bye")

JOKES = [
    "Dasturchi do'konga boradi. Xotini: «Bitta non ol, tuxum bo'lsa — 10 ta». "
    "U 10 ta non olib keldi. Chunki tuxum bor edi 😄",
    "— Nega dasturchilar qorong'ida ishlashni yaxshi ko'radi?\n— Chunki light mode ko'zni og'ritadi 🌚",
    "Kompyuterim menga shaxmatda yutqazdi. Lekin boks bo'yicha men undan kuchliroqman 🥊",
    "Wi-Fi ishlamasa, odamlar bir-biri bilan gaplasha boshlaydi. Juda qo'rqinchli 😱",
]

FACTS = [
    "Asal hech qachon buzilmaydi — Misr piramidalaridan 3000 yillik asal topilgan 🍯",
    "Sakkizoyoqning uchta yuragi bor 🐙",
    "Yer yuzidagi chumolilarning umumiy og'irligi odamlarnikiga yaqin 🐜",
    "Samarqand 2700 yildan ortiq tarixga ega — dunyodagi eng qadimiy shaharlardan biri 🏛",
]

UZ_WEEKDAYS = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}
MATH_RE = re.compile(r"^[\d\s+\-*/().,%^]+$")


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        left, right = _eval(node.left), _eval(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 100:
            raise ValueError("daraja juda katta")
        return _OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("ruxsat etilmagan ifoda")


def calculate(expr: str) -> str | None:
    """Oddiy arifmetik ifodani xavfsiz hisoblaydi (eval ishlatmasdan)."""
    expr = expr.replace(",", ".").replace("^", "**").replace("=", "").strip()
    if not expr or not MATH_RE.match(expr.replace("**", "^")) or not re.search(r"\d", expr):
        return None
    try:
        result = _eval(ast.parse(expr, mode="eval").body)
    except ZeroDivisionError:
        return "🧮 Nolga bo'lib bo'lmaydi 🙂"
    except (SyntaxError, ValueError, OverflowError):
        return None
    if isinstance(result, float) and result.is_integer():
        result = int(result)
    elif isinstance(result, float):
        result = round(result, 6)
    return f"🧮 {expr.replace('**', '^')} = {result}"


def reply(text: str, name: str = "") -> str:
    t = text.lower().strip()

    if t.startswith("[rasm yuborildi]"):
        return "🖼 Rasmingizni oldim! Demo rejimda rasmlarni tahlil qila olmayman." + DEMO_NOTE

    if (math := calculate(text)) is not None:
        return math + DEMO_NOTE

    if any(w in t for w in GREETINGS):
        return f"Va alaykum assalom{', ' + name if name else ''}! 😊 Sizga qanday yordam bera olaman?" + DEMO_NOTE

    if any(w in t for w in THANKS):
        return "Arzimaydi! Yana savollaringiz bo'lsa, yozavering 🙌" + DEMO_NOTE

    if any(w in t for w in BYES):
        return "Xayr! Yaxshi kun tilayman 👋" + DEMO_NOTE

    if "qalaysan" in t or "yaxshimisiz" in t or "ishlar qalay" in t or "как дела" in t:
        return "Rahmat, zo'r! Siz-chi? 😊" + DEMO_NOTE

    if "soat" in t or "vaqt" in t:
        return f"🕐 Hozir soat: {datetime.now():%H:%M}" + DEMO_NOTE

    if "sana" in t or "bugun" in t or "kun" in t:
        now = datetime.now()
        return f"📅 Bugun: {now:%d.%m.%Y}, {UZ_WEEKDAYS[now.weekday()]}" + DEMO_NOTE

    if "latifa" in t or "hazil" in t or "анекдот" in t or "joke" in t:
        return random.choice(JOKES) + DEMO_NOTE

    if "fakt" in t or "qiziq" in t:
        return "💡 " + random.choice(FACTS) + DEMO_NOTE

    if "isming" in t or "kimsan" in t or "sen kim" in t:
        return "Men Smart Yordamchi botman 🤖 Hozir demo rejimda ishlayapman." + DEMO_NOTE

    if "nima qila olasan" in t or "imkoniyat" in t:
        return (
            "Demo rejimda men:\n"
            "• salomlashaman 👋\n"
            "• hisoblayman (masalan: 12*7+5) 🧮\n"
            "• soat va sanani aytaman 🕐\n"
            "• latifa va qiziqarli fakt aytaman 😄\n\n"
            "To'liq AI imkoniyatlari uchun ANTHROPIC_API_KEY ni ulang."
        ) + DEMO_NOTE

    if t.endswith("?"):
        return (
            "Yaxshi savol! 🤔 Afsuski, demo rejimda murakkab savollarga javob bera olmayman. "
            "Sinab ko'ring: «latifa ayt», «soat necha», «25*4»."
        ) + DEMO_NOTE

    return f"Siz yozdingiz: «{text}»\n\nBuyruqlar ro'yxati uchun «nima qila olasan?» deb yozing." + DEMO_NOTE
