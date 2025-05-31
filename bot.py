# -*- coding: utf-8 -*-
import logging
from typing import Dict, List, Tuple
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

# ------ إعدادات التسجيل ------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ------ بيانات المسؤول ------
ADMIN_USERNAME = "isawaftah"  # يوزر المسؤول

# ------ حالات المحادثة ------
(
    MAIN_MENU,
    BROWSE_CATEGORIES,
    VIEW_CATEGORY,
    VIEW_STORY,
    ADMIN_PANEL,
    ADD_CATEGORY,
    DELETE_CATEGORY,
    ADD_STORY,
    EDIT_STORY,
    DELETE_STORY
) = range(10)

# ------ بيانات القصص ------
SEX_STORIES = {
    "رومانسية": [
        {"title": "ليلة عاصفة", "content": "كانت الليلية ممطرة...", "rating": 4.5, "views": 1200},
        {"title": "حب ممنوع", "content": "في أحد الأحياء الراقية...", "rating": 4.2, "views": 980}
    ],
    "سادية": [
        {"title": "السيطرة الكاملة", "content": "بدأ الأمر كعلاقة عادية...", "rating": 4.8, "views": 1500}
    ]
}

# ------ تخزين مؤقت للبيانات أثناء التعديل ------
user_data = {}

# ------ لوحات المفاتيح ------
def get_main_keyboard(user):
    keyboard = [
        [KeyboardButton("📚 تصفح الأقسام")],
        [KeyboardButton("🔥 الأكثر شهرة")]
    ]
    if is_admin(user):
        keyboard.append([KeyboardButton("👑 لوحة التحكم")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("📊 الإحصائيات")],
        [KeyboardButton("📂 إدارة الأقسام")],
        [KeyboardButton("📖 إدارة القصص")],
        [KeyboardButton("🏠 الرئيسية")]
    ], resize_keyboard=True)

