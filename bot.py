import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackContext, ConversationHandler, CallbackQueryHandler
from secret import BOT_TOKEN
import django
from django.conf import settings

django.setup()

from easy_vahed.models import Student, University, Major
from easy_vahed.enums import UniversityChoices, MajorChoices, YearChoices
from easy_vahed.services import CacheService

# Enable logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


async def start(update: Update, context: CallbackContext):
    message = update.message
    user_id = message.from_user.id

    is_registered = False
    if Student.objects.filter(user_id=user_id).exists():
        is_registered = True

    if not is_registered:
        return await blind_start(update, context)

    return await message.reply_text(
        'OKK!'
    )


async def blind_start(update: Update, context: CallbackContext) -> int:
    message = update.message

    keyboard = [
        [
            InlineKeyboardButton(getattr(UniversityChoices, university.name).label, callback_data=university.id)
        ] for university in University.objects.all()
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await message.reply_text(
        settings.TELEGRAM_MESSAGES['blind_start'],
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=markup
    )

    return settings.STATES['register_university']


async def register_university(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    user_id = query.from_user.id

    await query.answer()

    service = CacheService()
    service.cache_university(user_id=user_id,
                             university=query.data)

    keyboard = [
        [
            InlineKeyboardButton(getattr(MajorChoices, major.name).label, callback_data=major.id)
        ] for major in Major.objects.all()
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        settings.TELEGRAM_MESSAGES['register_university'],
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=markup
    )

    return settings.STATES['register_major']


async def register_major(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    user_id = query.from_user.id

    await query.answer()

    service = CacheService()
    service.cache_major(user_id=user_id,
                        major=query.data)

    keyboard = [
        [
            InlineKeyboardButton(label, callback_data=year)
        ] for year, label in YearChoices.choices
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        settings.TELEGRAM_MESSAGES['register_major'],
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=markup
    )

    return settings.STATES['register_done']


async def register_done(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    user_id = query.from_user.id

    await query.answer()

    service = CacheService()
    university_id = service.get_university(user_id=user_id)
    major_id = service.get_major(user_id=user_id)
    year = query.data

    if university_id == -1 or major_id == -1:
        await query.edit_message_text(
            settings.TELEGRAM_MESSAGES['expired']
        )
        return ConversationHandler.END

    university = University.objects.get(id=university_id)
    major = Major.objects.get(id=major_id)

    Student.objects.create(
        name=query.from_user.full_name,
        user_id=user_id,
        user_name=query.from_user.username,
        university=university,
        major=major,
        year=year,
    )

    await query.edit_message_text(
        settings.TELEGRAM_MESSAGES['register_done'],
        parse_mode=ParseMode.MARKDOWN,
    )

    return ConversationHandler.END




def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            settings.STATES['register_university']: [
                CallbackQueryHandler(register_university, pattern=r'^\d+$')
            ],
            settings.STATES['register_major']: [
                CallbackQueryHandler(register_major, pattern=r'^\d+$')
            ],
            settings.STATES['register_done']: [
                CallbackQueryHandler(register_done, pattern=r'^\d+$')
            ]
        },
        fallbacks=[CommandHandler('start', start)]
    ))
    application.run_polling()


if __name__ == "__main__":
    main()
