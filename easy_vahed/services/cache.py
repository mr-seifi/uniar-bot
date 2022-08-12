from django.core.cache import caches
from redis import Redis


class CacheService:
    PREFIX = 'E'
    KEYS = {
        'university': f'{PREFIX}:''{user_id}_UNIVERSITY',
        'major': f'{PREFIX}:''{user_id}_MAJOR',
        'course': f'{PREFIX}:''{user_id}_COURSES',
    }
    EX = 60 * 30

    @staticmethod
    def _get_redis_client() -> Redis:
        return caches['default'].client.get_client()

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

        client.hset(name=self.KEYS['course'].format(user_id=user_id), key=course, value=1)

    def get_courses(self, user_id):
        client = self._get_redis_client()

        return [c.decode() for c in client.hgetall(name=self.KEYS['course'].format(user_id=user_id))]

    def delete_course(self, user_id, course):
        client = self._get_redis_client()

        client.hdel(self.KEYS['course'].format(user_id=user_id),
                    course)
