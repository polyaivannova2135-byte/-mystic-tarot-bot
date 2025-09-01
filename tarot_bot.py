# tarot_bot.py
# --- Keep-alive web для Replit ---
# --- Keep-alive web для Render/Replit___

import os
import threading
from flask import Flask
ADMIN_ID = 7495537286
USERS_FILE = "users.json"

def _load_users() -> set[int]:
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return set(data.get("users", []))
    except Exception:
        return set()

def _save_users(users: set[int]) -> None:
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump({"users": sorted(users)}, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

USERS = _load_users()

app = Flask(__name__)

@app.get("/")
def index():
    return "OK"  # healthcheck, UptimeRobot будет пинговать

# Render/Replit требует слушать порт из переменной окружения
PORT = int(os.getenv("PORT", "8080"))

def run_web():
    app.run(host="0.0.0.0", port=PORT)

# Запускаем веб-сервер в отдельном потоке
threading.Thread(target=run_web, daemon=True).start()

# ========== PYTHON / AIOGRAM ==========
import os
import json
import random
import asyncio

from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)

# ========== КНОПКИ ==========
def get_main_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🌞 Карта дня", callback_data="go:day"),
            InlineKeyboardButton(text="❓ Да/Нет", callback_data="go:ask"),
        ],
        [
            InlineKeyboardButton(text="🔮 3 карты", callback_data="go:spread3"),
            InlineKeyboardButton(text="🦋 12 Истин", callback_data="go:deep12"),
        ],
        [
            InlineKeyboardButton(text="✝️ Крест", callback_data="go:cross"),
        ],
        [
            InlineKeyboardButton(text="💞 Совместимость", callback_data="go:compat"),
        ],
    ])

def get_main_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/day"), KeyboardButton(text="/ask")],
            [KeyboardButton(text="/spread3"), KeyboardButton(text="/deep12")],
            [KeyboardButton(text="/cross")],
            [KeyboardButton(text="/compat")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

# ========== ИМПОРТЫ ДАННЫХ ==========
from compat_names import name_percent, name_text_for_percent
from compat_zodiac import ZODIACS, zodiac_percent, zodiac_text_for_percent
from tarot_meanings_love import MEANINGS_LOVE
from tarot_meanings_money import MEANINGS_MONEY
from tarot_meanings_path import MEANINGS_PATH
from tarot_meanings_inner import MEANINGS_INNER
from tarot_conclusions import CONCLUSIONS
from tarot_scores import CARD_SCORES

from cross_meanings.core import CORE_MEANINGS
from cross_meanings.block import BLOCK_MEANINGS
from cross_meanings.past import PAST_MEANINGS
from cross_meanings.future import FUTURE_MEANINGS
from cross_meanings.outcome import OUTCOME_MEANINGS

# ========== ВСПОМОГАТЕЛЬНОЕ ==========
def get_zodiac_kb(who: str) -> InlineKeyboardMarkup:
    rows, row = [], []
    for i, sign in enumerate(ZODIACS, start=1):
        row.append(InlineKeyboardButton(text=sign, callback_data=f"z:{who}:{sign}"))
        if i % 3 == 0:
            rows.append(row); row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)

CROSS_MEANINGS = {
    "core": CORE_MEANINGS,
    "block": BLOCK_MEANINGS,
    "past": PAST_MEANINGS,
    "future": FUTURE_MEANINGS,
    "outcome": OUTCOME_MEANINGS,
}

# Память сценария совместимости
USER_FLOW: dict[int, dict] = {}

def meaning_cross(position, name, side):
    src = CROSS_MEANINGS.get(position, {})
    return src.get(name, {}).get(side, "Толкование пока не добавлено.")

def analyze_sphere(cards):
    """
    cards: [("Маг","upright"), ("Башня","reversed"), ...]
    -> "positive" | "neutral" | "challenging"
    """
    score = 0
    for name, side in cards:
        score += CARD_SCORES.get(name, {}).get(side, 0)
    if score >= 1:
        return "positive"
    if score <= -1:
        return "challenging"
    return "neutral"

