from _helpers import BaseCacheService
from django.utils import timezone


class CacheService(BaseCacheService):
    PREFIX = 'E'
    KEYS = {
        'university': f'{PREFIX}:''{user_id}_UNIVERSITY',
        'major': f'{PREFIX}:''{user_id}_MAJOR',
        'course': f'{PREFIX}:''{user_id}_COURSES',
    }
    EX = 60 * 30

    def cache_university(self, user_id, university):
        client = self._get_redis_client()

        client.set(name=self.KEYS['university'].format(user_id=user_id),
                   value=university,
                   ex=self.EX)

    def get_university(self, user_id) -> int:
        client = self._get_redis_client()

        return int(client.get(name=self.KEYS['university'].format(user_id=user_id)) or b'-1')

    def cache_major(self, user_id, major):
        client = self._get_redis_client()

        client.set(name=self.KEYS['major'].format(user_id=user_id),
                   value=major,
                   ex=self.EX)

    def get_major(self, user_id) -> int:
        client = self._get_redis_client()

        return int(client.get(name=self.KEYS['major'].format(user_id=user_id)) or b'-1')

    def cache_course(self, user_id, course):
        client = self._get_redis_client()

        client.hset(name=self.KEYS['course'].format(user_id=user_id),
                    key=course,
                    value=timezone.now().timestamp())

    def get_courses(self, user_id):
        client = self._get_redis_client()

        return [c.decode() for c in client.hgetall(name=self.KEYS['course'].format(user_id=user_id))]

    def get_course_created(self, user_id, course):
        client = self._get_redis_client()

        return float(client.hget(name=self.KEYS['course'].format(user_id=user_id), key=course).decode())

    def delete_courses(self, user_id, *courses):
        if not courses:
            return

        client = self._get_redis_client()
        client.hdel(self.KEYS['course'].format(user_id=user_id),
                    *courses)

    def delete_non_used_courses(self, user_id):
        now = timezone.now().timestamp()
        courses = [course for course in self.get_courses(user_id=user_id)
                   if now - self.get_course_created(user_id=user_id, course=course) >= self.EX]

        self.delete_courses(user_id, *courses)
