from easy_deadline.models import Exersice
from easy_deadline.services import DeadlineCacheService
from _helpers import get_bot
from typing import List
import asyncio


async def send_all_pms(exercises: List[Exersice]):
    bot = get_bot()
    for exercise in exercises:
        asyncio.create_task(bot.send_message(chat_id=exercise.student.user_id))


def send_pm():
    exercises = Exersice.objects.remained()
    service = DeadlineCacheService()
    for exercise in exercises:
        if not service.get_sent_pm(exercise_id=exercise.id):
            service.cache_sent_pm(exercise_id=exercise.id)