def meaning_for(sphere, name, side):
    src = {
        "love": MEANINGS_LOVE,
        "money": MEANINGS_MONEY,
        "path": MEANINGS_PATH,
        "inner": MEANINGS_INNER,
    }[sphere]
    return src.get(name, {}).get(side, "Значение для этой карты пока не добавлено.")

def pick_conclusion(sphere, tone):
    options = CONCLUSIONS.get(sphere, {}).get(tone, [])
    if not options:
        return "Вывод пока не подготовлен."
    return random.choice(options)

# ========== НАСТРОЙКА БОТА ==========
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# ===== БАЗОВЫЕ КОМАНДЫ (пинг + старт) =====
@dp.message(Command("stats"))
async def cmd_stats(m: types.Message):
    if m.from_user.id != ADMIN_ID:
        await m.answer("⛔️ У тебя нет доступа к этой команде.")
        return

    count = len(USERS)
    await m.answer(f"👥 Всего пользователей: {count}")
    
@dp.message(Command("ping"))
async def cmd_ping(m: types.Message):
    await m.answer("pong ✅")

@dp.message(Command("start"))
async def cmd_start(m: types.Message):
    text = (
        "✨ Привет! Я твой таро-ассистент ✨\n\n"
        "Помни: таро — это не приговор, а зеркало твоих мыслей и чувств.\n"
        "Расклады:\n"
        "• /day — 🌞 карта дня + совет\n"
        "• /ask — ❓ 2 карты «да/нет»\n"
        "• /spread3 — 🔮 3 карты (Любовь/Финансы/Общий)\n"
        "• /deep12 — 🦋 «12 карт Истины»\n"
        "• /cross — ✝️ «Крест»\n"
        "• /compat — 💞 совместимость\n\n"
        "Ниже — кнопки. Если любишь зелёные большие кнопки, напиши /menu."
    )
    # сохраняем пользователя
    USERS.add(m.from_user.id)
    _save_users(USERS)
    await m.answer(
        text,
        reply_markup=get_main_inline(),  # <-- ИНЛАЙН вместо reply
        parse_mode="HTML"
    )

@dp.message(Command("menu"))
async def cmd_menu(m: types.Message):
    await m.answer("Главное меню открыто 👇", reply_markup=get_main_kb())
# ========== ОБРАБОТКА ИНЛАЙН-КНОПОК С ГЛАВНОГО МЕНЮ ==========
@dp.callback_query(F.data == "go:day")
async def cb_day(callback: types.CallbackQuery):
    await callback.answer()
    await cmd_day(callback.message)

@dp.callback_query(F.data == "go:ask")
async def cb_ask(callback: types.CallbackQuery):
    await callback.answer()
    await cmd_ask(callback.message)

@dp.callback_query(F.data == "go:spread3")
async def cb_spread3(callback: types.CallbackQuery):
    await callback.answer()
    await cmd_spread3(callback.message)

@dp.callback_query(F.data == "go:deep12")
async def cb_deep12(callback: types.CallbackQuery):
    await callback.answer()
    await cmd_deep12(callback.message)

@dp.callback_query(F.data == "go:cross")
async def cb_cross(callback: types.CallbackQuery):
    await callback.answer()
    await cmd_cross(callback.message)

@dp.callback_query(F.data == "go:compat")
async def cb_compat(callback: types.CallbackQuery):
    await callback.answer()
    await cmd_compat(callback.message)

# (Отладчик всех сообщений убрал, чтобы не мешал сценарию совместимости)

# ========== КАРТА ДНЯ ==========
DECK_PATH = "deck_day.json"