def get_categories_keyboard(user):
    keyboard = []
    for category in SEX_STORIES.keys():
        keyboard.append([KeyboardButton(f"📂 {category}")])
    if is_admin(user):
        keyboard.append([
            KeyboardButton("➕ إضافة قسم"),
            KeyboardButton("🗑️ حذف قسم")
        ])
    keyboard.append([KeyboardButton("🏠 الرئيسية")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ------ لوحات المفاتيح الإنلاين ------
def get_main_menu(user):
    buttons = [
        [InlineKeyboardButton("📚 تصفح الأقسام", callback_data="browse_categories")],
        [InlineKeyboardButton("🔥 الأكثر شهرة", callback_data="top_stories")]
    ]
    if is_admin(user):
        buttons.append([InlineKeyboardButton("👑 لوحة التحكم", callback_data="admin_panel")])
    return InlineKeyboardMarkup(buttons)

def get_admin_actions(category=None, story_title=None):
    buttons = []
    if category:
        buttons.append([
            InlineKeyboardButton("➕ إضافة قصة", callback_data=f"add_story_{category}"),
            InlineKeyboardButton("✏️ تعديل القسم", callback_data=f"edit_category_{category}"),
            InlineKeyboardButton("🗑️ حذف القسم", callback_data=f"delete_category_{category}")
        ])
    if story_title:
        buttons.append([
            InlineKeyboardButton("✏️ تعديل القصة", callback_data=f"edit_story_{story_title}"),
            InlineKeyboardButton("🗑️ حذف القصة", callback_data=f"delete_story_{story_title}")
        ])
    buttons.append([InlineKeyboardButton("🏠 الرئيسية", callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)

# ------ وظائف مساعدة ------
def is_admin(user):
    return user.username == ADMIN_USERNAME

# ------ معالجات الأوامر ------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"مرحبًا {user.first_name} في بوت القصص المثيرة! 🍷\n\n"
        "يمكنك تصفح القصص حسب الأقسام أو الاطلاع على الأكثر شهرة.",
        reply_markup=get_main_keyboard(user)
    )
    return MAIN_MENU

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user
    
    if text == "🏠 الرئيسية":
        await update.message.reply_text(
            "القائمة الرئيسية:",
            reply_markup=get_main_keyboard(user)
        )
        return MAIN_MENU
        
    elif text == "📚 تصفح الأقسام":
        await update.message.reply_text(
            "اختر قسمًا:",
            reply_markup=get_categories_keyboard(user)
        )
        return BROWSE_CATEGORIES
        
    elif text == "👑 لوحة التحكم" and is_admin(user):
        await update.message.reply_text(
            "👑 لوحة تحكم المسؤول",
            reply_markup=get_admin_keyboard()
        )
        return ADMIN_PANEL
        
    elif text.startswith("📂 ") and text[3:] in SEX_STORIES:
        category = text[3:]
        stories = SEX_STORIES[category]
        message = f"📂 قسم: {category}\n\n"
        for story in stories:
            message += f"📖 {story['title']} ⭐{story['rating']} 👀{story['views']}\n"
        
        await update.message.reply_text(
            message,
            reply_markup=get_admin_actions(category) if is_admin(user) else None
        )
        return VIEW_CATEGORY
        
    elif text == "➕ إضافة قسم" and is_admin(user):
        await update.message.reply_text(
            "أرسل اسم القسم الجديد:",
            reply_markup=ReplyKeyboardRemove()
        )
        return ADD_CATEGORY
        
    elif text == "🗑️ حذف قسم" and is_admin(user):
        keyboard = []
        for category in SEX_STORIES.keys():
            keyboard.append([KeyboardButton(f"حذف {category}")])
        keyboard.append([KeyboardButton("إلغاء")])
        
        await update.message.reply_text(
            "اختر قسمًا لحذفه:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return DELETE_CATEGORY
        
    return MAIN_MENU

# ------ معالجات المسؤول ------
async def add_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_category = update.message.text
    if new_category in SEX_STORIES:
        await update.message.reply_text(
            "هذا القسم موجود بالفعل!",
            reply_markup=get_admin_keyboard()
        )
    else:
        SEX_STORIES[new_category] = []
        await update.message.reply_text(
            f"تمت إضافة قسم {new_category} بنجاح!",
            reply_markup=get_admin_keyboard()
        )
    return ADMIN_PANEL

async def delete_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "إلغاء":
        await update.message.reply_text(
            "تم الإلغاء",
            reply_markup=get_admin_keyboard()
        )
        return ADMIN_PANEL
    
    category = update.message.text.replace("حذف ", "")
    if category in SEX_STORIES:
        del SEX_STORIES[category]
        await update.message.reply_text(
            f"تم حذف قسم {category} بنجاح!",
            reply_markup=get_admin_keyboard()
        )
    else:
        await update.message.reply_text(
            "القسم غير موجود!",
            reply_markup=get_admin_keyboard()
        )
    return ADMIN_PANEL

# ------ معالجات الاستدعاء ------
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user = query.from_user
    
    if data == "main_menu":
        await query.edit_message_text(
            "القائمة الرئيسية:",
            reply_markup=get_main_menu(user)
        )
        return MAIN_MENU
        
    elif data == "admin_panel" and is_admin(user):
        await query.edit_message_text(
            "👑 لوحة تحكم المسؤول",
            reply_markup=get_admin_actions()
        )
        return ADMIN_PANEL
        
    elif data.startswith("add_story_") and is_admin(user):
        category = data.replace("add_story_", "")
        user_data[user.id] = {"action": "add_story", "category": category}
        await query.edit_message_text(
            f"أرسل عنوان القصة الجديدة لقسم {category}:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("إلغاء", callback_data=f"category_{category}")]
            ])
        )
        return ADD_STORY

# ------ إعداد التطبيق ------
def main():
    application = Application.builder().token("7919070032:AAEj9kYtVfLwhk54SeCCS-FaDBvoB3LDX0I").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages),
                CallbackQueryHandler(button_click)
            ],
            BROWSE_CATEGORIES: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages),
                CallbackQueryHandler(button_click)
            ],
            ADMIN_PANEL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages),
                CallbackQueryHandler(button_click)
            ],
            ADD_CATEGORY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_category)
            ],
            DELETE_CATEGORY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, delete_category)
            ],
            ADD_STORY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_story)
            ]
        },
        fallbacks=[CommandHandler('start', start)]
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
