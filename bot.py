import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackContext, ConversationHandler, CallbackQueryHandler
from secret import BOT_TOKEN
import django
from django.conf import settings

django.setup()

from easy_vahed.models import Student, University, Major, Chart, Course
from easy_vahed.enums import UniversityChoices, MajorChoices, YearChoices
from easy_vahed.services import CacheService, ConflictService

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

    await menu(update, context)

    return settings.STATES['menu']


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


async def menu(update: Update, context: CallbackContext) -> int:
    message = update.message

    keyboard = [
        [
            InlineKeyboardButton('ایزی واحد', callback_data=0)
        ]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await message.reply_text(
        settings.TELEGRAM_MESSAGES['menu'],
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=markup
    )

    return settings.STATES['menu']


async def easy_vahed(update: Update, context: CallbackContext) -> int:
    query = update.callback_query

    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton('انتخاب واحد', callback_data=0)
        ],
        [
            InlineKeyboardButton('دانلود چارت', callback_data=1)
        ]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        settings.TELEGRAM_MESSAGES['easy_vahed'],
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=markup
    )

    return settings.STATES['easy_vahed']


async def choose_courses(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    user_id = query.from_user.id
    selected_course = query.data

    print(selected_course)
    await query.answer()

    service = CacheService()
    selected_courses = service.get_courses(user_id=user_id)

    if selected_course[0] == 'C':
        if str(selected_course[1:]) in selected_courses:
            service.delete_course(user_id=user_id, course=str(selected_course[1:]))
        else:
            service.cache_course(user_id=user_id, course=selected_course[1:])

    if selected_course == '-1':
        return await choose_courses_done(update, context)

    selected_courses = service.get_courses(user_id=user_id)

    print(f'sc: {selected_courses}')
    emoji = '\U0001F351'
    keyboard = [
        [
            InlineKeyboardButton(f'{str(course)}{("", f" {emoji}")[str(course.id) in selected_courses]}',
                                 callback_data=fr'C{course.id}')
        ] for course in Course.objects.all()
    ]

    keyboard += [
        [
            InlineKeyboardButton('تموم شد', callback_data='-1')
        ]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    if selected_course[0] == 'C':
        await query.edit_message_reply_markup(
            reply_markup=markup
        )

    else:
        await query.edit_message_text(
            settings.TELEGRAM_MESSAGES['choose_courses'],
            reply_markup=markup)

    return settings.STATES['choose_courses']


async def choose_courses_done(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id

    cache_service = CacheService()
    service = ConflictService()

    course_ids = cache_service.get_courses(user_id=user_id)
    courses = Course.objects.filter(id__in=course_ids)

    for it_1, course_1 in enumerate(courses):
        for it_2, course_2 in enumerate(courses):
            if it_2 >= it_1:
                break

            has_conflict, reason = service.check_conflict(course_1, course_2)
            if has_conflict:
                await query.edit_message_text(
                    settings.TELEGRAM_MESSAGES['has_conflict'].format(c1=course_1.name, c2=course_2.name, reason=reason)
                )

                return ConversationHandler.END

    await query.edit_message_text(
        settings.TELEGRAM_MESSAGES['has_not_conflict']
    )

    return ConversationHandler.END


async def download_chart(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id

    await query.answer()

    st = Student.objects.get(user_id=user_id)
    chart = Chart.objects.get(university=st.university,
                              major=st.major)

    await context.bot.send_document(
        document=chart.file.file,
        chat_id=user_id
    )

    return settings.STATES['easy_vahed']


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
            ],
            settings.STATES['menu']: [
                CallbackQueryHandler(easy_vahed, pattern=r'^\d+$')
            ],
            settings.STATES['easy_vahed']: [
                CallbackQueryHandler(choose_courses, pattern=r'^0$'),
                CallbackQueryHandler(download_chart, pattern=r'^1$'),
            ],
            settings.STATES['choose_courses']: [
                CallbackQueryHandler(choose_courses, pattern='^.+$')
            ]
        },
        fallbacks=[CommandHandler('start', start)]
    ))
    application.run_polling()


if __name__ == "__main__":
    main()