def load_day_deck() -> dict:
    try:
        with open(DECK_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    # Фолбэк
    return {
        "Маг": {
            "upright": "День для инициативы и уверенных шагов.",
            "reversed": "Пока лучше притормозить и всё продумать."
        },
        "Императрица": {
            "upright": "Забота о себе, уют и плодородие идей.",
            "reversed": "Не растрачивай силы — береги ресурс."
        }
    }

DAY_DECK = load_day_deck()

MAJORS = [
    "Шут", "Маг", "Жрица", "Императрица", "Император", "Иерофант",
    "Влюблённые", "Колесница", "Сила", "Отшельник", "Колесо Фортуны",
    "Справедливость", "Повешенный", "Смерть", "Умеренность",
    "Дьявол", "Башня", "Звезда", "Луна", "Солнце", "Суд", "Мир"
]

GOOD = {"Маг","Императрица","Император","Влюблённые","Колесница","Сила","Колесо Фортуны","Звезда","Солнце","Мир","Суд"}
BAD = {"Дьявол","Башня","Луна"}
NEUTRAL = set(MAJORS) - GOOD - BAD

def pretty_card(name: str, reversed_: bool) -> str:
    return f"{name} (перевёрнутая)" if reversed_ else name

@dp.message(Command("day"))
async def cmd_day(m: types.Message):
    name = random.choice(list(DAY_DECK.keys()))
    is_reversed = random.choice([False, True])
    side = "reversed" if is_reversed else "upright"
    text = DAY_DECK[name].get(side, "")
    suffix = " (перевёрнутая)" if is_reversed else ""
    await m.answer(f"🪄 Карта дня: {name}{suffix}\n{text}")

# ========== ДА / НЕТ ==========
@dp.message(Command("ask"))
async def cmd_ask(m: types.Message):
    await m.answer("✨ Закрой глаза, загадай вопрос и сосредоточься...")
    for sm in ["🃏", "🔮", "✨"]:
        await asyncio.sleep(1)
        await m.answer(sm)

    c1, r1 = random.choice(MAJORS), random.choice([False, True])
    c2, r2 = random.choice(MAJORS), random.choice([False, True])

    def score(card: str, rev: bool) -> int:
        base = 1 if card in GOOD else -1 if card in BAD else 0
        return -base if rev else base

    s = score(c1, r1) + score(c2, r2)

    advices = [
        "Слушай сердце 💖", "Дай ситуации время ⏳", "Доверься интуиции 🌙",
        "Будь мягче к себе 🤍", "Сохрани баланс ⚖️", "Держи фокус — всё получится ✨",
    ]
    advice = random.choice(advices)

    if s >= 2: verdict = "✅ ДА"
    elif s == 1: verdict = "💕 Скорее да"
    elif s == 0: verdict = "🤍 Нейтрально"
    elif s == -1: verdict = "🌤️ Скорее нет"
    elif s <= -2: verdict = "❌ НЕТ"
    else: verdict = "👁️ Не могу ответить (карты не видят)"

    text = (
        "Твои карты:\n"
        f"• {pretty_card(c1, r1)}\n"
        f"• {pretty_card(c2, r2)}\n\n"
        f"Совет: {advice}\n\n"
        f"Ответ: {verdict}"
    )
    await m.answer(text)

# ========== /spread3 ==========
@dp.message(Command("spread3"))
async def cmd_spread3(m: types.Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="💖 Любовь",   callback_data="spread_love"),
            InlineKeyboardButton(text="💰 Финансы",  callback_data="spread_money"),
            InlineKeyboardButton(text="🪐 Общий",    callback_data="spread_general"),
        ]]
    )
    await m.answer("✨ Выбери тему расклада:", reply_markup=kb)

