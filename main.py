
import asyncio
import json
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================================
# التوكن تبعك
# ================================
bot = Bot(token="8567697709:AAEgJBn6zW1kBYAjVoRuVGB09YaxhLvmMq0", parse_mode="Markdown")
dp = Dispatcher()

# ================================
# تحميل الإعدادات من الملف
# ================================
def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

def save_config(data):
    with open("config.json", "w") as f:
        json.dump(data, f, indent=4)

config = load_config()

OWNER = config["owner_id"]
CHANNEL = config["channel"]

# ================================
# دالة تعديل نجوم واتساب → تلغرام
# ================================
def fix_whatsapp(text):
    new = ""
    skip = False
    for i, ch in enumerate(text):
        if ch == "*" and not skip:
            new += "**"
            skip = True
        elif ch == "*" and skip:
            skip = False
        else:
            new += ch
    return new

# ================================
# لوحة التحكم الرئيسية
# ================================
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="إدارة مجموعات الفوروورد", callback_data="fw_manage")],
        [InlineKeyboardButton(text="إدارة مجموعات النسخ", callback_data="cp_manage")],
        [InlineKeyboardButton(text="تحديد وضع الرسائل", callback_data="mode_menu")],
        [InlineKeyboardButton(text="تغيير وقت إعادة النشر", callback_data="time_set")],
        [InlineKeyboardButton(text="عرض الإعدادات الحالية", callback_data="show_config")]
    ])

# ================================
# قوائم فرعية
# ================================
def mode_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="عشوائي", callback_data="mode_random")],
        [InlineKeyboardButton(text="حسب رسائلي", callback_data="mode_manual")],
        [InlineKeyboardButton(text="رجوع", callback_data="back_main")]
    ])

def back_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="رجوع", callback_data="back_main")]
    ])

# ================================
# أمر /start
# ================================
@dp.message(Command("start"))
async def start_cmd(msg: types.Message):
    if msg.from_user.id != OWNER:
        return await msg.answer("هاد البوت للمالك فقط ⚠️")

    await msg.answer("أهلا براء 🔥🤖\nجاهز لاستقبال أوامرك ✨", reply_markup=main_menu())

# ================================
# استقبال رسالة ونشرها مباشرة
# ================================
@dp.message()
async def handle_message(msg: types.Message):
    if msg.from_user.id != OWNER:
        return

    text = msg.text or ""
    text = fix_whatsapp(text)

    config = load_config()

    # النشر للقناة
    await bot.send_message(config["channel"], text)

    # فورورد للمجموعات
    for g in config["forward_groups"]:
        try:
            await bot.forward_message(g, config["channel"], msg.message_id + 1)
        except:
            pass

    # نسخ نص للمجموعات
    for g in config["copy_groups"]:
        try:
            await bot.send_message(g, text)
        except:
            pass

# ================================
# لوحات التحكم Callback Queries
# ================================
@dp.callback_query()
async def menu_callbacks(call: types.CallbackQuery):
    if call.from_user.id != OWNER:
        return await call.answer("ممنوع")

    config = load_config()

    if call.data == "back_main":
        await call.message.edit_text("القائمة الرئيسية:", reply_markup=main_menu())

    elif call.data == "mode_menu":
        await call.message.edit_text("اختر الوضع:", reply_markup=mode_menu())

    elif call.data == "mode_random":
        config["mode"] = "random"
        save_config(config)
        await call.message.edit_text("تم التغيير لوضع: عشوائي", reply_markup=main_menu())

    elif call.data == "mode_manual":
        config["mode"] = "manual"
        save_config(config)
        await call.message.edit_text("تم التغيير لوضع: يدوي", reply_markup=main_menu())

    elif call.data == "show_config":
        text = f"""
🔧 إعداداتك يا براء:

📢 القناة: {config['channel']}

📨 مجموعات الفوروورد:
{config['forward_groups']}

📨 مجموعات النسخ:
{config['copy_groups']}

⏱️ وقت إعادة النشر كل: {config['resend_hours']} ساعة

🎲 وضع الرسائل: {config['mode']}
"""
        await call.message.edit_text(text, reply_markup=back_button())

# ================================
# إعادة نشر كل فترة (رسائل عشوائية)
# ================================
async def auto_resend():
    await bot.send_message(OWNER, "⏳ نظام إعادة النشر اشتغل…")

    while True:
        await asyncio.sleep(load_config()["resend_hours"] * 3600)

        config = load_config()
        messages = await bot.get_chat_history(config["channel"], limit=50)

        msg = random.choice(messages)

        for g in config["copy_groups"]:
            try:
                await bot.send_message(g, msg.text or "")
            except:
                pass

# ================================
# تشغيل البوت
# ================================
async def main():
    asyncio.create_task(auto_resend())
    await dp.start_polling(bot)

asyncio.run(main())
