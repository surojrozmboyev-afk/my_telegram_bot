import logging
import sqlite3
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

# Logging sozlamalari
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# ==================== SOZLAMALAR ====================
BOT_TOKEN = "8830395921:AAF5kuHCfSc_IhAoU4f2rxerVcAVzSND8jA"  # @BotFather tokeni
ADMIN_ID = 7413582067  # Admin Telegram ID raqami

CARD_NUMBER = "9860010127880739"
CARD_HOLDER = "M.O"
MIN_DEPOSIT = 2000

# ==================== MA'LUMOTLAR BAZASI (SQLite) ====================
def init_db():
    conn = sqlite3.connect("bot_base.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance REAL DEFAULT 0,
            referrer_id INTEGER DEFAULT NULL,
            referrals_count INTEGER DEFAULT 0
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS channels (
            channel_username TEXT PRIMARY KEY
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            main_type TEXT,
            sub_cat TEXT,
            title TEXT,
            price REAL,
            min_qty INTEGER DEFAULT 1,
            max_qty INTEGER DEFAULT 999999
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            qty INTEGER,
            link TEXT,
            price REAL,
            status TEXT DEFAULT 'Pending'
        )
    """)

    # Bazani qayta to'ldirish
    c.execute("DELETE FROM categories")

    all_products = [
        # --- TELEGRAM NAKRUTKA ---
        ("Nakrutka", "TG_Obunachi", "👤 Obunachi (♻️ Kafolat-120 Kun)", 15652, 100, 100000),
        ("Nakrutka", "TG_Obunachi", "⚡️👤 Obunachi (⛔️ BEZMINUS)", 17186, 100, 100000),
        ("Nakrutka", "TG_Obunachi", "👤 Obunachi (🎁 super arzon)", 350, 100, 100000),
        ("Nakrutka", "TG_Obunachi", "🌐 👤 Online Obunachi (♻️ Kafolat-30 Kun)", 22175, 100, 100000),
        ("Nakrutka", "TG_Obunachi", "👤 Obunachi (♻️ Kafolat-3-7 Kun)", 741, 100, 100000),
        ("Nakrutka", "TG_Obunachi", "👤 Obunachi (♻️ Kafolat 20-30 Kun)", 6448, 100, 100000),
        ("Nakrutka", "TG_Obunachi", "⚡️ Obunachi (⛔️ BEZMINUS/YANGI)", 12050, 100, 100000),
        ("Nakrutka", "TG_Obunachi", "⚡️ Obunachi (new ⛔️ BEZMINUS-90kunlik ♻️)", 6761, 100, 100000),
        ("Nakrutka", "TG_Obunachi", "👤 Obunachi (⛔️ BEZMINUS-90kunlik ♻️)", 7374, 100, 100000),

        ("Nakrutka", "TG_UzbObunachi", "🇺🇿 O'zbek obunachi (♻️ 14 Kun)", 9054, 100, 50000),
        ("Nakrutka", "TG_UzbObunachi", "🇺🇿 O'zbek obunachi (♻️ 30 Kun)", 12069, 100, 50000),
        ("Nakrutka", "TG_UzbObunachi", "🇺🇿 O'zbek obunachi (♻️ 60 Kun)", 17108, 100, 50000),
        ("Nakrutka", "TG_UzbObunachi", "🇺🇿 O'zbek obunachi (♻️ 90 Kun)", 24162, 100, 50000),

        ("Nakrutka", "TG_PremiumSub", "⭐ Premium a'zolar - 5/7 kun", 18573, 10, 5000),
        ("Nakrutka", "TG_PremiumSub", "⭐ Premium a'zolar - 15/20 kunlik", 35146, 10, 5000),
        ("Nakrutka", "TG_PremiumSub", "⭐ Premium a'zolar - 20 kun", 50866, 10, 5000),
        ("Nakrutka", "TG_PremiumSub", "⭐ Premium a'zolar - 30 kun", 70206, 10, 5000),
        ("Nakrutka", "TG_PremiumSub", "⭐ Premium a'zolar - 30 kun (new)", 75030, 10, 5000),
        ("Nakrutka", "TG_PremiumSub", "⭐ Premium a'zolar - 45 kun", 100886, 10, 5000),
        ("Nakrutka", "TG_PremiumSub", "⭐ Premium a'zolar - 60 kun", 160400, 10, 5000),
        ("Nakrutka", "TG_PremiumSub", "⭐ Premium a'zolar - 90 kun", 210420, 10, 5000),
        ("Nakrutka", "TG_PremiumSub", "⭐ Premium a'zolar - 180 kun", 260440, 10, 5000),

        ("Nakrutka", "TG_Korishlar", "👁️ Ko'rishlar (fast)", 70, 100, 500000),
        ("Nakrutka", "TG_Korishlar", "👁️ Ko'rishlar (tezkor)", 110, 100, 500000),
        ("Nakrutka", "TG_Korishlar", "🟢 [O'zbekiston] Ko'rishlar - lineclood statikasi", 1000, 100, 500000),
        ("Nakrutka", "TG_Korishlar", "👁️ Xabarlarni ko'rish/so'nggi 50 ta post [Super Tez]", 4068, 100, 10000),
        ("Nakrutka", "TG_Korishlar", "👁️ Xabarlarni ko'rish/so'nggi 100 ta post [Super Tez]", 8903, 100, 10000),
        ("Nakrutka", "TG_Korishlar", "👁️ Ko'rishlar [yangi]", 928, 100, 500000),
        ("Nakrutka", "TG_Korishlar", "👁️ Ko'rishlar [arzon]", 50, 100, 500000),
        ("Nakrutka", "TG_Korishlar", "👁️ Ko'rishlar [new]", 300, 100, 500000),

        ("Nakrutka", "TG_ReactArzon", "👍👏🔥🥰🐳 Reaksiyalar ijobiy", 1000, 100, 100000),
        ("Nakrutka", "TG_ReactArzon", "👎💩👏🗿🍌🤮 Reaksiyalar salbiy", 1000, 100, 100000),
        ("Nakrutka", "TG_ReactArzon", "👎 Reaksiyalar salbiy", 1000, 100, 100000),
        ("Nakrutka", "TG_ReactArzon", "🥰 Reaksiyalar ijobiy", 1000, 100, 100000),
        ("Nakrutka", "TG_ReactArzon", "🕊 Reaksiyalar ijobiy", 1000, 100, 100000),
        ("Nakrutka", "TG_ReactArzon", "👏 Reaksiyalar ijobiy", 1000, 100, 100000),
        ("Nakrutka", "TG_ReactArzon", "🐳 Reaksiyalar ijobiy", 1000, 100, 100000),
        ("Nakrutka", "TG_ReactArzon", "🔥 Reaksiyalar ijobiy", 1000, 100, 100000),
        ("Nakrutka", "TG_ReactArzon", "💩 Reaksiyalar salbiy", 1000, 100, 100000),
        ("Nakrutka", "TG_ReactArzon", "🤝 Reaksiyalar ijobiy", 1000, 100, 100000),
        ("Nakrutka", "TG_ReactArzon", "🤩 Reaksiyalar ijobiy", 1000, 100, 100000),
        ("Nakrutka", "TG_ReactArzon", "⚡️ Reaksiyalar ijobiy", 1000, 100, 100000),
        ("Nakrutka", "TG_ReactArzon", "🎉 Reaksiyalar ijobiy", 1000, 100, 100000),

        ("Nakrutka", "TG_ReactTezkor", "⚡️👍👏🔥🥰 Reaksiyalar ijobiy", 2000, 100, 100000),
        ("Nakrutka", "TG_ReactTezkor", "😍🥰💖🐳 Reaksiyalar ijobiy", 2000, 100, 100000),
        ("Nakrutka", "TG_ReactTezkor", "📑 Reaksiya OK qo'li + Ko'rishlar", 2000, 100, 100000),
        ("Nakrutka", "TG_ReactTezkor", "😍 Reaksiya yurak ko'zlari + Ko'rishlar", 2000, 100, 100000),
        ("Nakrutka", "TG_ReactTezkor", "🐳 Reaksiya kiti + Ko'rishlar", 2000, 100, 100000),
        ("Nakrutka", "TG_ReactTezkor", "❤️ Reaksiya yurak + Ko'rishlar", 2000, 100, 100000),
        ("Nakrutka", "TG_ReactTezkor", "💯 Reaksiya 100% + Ko'rishlar", 2000, 100, 100000),
        ("Nakrutka", "TG_ReactTezkor", "🎯 Reaksiya kulgi + Ko'rishlar", 2000, 100, 100000),
        ("Nakrutka", "TG_ReactTezkor", "🕊 Reaksiya qushlari + Ko'rishlar", 2000, 100, 100000),
        ("Nakrutka", "TG_ReactTezkor", "✨ Reaksiya me'yorlar + Ko'rishlar", 2000, 100, 100000),
        ("Nakrutka", "TG_ReactTezkor", "🤡 Reaksiya klassi + Ko'rishlar", 2000, 100, 100000),

        ("Nakrutka", "TG_PostShare", "💫 Post Share (Ulashish)", 806, 100, 50000),
        ("Nakrutka", "TG_PostShare", "↗️ Post Share (Ulashish)", 1074, 100, 50000),

        ("Nakrutka", "TG_Story", "📖 Telegram hikoyasi (Story Ko'rish)", 2534, 100, 50000),
        ("Nakrutka", "TG_Story", "🔄 Telegram hikoyasi -- Share (Repost)", 80700, 10, 5000),
        ("Nakrutka", "TG_Story", "❤️ Telegram hikoyasi yoqadi (Like)", 15806, 100, 50000),

        ("Nakrutka", "TG_BotSub", "🤖 Bot uchun start obunachi", 5500, 100, 50000),

        ("Nakrutka", "TG_Boost", "🚀 Kanal uchun kuchaytirish [7 kun]", 350460, 1, 100),
        ("Nakrutka", "TG_Boost", "🚀 Kanal uchun kuchaytirish [14 kun]", 700600, 1, 100),
        ("Nakrutka", "TG_Boost", "🚀 Kanal uchun kuchaytirish [30 kun]", 1300200, 1, 100),
        ("Nakrutka", "TG_Boost", "🚀 Kanal uchun kuchaytirish [90 kun]", 2500400, 1, 100),

        ("Nakrutka", "TG_PremReact", "⭐️ Premium Reaksiya (1 ta)", 5000, 1, 500),
        ("Nakrutka", "TG_PremReact", "⭐️ Premium Reaksiya (1,2,3)", 6000, 1, 500),
        ("Nakrutka", "TG_PremReact", "⭐️ Premium Reaksiya (1,2,3,4,5)", 7000, 1, 500),
        ("Nakrutka", "TG_PremReact", "⭐️ Premium Reaksiya (1,2,3,4,5,6,7,8,9,10)", 8000, 1, 500),

        # --- INSTAGRAM ---
        ("Nakrutka", "INST_Sub", "👤 Obunachi (arzon)", 7737, 100, 50000),
        ("Nakrutka", "INST_Sub", "👤 Obunachi (♻️ 30kun-kafolat)", 12955, 100, 50000),
        ("Nakrutka", "INST_Sub", "👤 Obunachi ♻️ (365kunlik yangi)", 16510, 100, 50000),
        ("Nakrutka", "INST_Sub", "👤 Obunachi ♻️ (365kunlik V2)", 16204, 100, 50000),

        ("Nakrutka", "INST_Like", "❤️ Like (arzon)", 856, 100, 50000),
        ("Nakrutka", "INST_Like", "❤️ Like [♻️ kafolatliy-365]", 2349, 100, 50000),
        ("Nakrutka", "INST_Like", "❤️ Like (O'rtacha arzon)", 3208, 100, 50000),
        ("Nakrutka", "INST_Like", "❤️ Like [♻️ kafolatliy-365 V2]", 4006, 100, 50000),

        ("Nakrutka", "INST_Views", "📺 Ko'rishlar (Tezkor||yangi⚡️)", 120, 100, 500000),
        ("Nakrutka", "INST_Views", "📺 Ko'rishlar (Tezkor|⚡️NEW)", 320, 100, 500000),

        ("Nakrutka", "INST_Share", "🔄 Post Ulashish", 700, 100, 50000),
        ("Nakrutka", "INST_Save", "📥 Post Saqlash", 1000, 100, 50000),
        ("Nakrutka", "INST_Cmplike", "💬 Comment Like", 1000, 100, 50000),
        ("Nakrutka", "INST_Comms", "📝 Post Comentlar", 8749, 10, 1000),
        ("Nakrutka", "INST_Story", "📸 Istoriya Prosmotr", 3181, 100, 50000),

        # --- YOUTUBE ---
        ("Nakrutka", "YT_Like", "👍 Video Like", 50193, 100, 50000),
        ("Nakrutka", "YT_ShortsLike", "⚡️ Shorts Like", 65240, 100, 50000),
        ("Nakrutka", "YT_Views", "▶️ Video ko'rishlar", 20148, 100, 100000),
        ("Nakrutka", "YT_Views", "▶️ Video ko'rishlar (yangi)", 15799, 100, 100000),
        ("Nakrutka", "YT_ShortsViews", "📱 Shorts Ko'rishlar", 12449, 100, 100000),

        # --- TEKIN XIZMATLAR ---
        ("FREE", "FREE_TG", "🎁 Telegram Obunachi (Tekin max 20 ta)", 0, 1, 20),
        ("FREE", "FREE_TG", "🎁 Telegram Reaksiya (Tekin max 10 ta)", 0, 1, 10),
        ("FREE", "FREE_INST", "🎁 Instagram Video ko'rish (Tekin 100 ta)", 0, 100, 100),

        # --- TELEGRAM PREMIUM ---
        ("TG_PREM", "TG_PREM", "👑 1 oy Premium", 47000, 1, 1),
        ("TG_PREM", "TG_PREM", "👑 3 oy Premium", 165000, 1, 1),
        ("TG_PREM", "TG_PREM", "👑 6 oy Premium", 230000, 1, 1),
        ("TG_PREM", "TG_PREM", "👑 12 oy Premium", 380000, 1, 1),

        # --- TELEGRAM STARS ---
        ("TG_STARS", "TG_STARS", "⭐ 50 ta Stars", 12500, 1, 1),
        ("TG_STARS", "TG_STARS", "⭐ 100 ta Stars", 25000, 1, 1),
        ("TG_STARS", "TG_STARS", "⭐ 250 ta Stars", 62500, 1, 1),
        ("TG_STARS", "TG_STARS", "⭐ 300 ta Stars", 75000, 1, 1),
        ("TG_STARS", "TG_STARS", "⭐ 350 ta Stars", 82500, 1, 1),
        ("TG_STARS", "TG_STARS", "⭐ 500 ta Stars", 125000, 1, 1),
        ("TG_STARS", "TG_STARS", "⭐ 1000 ta Stars", 250000, 1, 1),

        # --- TELEGRAM GIFTS ---
        ("TG_GIFTS", "TG_GIFTS", "💖 Yurak", 4705, 1, 1),
        ("TG_GIFTS", "TG_GIFTS", "🧸 Ayiqcha", 4705, 1, 1),
        ("TG_GIFTS", "TG_GIFTS", "🎁 Sovg'a qutisi", 7175, 1, 1),
        ("TG_GIFTS", "TG_GIFTS", "🌹 Roza / Gul", 7175, 1, 1),
        ("TG_GIFTS", "TG_GIFTS", "💖 Qanotli yurak", 13350, 1, 1),
        ("TG_GIFTS", "TG_GIFTS", "🧸 Ayiqcha va sovg'a", 13350, 1, 1),
        ("TG_GIFTS", "TG_GIFTS", "🧸 Velosipeddagi ayiqcha", 13350, 1, 1),
        ("TG_GIFTS", "TG_GIFTS", "🍾 Shampan idishi", 13350, 1, 1),
        ("TG_GIFTS", "TG_GIFTS", "🎄 Archa", 13350, 1, 1),
        ("TG_GIFTS", "TG_GIFTS", "🧸 Yurak ushlagan ayiqcha", 13350, 1, 1),
        ("TG_GIFTS", "TG_GIFTS", "🚀 Raketa", 13350, 1, 1),
        ("TG_GIFTS", "TG_GIFTS", "💐 Guldasta", 13350, 1, 1),
        ("TG_GIFTS", "TG_GIFTS", "🎂 Tort", 13350, 1, 1),
        ("TG_GIFTS", "TG_GIFTS", "💍 Uzuk", 25700, 1, 1),
        ("TG_GIFTS", "TG_GIFTS", "💎 Olmos", 25700, 1, 1),
        ("TG_GIFTS", "TG_GIFTS", "🏆 Kubok", 25700, 1, 1),

        # --- RAQAMLAR (SERVER 1, 2, 3) ---
        ("Raqam", "Server1", "🇦🇫 Afg'oniston", 8480, 1, 1),
        ("Raqam", "Server1", "🇩🇿 Jazoir", 10720, 1, 1),
        ("Raqam", "Server1", "🇰🇪 Keniya", 8480, 1, 1),
        ("Raqam", "Server1", "🇩🇪 Germaniya", 22440, 1, 1),
        ("Raqam", "Server1", "🇧🇼 Botsvana", 20200, 1, 1),
        ("Raqam", "Server1", "🇧🇩 Bangladesh", 8184, 1, 1),
        ("Raqam", "Server1", "🇴🇲 Ummon", 28920, 1, 1),
        ("Raqam", "Server1", "🇱🇰 SL", 13720, 1, 1),
        ("Raqam", "Server1", "🇹🇷 Turkiya", 20200, 1, 1),
        ("Raqam", "Server1", "🇶🇦 Qatar", 46500, 1, 1),

        ("Raqam", "Server2_P1", "🇺🇿 Oʻzbekiston", 11720, 1, 1),
        ("Raqam", "Server2_P1", "🇰🇬 Qirgʻiziston", 24060, 1, 1),
        ("Raqam", "Server2_P1", "🇦🇿 Ozarbayjon", 26680, 1, 1),
        ("Raqam", "Server2_P1", "🇹🇯 Tojikiston", 15960, 1, 1),
        ("Raqam", "Server2_P1", "🇶🇦 Qatar", 45500, 1, 1),
        ("Raqam", "Server2_P1", "🇧🇭 Bahrayn", 52600, 1, 1),
        ("Raqam", "Server2_P1", "🇦🇪 BAA", 37400, 1, 1),
        ("Raqam", "Server2_P1", "🇵🇸 Falastin", 20200, 1, 1),
        ("Raqam", "Server2_P1", "🇴🇲 Ummon", 29920, 1, 1),

        ("Raqam", "Server2_P2", "🇸🇦 Saudiya Arabistoni", 18580, 1, 1),
        ("Raqam", "Server2_P2", "🇰🇼 Quvayt", 29920, 1, 1),
        ("Raqam", "Server2_P2", "🇮🇶 Iroq", 29300, 1, 1),
        ("Raqam", "Server2_P2", "🇸🇾 Suriya", 19200, 1, 1),
        ("Raqam", "Server2_P2", "🇱🇧 Livan", 19200, 1, 1),
        ("Raqam", "Server2_P2", "🇲🇻 Maldiv orollari", 29300, 1, 1),
        ("Raqam", "Server2_P2", "🇦🇫 Afg'oniston", 12100, 1, 1),
        ("Raqam", "Server2_P2", "🇵🇰 Pokiston", 11290, 1, 1),
        ("Raqam", "Server2_P2", "🇮🇳 Hindiston", 8670, 1, 1),

        ("Raqam", "Server3", "🇺🇸 AQSH", 4000, 1, 1),
    ]

    c.executemany("INSERT INTO categories (main_type, sub_cat, title, price, min_qty, max_qty) VALUES (?, ?, ?, ?, ?, ?)", all_products)
    conn.commit()
    conn.close()

init_db()
# ==================== FSM HOLATLARI ====================
(
    WAITING_RECEIPT,
    WAITING_ORDER_QTY,
    WAITING_ORDER_LINK,
    WAITING_ORDER_CONFIRM,
    WAITING_NEW_PRICE_VAL,
    WAITING_ADD_PANEL_NAME,
    WAITING_ADD_SERV_TITLE,
    WAITING_ADD_SERV_PRICE,
    WAITING_ADD_SERV_MIN,
    WAITING_MANUAL_BAL_USER,
    WAITING_MANUAL_BAL_SUM,
    WAITING_ADD_CHANNEL,
    WAITING_SUPPORT_MSG,
) = range(13)

# ==================== HELPER FUNKSIYALAR ====================
def get_user_db(user_id, referrer_id=None):
    conn = sqlite3.connect("bot_base.db")
    c = conn.cursor()
    c.execute("SELECT user_id, balance, referrer_id, referrals_count FROM users WHERE user_id = ?", (user_id,))
    u = c.fetchone()
    if not u:
        c.execute("INSERT INTO users (user_id, balance, referrer_id, referrals_count) VALUES (?, 0, ?, 0)", (user_id, referrer_id))
        if referrer_id and referrer_id != user_id:
            c.execute("UPDATE users SET balance = balance + 10, referrals_count = referrals_count + 1 WHERE user_id = ?", (referrer_id,))
        conn.commit()
        c.execute("SELECT user_id, balance, referrer_id, referrals_count FROM users WHERE user_id = ?", (user_id,))
        u = c.fetchone()
    conn.close()
    return {"user_id": u[0], "balance": u[1], "referrer_id": u[2], "referrals_count": u[3]}

def get_channels():
    conn = sqlite3.connect("bot_base.db")
    c = conn.cursor()
    c.execute("SELECT channel_username FROM channels")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

async def check_sub(bot, user_id: int) -> bool:
    chans = get_channels()
    for ch in chans:
        try:
            member = await bot.get_chat_member(chat_id=ch, user_id=user_id)
            if member.status in ["left", "kicked"]:
                return False
        except Exception:
            pass
    return True

# ==================== START & ASOSIY MENYU ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    ref_id = int(args[0]) if args and args[0].isdigit() else None
    
    user = get_user_db(user_id, ref_id)

    if not await check_sub(context.bot, user_id):
        chans = get_channels()
        buttons = []
        for ch in chans:
            buttons.append([InlineKeyboardButton(text=f"📢 {ch}", url=f"https://t.me/{ch.replace('@', '')}")])
        buttons.append([InlineKeyboardButton("🔄 Obunani Tekshirish 🔄", callback_data="check_sub")])

        await update.message.reply_text(
            "⚡ **DIQQAT!** Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode="Markdown"
        )
        return

    main_buttons = [
        [KeyboardButton("🛍 Buyurtma berish"), KeyboardButton("📞 Raqam olish")],
        [KeyboardButton("🛒 Buyurtmalar"), KeyboardButton("👥 Referal")],
        [KeyboardButton("💳 Hisobim"), KeyboardButton("💰 Hisobni to'ldirish")],
        [KeyboardButton("☎️ Yordam")]
    ]
    
    if user_id == ADMIN_ID:
        main_buttons.append([KeyboardButton("⚙️ Admin Panel")])

    await update.message.reply_text(
        "✨ **Assalomu aleykum! Xush kelibsiz!** 🚀\n👇 *Kerakli menyulardan birini tanlang:*",
        reply_markup=ReplyKeyboardMarkup(main_buttons, resize_keyboard=True),
        parse_mode="Markdown"
    )

async def check_sub_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if await check_sub(context.bot, query.from_user.id):
        await query.message.delete()
        await start(query, context)
    else:
        await query.message.reply_text("❌ Hali barcha kanallarga obuna bo'lmadingiz!")

# ==================== TEXT HANDLERS ====================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    user = get_user_db(user_id)

    if not await check_sub(context.bot, user_id):
        await start(update, context)
        return

    if text == "🛍 Buyurtma berish":
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("🔥 🛍 Nakrutka", callback_data="cat_nakrutka")],
            [InlineKeyboardButton("⭐ TELEGRAM STARS / PREM 💎", callback_data="menu_tg_stars_prem")],
            [InlineKeyboardButton("🎁 TELEGRAM GIFTS", callback_data="sublist_TG_GIFTS")],
            [InlineKeyboardButton("❌ Yopish", callback_data="close_menu")]
        ])
        await update.message.reply_text("💎 **Xizmat turlari va Bo'limlar:**\n\n👇 *Kerakli kategoriyani tanlang:*", reply_markup=kb, parse_mode="Markdown")

    elif text == "📞 Raqam olish":
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("⚡ Server 1 — Barqaror 🌍", callback_data="numserv_Server1")],
            [InlineKeyboardButton("🚀 Server 2 — Tezkor 🔥", callback_data="numserv_Server2_P1")],
            [InlineKeyboardButton("💡 Server 3 — Tejamkor 💸", callback_data="numserv_Server3")],
            [InlineKeyboardButton("❌ Yopish", callback_data="close_menu")]
        ])
        await update.message.reply_text("📞 **Virtual Raqam Olish Bo'limi:**\n\n📌 *Kerakli Serverni tanlang:*", reply_markup=kb, parse_mode="Markdown")

    elif text == "🛒 Buyurtmalar":
        conn = sqlite3.connect("bot_base.db")
        c = conn.cursor()
        c.execute("SELECT id, title, qty, price, status FROM orders WHERE user_id = ? ORDER BY id DESC LIMIT 10", (user_id,))
        ords = c.fetchall()
        conn.close()

        if not ords:
            await update.message.reply_text("📦 **Sizda hali hech qanday buyurtma mavjud emas!** ⚡", parse_mode="Markdown")
        else:
            msg = "📜 **Sizning oxirgi buyurtmalaringiz:**\n\n"
            for o in ords:
                st_icon = "⏳" if o[4] == "Pending" else ("✅" if o[4] == "Completed" else "❌")
                msg += f"🆔 `#{o[0]}` | **{o[1]}**\n📊 Miqdor: {o[2]} ta | 💰 {o[3]:,.0f} so'm | {st_icon} {o[4]}\n\n"
            await update.message.reply_text(msg, parse_mode="Markdown")

    elif text == "👥 Referal":
        bot_info = await context.bot.get_me()
        ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
        msg = (
            f"👑 **REFERAL DASTURI** 💎\n\n"
            f"🔗 *Sizning shaxsiy havolangiz:*\n`{ref_link}`\n\n"
            f"🎁 **Bonus:** Har bir taklif qilgan do'stingiz uchun **10 so'm** balans beriladi!\n"
            f"📊 *Siz taklif qilgan a'zolar:* **{user['referrals_count']} ta**"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif text == "💳 Hisobim":
        msg = (
            f"👤 **Foydalanuvchi Profili** 👑\n\n"
            f"🆔 **ID:** `{user_id}`\n"
            f"💰 **Balans:** `{user['balance']:,.0f} so'm` ⚡\n"
            f"👥 **Referallaringiz:** `{user['referrals_count']} ta` 💎"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton("💰 Hisobni to'ldirish 💳", callback_data="btn_deposit")]])
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=kb)

    elif text == "💰 Hisobni to'ldirish":
        await deposit_prompt(update, context)

    elif text == "☎️ Yordam":
        await update.message.reply_text(
            "🎙 **YORDAM BO'LIMI** ✨\n\n"
            "💬 Admin bilan bog'lanish uchun xabaringizni, savolingizni yoki muammoingizni shu yerga yozib yuboring.\n\n"
            "✍️ *Xabaringiz to'g'ridan-to'g'ri adminga yetkaziladi:*",
            parse_mode="Markdown"
        )
        return WAITING_SUPPORT_MSG

    elif text == "⚙️ Admin Panel" and user_id == ADMIN_ID:
        await admin_panel_show(update, context)

# ==================== CALLBACK QUERY HANDLERS (MENYULAR va KATEGORIYALAR) ====================
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data == "close_menu":
        await query.message.delete()
        return

    # --- Nakrutka Bo'limlari ---
    elif data == "cat_nakrutka":
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("✈️ Telegram", callback_data="subcat_TG"), InlineKeyboardButton("📸 Instagram", callback_data="subcat_INST")],
            [InlineKeyboardButton("▶️ YouTube", callback_data="subcat_YT"), InlineKeyboardButton("🎁 Tekin Xizmatlar", callback_data="subcat_FREE")],
            [InlineKeyboardButton("⬅️ Orqaga", callback_data="close_menu")]
        ])
        await query.message.edit_text("🔥 **Nakrutka xizmatlari turini tanlang:**", reply_markup=kb, parse_mode="Markdown")

    elif data == "subcat_TG":
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("👤 Obunachilar (Kafolatli)", callback_data="sublist_TG_Obunachi")],
            [InlineKeyboardButton("🇺🇿 O'zbek Obunachilar", callback_data="sublist_TG_UzbObunachi")],
            [InlineKeyboardButton("⭐ Premium Obunachilar", callback_data="sublist_TG_PremiumSub")],
            [InlineKeyboardButton("👁️ Ko'rishlar (Views)", callback_data="sublist_TG_Korishlar")],
            [InlineKeyboardButton("👍 Reaksiyalar (Arzon)", callback_data="sublist_TG_ReactArzon")],
            [InlineKeyboardButton("⚡ Reaksiyalar (Tezkor)", callback_data="sublist_TG_ReactTezkor")],
            [InlineKeyboardButton("💫 Post Share", callback_data="sublist_TG_PostShare")],
            [InlineKeyboardButton("📖 Story Xizmatlari", callback_data="sublist_TG_Story")],
            [InlineKeyboardButton("🤖 Bot uchun Start", callback_data="sublist_TG_BotSub")],
            [InlineKeyboardButton("🚀 Kanal Boost", callback_data="sublist_TG_Boost")],
            [InlineKeyboardButton("⭐️ Premium Reaksiya", callback_data="sublist_TG_PremReact")],
            [InlineKeyboardButton("⬅️ Orqaga", callback_data="cat_nakrutka")]
        ])
        await query.message.edit_text("✈️ **Telegram Nakrutka Bo'limlari:**", reply_markup=kb, parse_mode="Markdown")

    elif data == "subcat_INST":
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("👤 Obunachi (Followers)", callback_data="sublist_INST_Sub")],
            [InlineKeyboardButton("❤️ Likelar", callback_data="sublist_INST_Like")],
            [InlineKeyboardButton("📺 Ko'rishlar (Reels/Views)", callback_data="sublist_INST_Views")],
            [InlineKeyboardButton("🔄 Post Ulashish", callback_data="sublist_INST_Share")],
            [InlineKeyboardButton("📥 Saqlashlar", callback_data="sublist_INST_Save")],
            [InlineKeyboardButton("💬 Comment Likelar", callback_data="sublist_INST_Cmplike")],
            [InlineKeyboardButton("📝 Izohlar (Comments)", callback_data="sublist_INST_Comms")],
            [InlineKeyboardButton("📸 Istoriya Ko'rishlar", callback_data="sublist_INST_Story")],
            [InlineKeyboardButton("⬅️ Orqaga", callback_data="cat_nakrutka")]
        ])
        await query.message.edit_text("📸 **Instagram Xizmatlari:**", reply_markup=kb, parse_mode="Markdown")

    elif data == "subcat_YT":
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("👍 Video Likelar", callback_data="sublist_YT_Like")],
            [InlineKeyboardButton("⚡ Shorts Likelar", callback_data="sublist_YT_ShortsLike")],
            [InlineKeyboardButton("▶️ Video Ko'rishlar", callback_data="sublist_YT_Views")],
            [InlineKeyboardButton("📱 Shorts Ko'rishlar", callback_data="sublist_YT_ShortsViews")],
            [InlineKeyboardButton("⬅️ Orqaga", callback_data="cat_nakrutka")]
        ])
        await query.message.edit_text("▶️ **YouTube Xizmatlari:**", reply_markup=kb, parse_mode="Markdown")

    elif data == "subcat_FREE":
        conn = sqlite3.connect("bot_base.db")
        c = conn.cursor()
        c.execute("SELECT id, title FROM categories WHERE main_type = 'FREE'")
        prods = c.fetchall()
        conn.close()

        buttons = [[InlineKeyboardButton(p[1], callback_data=f"buyprod_{p[0]}")] for p in prods]
        buttons.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="cat_nakrutka")])
        await query.message.edit_text("🎁 **Tekin Xizmatlar Ro'yxati:**", reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")

    elif data == "menu_tg_stars_prem":
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("👑 TELEGRAM PREMIUM", callback_data="sublist_TG_PREM")],
            [InlineKeyboardButton("⭐ TELEGRAM STARS", callback_data="sublist_TG_STARS")],
            [InlineKeyboardButton("⬅️ Orqaga", callback_data="close_menu")]
        ])
        await query.message.edit_text("⭐ **Telegram Stars va Premium Bo'limi:**", reply_markup=kb, parse_mode="Markdown")

    # --- Subkategoriya xizmatlarini ko'rsatish ---
    elif data.startswith("sublist_"):
        sub_cat = data.replace("sublist_", "")
        conn = sqlite3.connect("bot_base.db")
        c = conn.cursor()
        c.execute("SELECT id, title, price FROM categories WHERE sub_cat = ?", (sub_cat,))
        prods = c.fetchall()
        conn.close()

        buttons = []
        for p in prods:
            price_str = f" - {p[2]:,.0f} so'm" if p[2] > 0 else " - Bepul"
            buttons.append([InlineKeyboardButton(f"{p[1]}{price_str}", callback_data=f"buyprod_{p[0]}")])
        buttons.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="close_menu")])

        await query.message.edit_text("📜 **Mavjud Xizmatlar Ro'yxati:**\n\n👇 *Kerakli xizmatni tanlang:*", reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")

    # --- Server Raqamlari Ro'yxatlari ---
    elif data.startswith("numserv_"):
        server = data.replace("numserv_", "")
        
        if server == "Server1":
            conn = sqlite3.connect("bot_base.db")
            c = conn.cursor()
            c.execute("SELECT id, title, price FROM categories WHERE sub_cat = 'Server1'")
            prods = c.fetchall()
            conn.close()

            buttons = []
            for p in prods:
                buttons.append([InlineKeyboardButton(f"🌍 {p[1]} — {p[2]:,.0f} so'm", callback_data=f"buyprod_{p[0]}")])
            buttons.append([InlineKeyboardButton("❌ Yopish", callback_data="close_menu")])

            msg = "🌍 **Server 1 — Mavjud davlatlar**\n\n💡 *Davlatni tanlang va raqam xarid qiling:*"
            await query.message.edit_text(msg, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")

        elif server == "Server2_P1":
            conn = sqlite3.connect("bot_base.db")
            c = conn.cursor()
            c.execute("SELECT id, title, price FROM categories WHERE sub_cat = 'Server2_P1'")
            prods = c.fetchall()
            conn.close()

            buttons = []
            for p in prods:
                buttons.append([InlineKeyboardButton(f"🌍 {p[1]} — {p[2]:,.0f} so'm", callback_data=f"buyprod_{p[0]}")])
            buttons.append([InlineKeyboardButton("Keyingisi ➡️ (2/2)", callback_data="numserv_Server2_P2")])
            buttons.append([InlineKeyboardButton("❌ Yopish", callback_data="close_menu")])

            msg = "🚀 **Server 2 — 1-sahifa (1/2)**\n\n💡 *Davlatni tanlang va raqam xarid qiling:*"
            await query.message.edit_text(msg, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")

        elif server == "Server2_P2":
            conn = sqlite3.connect("bot_base.db")
            c = conn.cursor()
            c.execute("SELECT id, title, price FROM categories WHERE sub_cat = 'Server2_P2'")
            prods = c.fetchall()
            conn.close()

            buttons = []
            for p in prods:
                buttons.append([InlineKeyboardButton(f"🌍 {p[1]} — {p[2]:,.0f} so'm", callback_data=f"buyprod_{p[0]}")])
            buttons.append([InlineKeyboardButton("⬅️ Orqaga (1/2)", callback_data="numserv_Server2_P1")])
            buttons.append([InlineKeyboardButton("❌ Yopish", callback_data="close_menu")])

            msg = "🚀 **Server 2 — 2-sahifa (2/2)**\n\n💡 *Davlatni tanlang va raqam xarid qiling:*"
            await query.message.edit_text(msg, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")

        elif server == "Server3":
            conn = sqlite3.connect("bot_base.db")
            c = conn.cursor()
            c.execute("SELECT id, title, price FROM categories WHERE sub_cat = 'Server3'")
            prods = c.fetchall()
            conn.close()

            buttons = []
            for p in prods:
                buttons.append([InlineKeyboardButton(f"🌍 {p[1]} — {p[2]:,.0f} so'm", callback_data=f"buyprod_{p[0]}")])
            buttons.append([InlineKeyboardButton("❌ Yopish", callback_data="close_menu")])

            msg = "💡 **Server 3 — Mavjud davlatlar:**\n\n📋 *Sotib olmoqchi bo'lgan davlatni tanlang:*"
            await query.message.edit_text(msg, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")

            # --- Mahsulot yoki Raqam Tanlanganda ---
    elif data.startswith("buyprod_"):
        prod_id = int(data.replace("buyprod_", ""))
        conn = sqlite3.connect("bot_base.db")
        c = conn.cursor()
        c.execute("SELECT id, main_type, sub_cat, title, price, min_qty, max_qty FROM categories WHERE id = ?", (prod_id,))
        p = c.fetchone()
        conn.close()

        if not p:
            await query.message.edit_text("❌ Mahsulot topilmadi!")
            return

        context.user_data["order_prod_id"] = p[0]
        context.user_data["order_title"] = p[3]
        context.user_data["order_unit_price"] = p[4]
        context.user_data["order_min_qty"] = p[5]
        context.user_data["order_max_qty"] = p[6]
        context.user_data["order_type"] = p[1]

        # 1) Virtual Raqam bo'lsa:
        if p[1] == "Raqam":
            context.user_data["order_qty"] = 1
            context.user_data["order_link"] = "Virtual Raqam"
            
            warning_msg = (
                f"🛒 **Raqam xarid qilish**\n\n"
                f"🌍 **Mamlakat:** {p[3]}\n"
                f"💰 **Narxi:** {p[4]:,.0f} so'm\n\n"
                f"⚠️ *Bizda faqat tayyor akkauntlar bo'lgani uchun faqat Telegram uchun raqamlar olishingiz mumkin.*\n\n"
                f"✅ Raqam ichiga kirganingizdan so'ng 2 bosqichli tekshiruvni birdaniga yoqmang❗️ (rasm ism user) o'zgartirmang. Faqat Gmail'ni o'zgartiring.\n\n"
                f"‼️ Raqamga Telegramning rasmiy ilovasi orqaliy kod yubormang!\n"
                f"[🏧telegraph 🚮puls] ilovalaridan foydalanish tavsiya etiladi!"
            )
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton("✅ Tasdiqlash", callback_data="confirm_num_buy")],
                [InlineKeyboardButton("⬅️ Orqaga", callback_data="close_menu")]
            ])
            await query.message.edit_text(warning_msg, reply_markup=kb, parse_mode="Markdown")

        # 2) Telegram Stars / Prem / Gifts bo'lsa:
        elif p[1] in ["TG_PREM", "TG_STARS", "TG_GIFTS"]:
            context.user_data["order_qty"] = 1
            context.user_data["order_total_price"] = p[4]
            await query.message.edit_text(
                f"📦 **{p[3]}**\n💰 Narxi: `{p[4]:,.0f} so'm`\n\n"
                f"✍️ Iltimos, sovg'a/ulashilishi kerak bo'lgan Telegram **username** yoki **havolani** yuboring (Masalan: `@username`):",
                parse_mode="Markdown"
            )
            return WAITING_ORDER_LINK

        # 3) Nakrutka yoki Bepul xizmatlar bo'lsa:
        else:
            if p[5] == p[6]: # Bir dona bo'lsa
                context.user_data["order_qty"] = p[5]
                context.user_data["order_total_price"] = p[4]
                await query.message.edit_text(
                    f"📌 **{p[3]}**\n\n✍️ Iltimos, buyurtma uchun **havola (link)** yoki **username** yuboring:",
                    parse_mode="Markdown"
                )
                return WAITING_ORDER_LINK
            else:
                await query.message.edit_text(
                    f"📦 **{p[3]}**\n"
                    f"💰 1000 ta narxi: `{p[4]:,.0f} so'm`\n"
                    f"📊 Minimal: `{p[5]}` ta | Maksimal: `{p[6]}` ta\n\n"
                    f"✍️ **Qancha miqdorda buyurtma qilmoqchisiz?** Raqamda kiriting:",
                    parse_mode="Markdown"
                )
                return WAITING_ORDER_QTY

    # --- Raqam Tasdiqlanganda ---
    elif data == "confirm_num_buy":
        title = context.user_data.get("order_title", "Raqam")
        price = context.user_data.get("order_unit_price", 0)
        u = get_user_db(user_id)

        if u["balance"] < price:
            await query.message.edit_text(f"❌ **Mablag' yetarli emas!**\n\nSizning balansingiz: `{u['balance']:,.0f} so'm`\nKerakli summa: `{price:,.0f} so'm`", parse_mode="Markdown")
            return

        # Balansdan ayirish
        conn = sqlite3.connect("bot_base.db")
        c = conn.cursor()
        c.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (price, user_id))
        c.execute("INSERT INTO orders (user_id, title, qty, link, price, status) VALUES (?, ?, 1, 'Virtual Raqam', ?, 'Pending')", (user_id, title, price))
        order_id = c.lastrowid
        conn.commit()
        conn.close()

        await query.message.edit_text("✅ **Buyurtmangiz qabul qilindi!**\n\n📩 Admin tez orada raqam ma'lumotlarini lichkangizga yuboradi.", parse_mode="Markdown")

        # Adminga UPALOVKA qilib yuborish
        admin_msg = (
            f"📥 **YANGI RAQAM ZAKAZI! (UPAKOVKA)**\n\n"
            f"🆔 **Order ID:** `#{order_id}`\n"
            f"👤 **Buyurtmachi:** [{query.from_user.full_name}](tg://user?id={user_id}) (`{user_id}`)\n"
            f"🌍 **Raqam turi:** `{title}`\n"
            f"💰 **To'langan summa:** `{price:,.0f} so'm`\n\n"
            f"⚡️ *Iltimos, ushbu foydalanuvchi lichkasiga raqam va kodni taqdim eting!*"
        )
        kb_admin = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("✅ Bajarildi deb belgilash", callback_data=f"doneorder_{order_id}")]
        ])
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg, reply_markup=kb_admin, parse_mode="Markdown")

        # ==================== ORDER FSM HANDLERS ====================
async def process_order_qty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text.isdigit():
        await update.message.reply_text("❌ **Iltimos, faqat raqam kiriting!** (Masalan: 1000)", parse_mode="Markdown")
        return WAITING_ORDER_QTY

    qty = int(text)
    min_q = context.user_data.get("order_min_qty", 1)
    max_q = context.user_data.get("order_max_qty", 999999)
    unit_price = context.user_data.get("order_unit_price", 0)

    if qty < min_q or qty > max_q:
        await update.message.reply_text(f"❌ **Miqdor xato!**\n\nMinimal: `{min_q}` ta\nMaksimal: `{max_q}` ta", parse_mode="Markdown")
        return WAITING_ORDER_QTY

    total_price = (qty / 1000.0) * unit_price if unit_price > 0 else 0
    context.user_data["order_qty"] = qty
    context.user_data["order_total_price"] = total_price

    await update.message.reply_text(
        f"📊 Miqdor: `{qty}` ta\n💰 Jami narx: `{total_price:,.0f} so'm`\n\n"
        f"✍️ **Endi buyurtma uchun havola (link) yoki username yuboring:**",
        parse_mode="Markdown"
    )
    return WAITING_ORDER_LINK


async def process_order_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text.strip()
    context.user_data["order_link"] = link

    title = context.user_data.get("order_title")
    qty = context.user_data.get("order_qty", 1)
    total_price = context.user_data.get("order_total_price", 0)

    msg = (
        f"🛒 **BUYURTMANI TASDIQLASH** ⚡️\n\n"
        f"📌 **Xizmat:** `{title}`\n"
        f"📊 **Miqdor:** `{qty}` ta\n"
        f"🔗 **Havola/User:** `{link}`\n"
        f"💰 **Umumiy narx:** `{total_price:,.0f} so'm`\n\n"
        f"⚠️ Buyurtmani tasdiqlaysizmi?"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("✅ Ha, tasdiqlayman", callback_data="confirm_final_order")],
        [InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_order")]
    ])

    await update.message.reply_text(msg, reply_markup=kb, parse_mode="Markdown")
    return WAITING_ORDER_CONFIRM


async def process_order_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "cancel_order":
        await query.message.edit_text("❌ **Buyurtma bekor qilindi.**", parse_mode="Markdown")
        return ConversationHandler.END

    if query.data == "confirm_final_order":
        user_id = query.from_user.id
        title = context.user_data.get("order_title")
        qty = context.user_data.get("order_qty", 1)
        link = context.user_data.get("order_link")
        total_price = context.user_data.get("order_total_price", 0)

        u = get_user_db(user_id)

        if u["balance"] < total_price:
            await query.message.edit_text(
                f"❌ **Mablag' yetarli emas!**\n\n"
                f"💰 Sizning balansingiz: `{u['balance']:,.0f} so'm`\n"
                f"💳 Kerakli summa: `{total_price:,.0f} so'm`\n\n"
                f"Iltimos, hisobingizni to'ldiring!",
                parse_mode="Markdown"
            )
            return ConversationHandler.END

        # Balansdan ayirish va Bazaga saqlash
        conn = sqlite3.connect("bot_base.db")
        c = conn.cursor()
        c.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (total_price, user_id))
        c.execute("INSERT INTO orders (user_id, title, qty, link, price, status) VALUES (?, ?, ?, ?, ?, 'Pending')",
                  (user_id, title, qty, link, total_price))
        order_id = c.lastrowid
        conn.commit()
        conn.close()

        await query.message.edit_text(
            f"✅ **Buyurtmangiz muvaffaqiyatli qabul qilindi!**\n\n"
            f"🆔 Order ID: `#{order_id}`\n"
            f"⚡️ Buyurtmangiz tez orada ko'rib chiqiladi.",
            parse_mode="Markdown"
        )

        # Adminga UPAKOVKA qilib yuborish
        admin_msg = (
            f"📥 **YANGI BUYURTMA! (UPAKOVKA)** 📦\n\n"
            f"🆔 **Order ID:** `#{order_id}`\n"
            f"👤 **Buyurtmachi:** [{query.from_user.full_name}](tg://user?id={user_id}) (`{user_id}`)\n"
            f"📦 **Xizmat:** `{title}`\n"
            f"📊 **Miqdor:** `{qty}` ta\n"
            f"🔗 **Havola/User:** `{link}`\n"
            f"💰 **Jami narxi:** `{total_price:,.0f} so'm`\n"
        )
        kb_admin = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("✅ Bajarildi deb belgilash", callback_data=f"doneorder_{order_id}")]
        ])
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg, reply_markup=kb_admin, parse_mode="Markdown")

        return ConversationHandler.END

# ==================== HISOBNI TO'LDIRISH (DEPOSIT) ====================
async def deposit_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        f"💳 **HISOBNI TO'LDIRISH**\n\n"
        f"📌 *Karta raqam:* `{CARD_NUMBER}`\n"
        f"👤 *Ega:* **{CARD_HOLDER}**\n"
        f"⚠️ *Minimal to'lov:* `{MIN_DEPOSIT:,.0f} so'm`\n\n"
        f"📸 To'lovni amalga oshirgach, **to'lov chekining rasmini (skrinshot)** yoki **faylini** shu yerga yuboring:"
    )
    if update.message:
        await update.message.reply_text(msg, parse_mode="Markdown")
    else:
        await update.callback_query.message.reply_text(msg, parse_mode="Markdown")
    return WAITING_RECEIPT


async def process_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.full_name

    photo = update.message.photo[-1] if update.message.photo else None
    document = update.message.document if update.message.document else None

    if not photo and not document:
        await update.message.reply_text("❌ Iltimos, to'lov chekining **rasmini** yoki **faylini** yuboring!")
        return WAITING_RECEIPT

    await update.message.reply_text("✅ **Chekingiz qabul qilindi va adminga yuborildi.** Text/xabar kelishini kuting!")

    caption_text = (
        f"💳 **YANGI TO'LOV CHEKI!**\n\n"
        f"👤 **Foydalanuvchi:** [{user_name}](tg://user?id={user_id}) (`{user_id}`)\n"
        f"⏳ To'lovni tekshirib, foydalanuvchi balansini to'ldiring:"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("➕ Balans qo'shish", callback_data=f"addbaluser_{user_id}")],
        [InlineKeyboardButton("❌ Rad etish", callback_data=f"rejectdep_{user_id}")]
    ])

    if photo:
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo.file_id, caption=caption_text, reply_markup=kb, parse_mode="Markdown")
    elif document:
        await context.bot.send_document(chat_id=ADMIN_ID, document=document.file_id, caption=caption_text, reply_markup=kb, parse_mode="Markdown")

    return ConversationHandler.END


# ==================== YORDAM XABARI HANDLERI ====================
async def process_support_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.full_name
    msg_text = update.message.text

    admin_msg = (
        f"☎️ **YORDAM BO'LIMIDAN YANGI XABAR!**\n\n"
        f"👤 **Kimdan:** [{user_name}](tg://user?id={user_id}) (`{user_id}`)\n"
        f"💬 **Xabar:**\n{msg_text}"
    )

    await context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg, parse_mode="Markdown")
    await update.message.reply_text("✅ **Xabaringiz adminga yetkazildi!** Tez orada javob beriladi.", parse_mode="Markdown")
    return ConversationHandler.END

# ==================== ADMIN PANEL HANDLERS ====================
async def admin_panel_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect("bot_base.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*), SUM(balance) FROM users")
    u_stats = c.fetchone()
    total_users = u_stats[0] or 0
    total_balance = u_stats[1] or 0.0

    c.execute("SELECT COUNT(*) FROM orders WHERE status = 'Pending'")
    pending_orders = c.fetchone()[0] or 0

    c.execute("SELECT COUNT(*) FROM orders WHERE status = 'Completed'")
    completed_orders = c.fetchone()[0] or 0
    conn.close()

    msg = (
        f"⚙️ **ADMIN PANEL MONITORING** 👑\n\n"
        f"👥 **Jami foydalanuvchilar:** `{total_users} ta`\n"
        f"💰 **Foydalanuvchilar umumiy balansi:** `{total_balance:,.0f} so'm`\n\n"
        f"⏳ **Kutayotgan buyurtmalar:** `{pending_orders} ta`\n"
        f"✅ **Bajarilgan buyurtmalar:** `{completed_orders} ta`\n"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("➕ Balans qo'shish (Manual)", callback_data="admin_add_bal_manual")],
        [InlineKeyboardButton("📢 Majburiy Obuna Kanallari", callback_data="admin_channels_list")],
        [InlineKeyboardButton("❌ Yopish", callback_data="close_menu")]
    ])

    if update.message:
        await update.message.reply_text(msg, reply_markup=kb, parse_mode="Markdown")
    else:
        await update.callback_query.message.edit_text(msg, reply_markup=kb, parse_mode="Markdown")


async def admin_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # --- Buyurtmani Bajarildi deb belgilash ---
    if data.startswith("doneorder_"):
        order_id = int(data.replace("doneorder_", ""))
        conn = sqlite3.connect("bot_base.db")
        c = conn.cursor()
        c.execute("SELECT user_id, title FROM orders WHERE id = ?", (order_id,))
        ord_info = c.fetchone()
        
        if ord_info:
            c.execute("UPDATE orders SET status = 'Completed' WHERE id = ?", (order_id,))
            conn.commit()
            conn.close()

            await query.message.edit_text(f"✅ **Buyurtma #{order_id} bajarildi deb belgilandi!**")
            
            # Xaridorga xabar yuborish
            try:
                await context.bot.send_message(
                    chat_id=ord_info[0],
                    text=f"🎉 **Buyurtmangiz bajarildi!**\n\n🆔 Buyurtma ID: `#{order_id}`\n📦 Xizmat: `{ord_info[1]}`\n\nXizmatimizdan foydalanganingiz uchun rahmat! 🚀",
                    parse_mode="Markdown"
                )
            except Exception:
                pass
        else:
            conn.close()

    # --- Balans Qo'shish / Rad Etish ---
    elif data.startswith("addbaluser_"):
        target_id = int(data.replace("addbaluser_", ""))
        context.user_data["target_bal_user"] = target_id
        await query.message.reply_text(f"✍️ **User ID:** `{target_id}`\n\nQancha summa qo'shmoqchisiz? Raqamda kiriting:", parse_mode="Markdown")
        return WAITING_MANUAL_BAL_SUM

    elif data.startswith("rejectdep_"):
        target_id = int(data.replace("rejectdep_", ""))
        await query.message.edit_text("❌ To'lov cheki rad etildi.")
        try:
            await context.bot.send_message(chat_id=target_id, text="❌ **Siz yuborgan to'lov cheki admin tomonidan rad etildi!** Iltimos, to'g'ri chek yuboring.", parse_mode="Markdown")
        except Exception:
            pass

    elif data == "admin_add_bal_manual":
        await query.message.reply_text("✍️ Balans qo'shmoqchi bo'lgan foydalanuvchining **Telegram ID** raqamini kiriting:", parse_mode="Markdown")
        return WAITING_MANUAL_BAL_USER

    elif data == "admin_channels_list":
        chans = get_channels()
        msg = "📢 **MAJBURIY OBUNA KANALLARI:**\n\n"
        for ch in chans:
            msg += f"• `{ch}`\n"
        if not chans:
            msg += "Hali kanallar qo'shilmagan."

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("➕ Kanal qo'shish", callback_data="admin_add_chan")],
            [InlineKeyboardButton("⬅️ Orqaga", callback_data="admin_panel_back")]
        ])
        await query.message.edit_text(msg, reply_markup=kb, parse_mode="Markdown")

    elif data == "admin_add_chan":
        await query.message.reply_text("✍️ Qo'shmoqchi bo'lgan kanalingiz username'ini kiriting (masalan: `@kanal_username`):", parse_mode="Markdown")
        return WAITING_ADD_CHANNEL

    elif data == "admin_panel_back":
        await admin_panel_show(update, context)


async def process_manual_bal_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text.isdigit():
        await update.message.reply_text("❌ Iltimos, to'g'ri Telegram ID kiriting!")
        return WAITING_MANUAL_BAL_USER
    context.user_data["target_bal_user"] = int(text)
    await update.message.reply_text("✍️ Qancha summa qo'shmoqchisiz? (so'mda):", parse_mode="Markdown")
    return WAITING_MANUAL_BAL_SUM


async def process_manual_bal_sum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    try:
        sum_val = float(text)
    except ValueError:
        await update.message.reply_text("❌ Iltimos, faqat raqam kiriting!")
        return WAITING_MANUAL_BAL_SUM

    target_id = context.user_data.get("target_bal_user")
    conn = sqlite3.connect("bot_base.db")
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (sum_val, target_id))
    conn.commit()
    conn.close()

    await update.message.reply_text(f"✅ User ID `{target_id}` balansiga `{sum_val:,.0f} so'm` muvaffaqiyatli qo'shildi!", parse_mode="Markdown")

    try:
        await context.bot.send_message(
            chat_id=target_id,
            text=f"🎉 **Hisobingiz to'ldirildi!**\n\n💰 Balansingizga `{sum_val:,.0f} so me` qo'shildi.",
            parse_mode="Markdown"
        )
    except Exception:
        pass

    return ConversationHandler.END


async def process_add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ch_name = update.message.text.strip()
    if not ch_name.startswith("@"):
        ch_name = "@" + ch_name

    conn = sqlite3.connect("bot_base.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO channels (channel_username) VALUES (?)", (ch_name,))
        conn.commit()
        await update.message.reply_text(f"✅ `{ch_name}` kanali muvaffaqiyatli qo'shildi!\n\n⚠️ Botni ushbu kanalda **ADMIN** qilishni unutmang!", parse_mode="Markdown")
    except Exception:
        await update.message.reply_text("❌ Bu kanal allaqachon mavjud!")
    finally:
        conn.close()

    return ConversationHandler.END


# ==================== MAIN ISHGA TUSHIRISH ====================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # ConvHandler 1: Zakaz Olish
    order_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(handle_callback, pattern="^buyprod_"),
            CallbackQueryHandler(handle_callback, pattern="^confirm_num_buy$")
        ],
        states={
            WAITING_ORDER_QTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_order_qty)],
            WAITING_ORDER_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_order_link)],
            WAITING_ORDER_CONFIRM: [CallbackQueryHandler(process_order_confirm, pattern="^(confirm_final_order|cancel_order)$")],
        },
        fallbacks=[],
    )

    # ConvHandler 2: Deposit Chek
    deposit_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^💰 Hisobni to'ldirish$"), deposit_prompt),
            CallbackQueryHandler(deposit_prompt, pattern="^btn_deposit$")
        ],
        states={
            WAITING_RECEIPT: [MessageHandler(filters.PHOTO | filters.Document.ALL, process_receipt)],
        },
        fallbacks=[],
    )

    # ConvHandler 3: Admin & Manual Balans
    admin_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(admin_callback_handler, pattern="^admin_add_bal_manual$"),
            CallbackQueryHandler(admin_callback_handler, pattern="^addbaluser_"),
            CallbackQueryHandler(admin_callback_handler, pattern="^admin_add_chan$"),
        ],
        states={
            WAITING_MANUAL_BAL_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_manual_bal_user)],
            WAITING_MANUAL_BAL_SUM: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_manual_bal_sum)],
            WAITING_ADD_CHANNEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_add_channel)],
        },
        fallbacks=[],
    )

    # ConvHandler 4: Support (Yordam)
    support_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^☎️ Yordam$"), handle_text)
        ],
        states={
            WAITING_SUPPORT_MSG: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_support_msg)],
        },
        fallbacks=[],
    )

    # Handlerlarni ro'yxatdan o'tkazish
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_sub_cb, pattern="^check_sub$"))

    app.add_handler(order_handler)
    app.add_handler(deposit_handler)
    app.add_handler(admin_handler)
    app.add_handler(support_handler)

    app.add_handler(CallbackQueryHandler(admin_callback_handler, pattern="^(doneorder_|rejectdep_|admin_channels_list|admin_panel_back)"))
    app.add_handler(CallbackQueryHandler(handle_callback))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Bot muvaffaqiyatli ishga tushdi! 🚀")
    app.run_polling()


if __name__ == "__main__":
    main()