@dp.callback_query(F.data.startswith("spread_"))
async def process_spread_callback(callback_query: types.CallbackQuery):
    theme = callback_query.data  # spread_love / spread_money / spread_general

    await callback_query.message.answer("🔮 Перемешиваю колоду...")
    await asyncio.sleep(1)
    await callback_query.message.answer("🃏 Достаю карты...")
    await asyncio.sleep(1)

    cards = []
    for _ in range(3):  # (по твоей логике — повторы возможны)
        name = random.choice(MAJORS)
        is_reversed = random.choice([True, False])
        suffix = " (перевёрнутая)" if is_reversed else ""
        cards.append(f"🃏 {name}{suffix}")

    cards_text = "\n".join(cards)

    conclusions = {
        "spread_love": [
            "💖 В любви сегодня важно быть честной с собой. Немного мягкости — и связь станет теплее.",
            "🌹 Назревает новый этап — не бойся открыться и говорить о чувствах.",
            "💕 Отношения просят заботы и внимания. Нежность сейчас — это сила.",
            "✨ Атмосфера перемен: отпусти старое, чтобы пришло новое.",
            "💌 Романтическая энергия дня поддерживает признания и тёплые жесты.",
            "🌷 Уязвимость — это смелость. Она укрепит близость.",
            "🔮 Внутренняя трансформация ведёт к лёгкости в чувствах.",
            "🤍 Если было напряжение — наступает выравнивание. Говори мягко и искренне.",
            "🌙 Доверься интуиции — сердце подскажет нужные слова.",
            "🌟 Возможна судьбоносная встреча или тёплый разговор.",
            "🌼 Забота о себе улучшит и отношения — баланс начинается внутри.",
            "✨ Любовь рядом. Маленький шаг навстречу многое изменит.",
        ],
        "spread_money": [
            "💰 Финансы требуют внимательности и спокойных решений.",
            "📊 Деньги движутся верно — держи баланс расходов и накоплений.",
            "🌙 Возможна небольшая нестабильность, но она временная. Терпение окупится.",
            "✨ Постепенный прогресс надёжнее резких шагов.",
            "💎 Будь практичной: продумывай решения заранее.",
            "⚖️ Избегай крайностей — выбери золотую середину.",
            "📈 Тенденция к укреплению есть — сохрани фокус.",
            "🔮 Внутренняя гармония помогает денежному потоку.",
            "🌟 Появится возможность — оцени её без спешки.",
            "💵 Если было напряжение — наметится выравнивание. Держи контроль.",
            "🧭 Планирование и система дадут уверенность.",
            "🪙 Небольшой резерв спасёт от внезапных трат.",
        ],
        "spread_general": [
            "🪐 День мягкий, но полный перемен. Старое уходит — освобождается место для нового.",
            "✨ Прислушайся к интуиции — ответы рядом.",
            "🌱 Энергия роста есть, даже если шаги маленькие.",
            "🔭 Завершается цикл — время наметить новые планы.",
            "🌷 Баланс в заботе о себе поможет решать и внешние дела.",
            "🌙 Замечай знаки и ощущения — они подскажут важное.",
            "🧹 Небольшое очищение пространства даст лёгкость.",
            "💎 Случайные встречи/слова могут быть подсказками судьбы.",
            "✨ Маленькое действие приблизит к большой цели.",
            "🌸 Гармоничный день для сочетания дел и отдыха.",
            "🔮 Благоприятно начинать новое — доверься началу.",
            "🌤️ Не спеши — внимательность к деталям принесёт понимание.",
        ],
    }

    advice = random.choice(conclusions.get(theme, ["✨ Слушай интуицию и доверься процессу."]))
    await callback_query.message.answer(f"🔮 Твой расклад:\n\n{cards_text}\n\n{advice}")
    await callback_query.answer()

