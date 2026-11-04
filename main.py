from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import sqlite3
from datetime import datetime
import time

BOT_TOKEN = "8935782381:AAE1W7_NNhtOu1-0uJFFqLEQPkw8_dZJcsQ"

# ==================== SETTINGS ====================
OWNER_USERNAME = "@v099c"
MOD_OWNER_USERNAME = "@v98c4"

# ⭐ ပြောင်းလဲထားသော Channel အသစ်များ
CHANNEL_1 = "@Mango_Channel_1"
CHANNEL_1_LINK = "https://t.me/Mango_Channel_1"
CHANNEL_2 = "@Story_H346"
CHANNEL_2_LINK = "https://t.me/Story_H346"

# Potato Mod Link (တိုက်ရိုက် ဖွင့်မည့် Link)
POTATO_MOD_LINK = "https://t.me/Story_H346/51"

DB_FILE = "mango_bot.db"


# ==================== DATABASE ====================

def init_db():
    """Database နဲ့ Table ဖန်တီးခြင်း"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS verified_users (
            user_id INTEGER PRIMARY KEY,
            verified_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_verified(user_id):
    """Join ပြီးသား User ကို သိမ်းဆည်းခြင်း"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO verified_users (user_id, verified_at)
        VALUES (?, ?)
    """, (user_id, datetime.now().isoformat()))
    conn.commit()
    conn.close()


# ==================== JOIN CHECK ====================

async def check_joined(context, user_id):
    """User က Channel ၂ ခုလုံး Join ထား/မထား စစ်ဆေးခြင်း"""
    not_joined = []
    for channel in [CHANNEL_1, CHANNEL_2]:
        try:
            member = await context.bot.get_chat_member(channel, user_id)
            if member.status in ["left", "kicked"]:
                not_joined.append(channel)
        except Exception as e:
            print(f"Channel check error ({channel}): {e}")
            not_joined.append(channel)
    return not_joined


# ==================== MESSAGE FUNCTIONS ====================

async def send_new_message(query, text, reply_markup=None, disable_preview=False):
    """Message အသစ် ပို့ခြင်း (အဟောင်း မပျောက်စေရ)
    parse_mode လုံးဝ မသုံးပါ (Error မတက်စေရ)"""
    try:
        await query.message.reply_text(
            text=text,
            reply_markup=reply_markup,
            disable_web_page_preview=disable_preview,
        )
    except Exception as e:
        print(f"Send error: {e}")


# ==================== START COMMAND ====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start နှိပ်ရင် ရွေးချယ်စရာများ ပြသခြင်း"""
    
    keyboard = [
        [InlineKeyboardButton("👑 Bot Owner", callback_data="bot_owner")],
        [InlineKeyboardButton("📥 Mod ဒေါင်းလုပ်", callback_data="download_mod")],
        [InlineKeyboardButton("🛡️ Mod Owner", callback_data="mod_owner")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "🤖 မင်္ဂလာပါ! Bot မှ ကြိုဆိုပါတယ်။\n\n"
        "အောက်ပါ ရွေးချယ်စရာများထဲမှ တစ်ခုကို နှိပ်ပါ-\n\n"
        "👑 Bot Owner - Bot ပိုင်ရှင်ကို ဆက်သွယ်ရန်\n"
        "📥 Mod ဒေါင်းလုပ် - Mod များ ဒေါင်းလုပ် ရယူရန်\n"
        "🛡️ Mod Owner - Mod ပိုင်ရှင်ကို ဆက်သွယ်ရန်"
    )
    
    await update.message.reply_text(text, reply_markup=reply_markup)


# ==================== CALLBACK HANDLER ====================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inline Button နှိပ်တိုင်း ကိုင်တွယ်ခြင်း"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # ========== Bot Owner ==========
    if query.data == "bot_owner":
        text = (
            "👑 Bot Owner\n\n"
            "Bot ပိုင်ရှင်နှင့် ဆက်သွယ်ရန်-\n\n"
            f"📩 {OWNER_USERNAME}"
        )
        await send_new_message(query, text)
        return
    
    # ========== Mod Owner ==========
    if query.data == "mod_owner":
        text = (
            "🛡️ Mod Owner\n\n"
            "Mod ပိုင်ရှင်နှင့် ဆက်သွယ်ရန်-\n\n"
            f"📩 {MOD_OWNER_USERNAME}"
        )
        await send_new_message(query, text)
        return
    
    # ========== Mod ဒေါင်းလုပ် ==========
    if query.data == "download_mod":
        not_joined = await check_joined(context, user_id)
        
        if not_joined:
            # Join မလုပ်ရသေးရင် Error ပြသ
            keyboard = [
                [InlineKeyboardButton("📢 Channel 1 Join", url=CHANNEL_1_LINK)],
                [InlineKeyboardButton("📢 Channel 2 Join", url=CHANNEL_2_LINK)],
                [InlineKeyboardButton("✅ Join ပြီးပါပြီ - စစ်ဆေးမည်", callback_data="check_join")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            text = (
                "⚠️ Error!\n\n"
                "Mod ဒေါင်းလုပ် ရယူရန် အောက်ပါ Channel ၂ ခုလုံးကို "
                "အရင်ဆုံး Join ပေးပါ။\n\n"
                f"1️⃣ Channel 1: {CHANNEL_1}\n"
                f"2️⃣ Channel 2: {CHANNEL_2}\n\n"
                "Join ပြီးရင် 'Join ပြီးပါပြီ - စစ်ဆေးမည်' ကို နှိပ်ပါ။"
            )
            await send_new_message(query, text, reply_markup)
        else:
            # Join ပြီးသားဆိုရင် ကျေးဇူးတင်စာ ပြသ
            save_verified(user_id)
            await show_download_page(query)
        return
    
    # ========== Join စစ်ဆေးခြင်း ==========
    if query.data == "check_join":
        not_joined = await check_joined(context, user_id)
        
        if not_joined:
            keyboard = [
                [InlineKeyboardButton("📢 Channel 1 Join", url=CHANNEL_1_LINK)],
                [InlineKeyboardButton("📢 Channel 2 Join", url=CHANNEL_2_LINK)],
                [InlineKeyboardButton("✅ Join ပြီးပါပြီ - စစ်ဆေးမည်", callback_data="check_join")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            missing = ""
            if CHANNEL_1 in not_joined:
                missing += f"❌ Channel 1 ({CHANNEL_1}) ကို မဖောက်ရသေးပါ\n"
            if CHANNEL_2 in not_joined:
                missing += f"❌ Channel 2 ({CHANNEL_2}) ကို မဖောက်ရသေးပါ\n"
            
            text = (
                "⚠️ Error!\n\n"
                "Channel ၂ ခုလုံး Join မဖြစ်သေးပါဘူး။\n\n"
                f"{missing}\n"
                "ပြန်လည် Join ပြီး ထပ်စစ်ပါ။"
            )
            await send_new_message(query, text, reply_markup)
        else:
            save_verified(user_id)
            await show_download_page(query)
        return


async def show_download_page(query):
    """Mod ဒေါင်းလုပ် စာမျက်နှာ ပြသခြင်း"""
    text = (
        "✅ ကျေးဇူးတင်ပါသည်!\n\n"
        "သင်သည် အောင်မြင်စွာ Join ပြီးပါပြီ။\n\n"
        "🥔 Potato Mod အား စတင်ဒေါင်းလို့ရပါပြီ။\n\n"
        "အောက်ပါ ခလုတ်ကို နှိပ်ပြီး ဒေါင်းလုပ်ပါ-"
    )
    # ⭐ url= သုံးထားတဲ့အတွက် နှိပ်လိုက်တာနဲ့ တိုက်ရိုက် Link ဖွင့်သွားမည်
    keyboard = [
        [InlineKeyboardButton("📥 Potato Mod ဒေါင်းလုပ်", url=POTATO_MOD_LINK)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_new_message(query, text, reply_markup, disable_preview=True)


# ==================== AUTO REPLY (ဖျက်ထားပြီး) ====================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Auto Reply များ အားလုံး ဖျက်ထားပါသည်"""
    pass


# ==================== MAIN ====================

def main():
    init_db()
    
    print("=" * 40)
    print("Bot စတင်နေပါသည်...")
    print(f"Channel 1: {CHANNEL_1}")
    print(f"Channel 2: {CHANNEL_2}")
    print("=" * 40)
    
    retry_count = 0
    
    while True:
        try:
            # Application အသစ် တည်ဆောက်ခြင်း (တစ်ခါ run တိုင်း အသစ်)
            app = Application.builder().token(BOT_TOKEN).build()
            
            app.add_handler(CommandHandler("start", start_command))
            app.add_handler(CallbackQueryHandler(button_handler))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
            
            retry_count = 0
            print(f"✅ Bot လည်ပတ်နေပါသည်... ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
            
            # Bot ရပ်သွားတဲ့အထိ run နေမယ်
            app.run_polling(drop_pending_updates=True)
            
        except Exception as e:
            retry_count += 1
            print(f"❌ Error တက်ပါသည်: {e}")
            print(f"🔄 ၅ စက္ကန့်နေပြီး ပြန် Run မည်... (အကြိမ် {retry_count})")
            time.sleep(5)
            continue


if __name__ == "__main__":
    main()