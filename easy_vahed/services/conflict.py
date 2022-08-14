from easy_vahed.models import Course
from typing import Tuple


class ConflictService:
    CONFLICT_CODES = {
        -1: '',
        0: 'تاریخ برگزاری امتحان',
        1: 'روز و ساعت برگزاری کلاس'
    }

    @staticmethod
    def _check_period_hours_conflict(start_hour_1, end_hour_1, start_hour_2, end_hour_2) -> bool:
        if start_hour_1 == start_hour_2 or end_hour_1 == end_hour_2:
            return True

        if start_hour_1 < start_hour_2:
            if end_hour_1 >= start_hour_2:
                return True
        else:
            if end_hour_2 >= start_hour_1:
                return True
        return False

    @classmethod
    def check_conflict(cls, course_1: Course, course_2: Course) -> Tuple[bool, str]:

        if course_1.university != course_2.university:
            return False, cls.CONFLICT_CODES[-1]

        if course_1.exam_date == course_2.exam_date:
            if cls._check_period_hours_conflict(course_1.exam_start, course_1.exam_end,
                                                course_2.exam_start, course_2.exam_end):
                return True, cls.CONFLICT_CODES[0]

        day_conflict = False
        for day_1 in course_1.days.all():
            for day_2 in course_2.days.all():
                if day_1 == day_2:
                    day_conflict = True
                    break
        if not day_conflict:
            return False, cls.CONFLICT_CODES[-1]

        if cls._check_period_hours_conflict(course_1.start_hour, course_1.end_hour,
                                            course_2.start_hour, course_2.end_hour):
            return True, cls.CONFLICT_CODES[1]

        return False, cls.CONFLICT_CODES[-1]