# ========== 12 КАРТ ИСТИНЫ ==========
@dp.message(Command("deep12"))
async def cmd_deep12(m: types.Message):
    spheres = [
        ("love",  "❤️ Любовь"),
        ("money", "💰 Финансы"),
        ("path",  "🧭 Истинный путь"),
        ("inner", "🕊 Внутренний мир"),
    ]

    await m.answer("✨ Делаю глубокий расклад «12 карт Истины». Перемешиваю колоду…")

    unique_12 = random.sample(MAJORS, 12)  # без повторов
    random.shuffle(unique_12)
    take_index = 0

    text_parts = []
    for sphere_key, sphere_title in spheres:
        names = unique_12[take_index:take_index + 3]
        take_index += 3

        three = []
        for name in names:
            side = "reversed" if random.choice([True, False]) else "upright"
            three.append((name, side))

        lines = [
            f"— {pretty_card(n, s == 'reversed')}: {meaning_for(sphere_key, n, s)}"
            for (n, s) in three
        ]

        tone = analyze_sphere(three)
        conclusion = pick_conclusion(sphere_key, tone)

        block = (
            f"\n<b>{sphere_title}</b>\n"
            f"{lines[0]}\n{lines[1]}\n{lines[2]}\n\n"
            f"<b>Вывод:</b> {conclusion}\n"
        )
        text_parts.append(block)

    full_text = "🔮 <b>Расклад «12 карт Истины»</b>\n" + "\n".join(text_parts)
    await m.answer(full_text)

# ========== КРЕСТ ==========
@dp.message(Command("cross"))
async def cmd_cross(m: types.Message):
    positions = [
        ("core",    "✨ Суть"),
        ("block",   "⛔️ Препятствие"),
        ("past",    "⌛️ Прошлое"),
        ("future",  "🌅 Будущее"),
        ("outcome", "🎯 Итог"),
    ]

    intro = (
        "🔮 <b>Расклад «Крест»</b>\n\n"
        "Сосредоточься на своём вопросе. Закрой глаза на пару секунд, "
        "сделай глубокий вдох и выдох. Представь, что держишь колоду…"
    )
    await m.answer(intro)

    anim = await m.answer("🃏 Перемешиваю колоду…")
    for dots in ["", " .", " ..", " ...", " ....", " ....."]:
        await asyncio.sleep(0.9)
        try:
            await anim.edit_text(f"🃏 Перемешиваю колоду{dots}")
        except Exception:
            pass

    names = random.sample(MAJORS, k=5)  # без повторов
    text_parts = []
    for (pos_key, pos_title), name in zip(positions, names):
        is_rev = random.choice([False, True])
        side = "reversed" if is_rev else "upright"
        line = f"— {pretty_card(name, is_rev)}: {meaning_cross(pos_key, name, side)}"
        text_parts.append(f"\n<b>{pos_title}</b>\n{line}")

    full_text = "🔮 <b>Расклад «Крест»</b>\n" + "\n".join(text_parts)

    try:
        await anim.delete()
    except Exception:
        pass
    await m.answer(full_text)

# ========== СОВМЕСТИМОСТЬ ==========
@dp.message(Command("compat"))
async def cmd_compat(m: types.Message):
    uid = m.from_user.id
    USER_FLOW[uid] = {
        "state": "ask_self_name",
        "self_name": None,
        "partner_name": None,
        "self_zodiac": None,
        "partner_zodiac": None,
    }
    await m.answer("💞 <b>Совместимость</b>\n\nНапиши, пожалуйста, <b>своё имя</b>.")

@dp.message(F.text)
async def compat_flow(m: types.Message):
    uid = m.from_user.id
    flow = USER_FLOW.get(uid)
    if not flow:
        return

    if flow["state"] == "ask_self_name":
        flow["self_name"] = m.text.strip()
        flow["state"] = "ask_partner_name"
        await m.answer("Теперь напиши <b>имя партнёра</b>.")
        return

    if flow["state"] == "ask_partner_name":
        flow["partner_name"] = m.text.strip()
        flow["state"] = "pick_self_zodiac"
        await m.answer("Выбери <b>свой</b> знак зодиака:", reply_markup=get_zodiac_kb("self"))
        return

@dp.callback_query(F.data.startswith("z:self:"))
async def pick_self_zodiac(callback: types.CallbackQuery):
    uid = callback.from_user.id
    flow = USER_FLOW.get(uid)
    if not flow:
        await callback.answer(); return

    my_sign = callback.data.split(":", 2)[2]
    flow["self_zodiac"] = my_sign
    flow["state"] = "pick_partner_zodiac"
    await callback.message.edit_text(
        f"Твой знак: <b>{my_sign}</b>\n\nТеперь выбери знак <b>партнёра</b>:",
        reply_markup=get_zodiac_kb("partner"),
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("z:partner:"))
async def pick_partner_zodiac(callback: types.CallbackQuery):
    uid = callback.from_user.id
    flow = USER_FLOW.get(uid)
    if not flow:
        await callback.answer(); return

    partner_sign = callback.data.split(":", 2)[2]
    flow["partner_zodiac"] = partner_sign

    n_pct = name_percent(flow["self_name"], flow["partner_name"])
    n_text = name_text_for_percent(n_pct)

    z_pct = zodiac_percent(flow["self_zodiac"], flow["partner_zodiac"])
    z_text = zodiac_text_for_percent(z_pct)

    total = int(round((n_pct + z_pct) / 2))
    if total >= 80:
        overall = "✨ Сильная связь и отличная перспектива!"
    elif total >= 60:
        overall = "🌿 Хорошая база — многое зависит от общения и уважения границ."
    elif total >= 40:
        overall = "⚖️ Союз возможен, но потребуется внимание к различиям."
    else:
        overall = "🌑 Связь непростая — без осознанности может быть тяжело."

    txt = (
        f"💞 <b>Совместимость</b>\n\n"
        f"Ты: <b>{flow['self_name']}</b> — {flow['self_zodiac']}\n"
        f"Партнёр: <b>{flow['partner_name']}</b> — {flow['partner_zodiac']}\n\n"
        f"📛 По именам: <b>{n_pct}%</b>\n— {n_text}\n\n"
        f"🌟 По знакам: <b>{z_pct}%</b>\n— {z_text}\n\n"
        f"🧩 Общая картина: <b>{total}%</b>\n{overall}\n\n"
        f"<i>Проценты — ориентир. Настоящая совместимость рождается из выбора и внимания двоих.</i>"
    )

    try:
        await callback.message.edit_text(txt)
    except Exception:
        await callback.message.answer(txt)

    await callback.answer()
    USER_FLOW.pop(uid, None)
# Алиасы для текстовых кнопок ReplyKeyboard (ловим ровно такой текст)
@dp.message(F.text == "🌞 Карта дня")
async def kb_day(m: types.Message):
    await cmd_day(m)

@dp.message(F.text == "❓ Да/Нет")
async def kb_ask(m: types.Message):
    await cmd_ask(m)

@dp.message(F.text == "🔮 3 карты")
async def kb_spread3(m: types.Message):
    await cmd_spread3(m)

@dp.message(F.text == "🦋 12 Истин")
async def kb_deep12(m: types.Message):
    await cmd_deep12(m)

@dp.message(F.text == "✝️ Крест")
async def kb_cross(m: types.Message):
    await cmd_cross(m)

@dp.message(F.text == "💞 Совместимость")
async def kb_compat(m: types.Message):
    await cmd_compat(m)

# ========== ВХОД В БОТА ==========
async def run_bot():
    if not TOKEN:
        raise RuntimeError("Нет BOT_TOKEN в переменных окружения (Secrets)")
    me = await bot.get_me()
    print("Logged in as:", me.id, f"@{me.username}")

    # ВАЖНО: правильная индентация здесь (был синтакс-краш)
    await bot.delete_webhook(drop_pending_updates=True)

    print("Bot started")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

__all__ = ["run_bot"]
if __name__ == "__main__":
    import asyncio
    asyncio.run(run_bot())