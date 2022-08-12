from django.db import models
from .enums import UniversityChoices, MajorChoices, YearChoices
from _helpers import english_day_mapping, persian_day_mapping


class WeekDay(models.Model):
    day = models.IntegerField()

    @property
    def english_day(self):
        return english_day_mapping[self.day]

    @property
    def persian_day(self):
        return persian_day_mapping[self.day]

    def __str__(self):
        return self.english_day


class University(models.Model):
    name = models.CharField(max_length=64, choices=UniversityChoices.choices)

    def __str__(self):
        return self.name


class Major(models.Model):
    name = models.CharField(max_length=64, choices=MajorChoices.choices)

    def __str__(self):
        return self.name


class Professor(models.Model):
    name = models.CharField(max_length=128)
    university = models.ForeignKey(to='University', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Student(models.Model):
    name = models.CharField(max_length=255)
    user_id = models.CharField(max_length=32, db_index=True)
    user_name = models.CharField(max_length=128)
    university = models.ForeignKey(to='University', on_delete=models.CASCADE)
    major = models.ForeignKey(to='Major', on_delete=models.CASCADE)
    year = models.CharField(max_length=8, choices=YearChoices.choices)

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=64, db_index=True)
    professor = models.ForeignKey(to='Professor', on_delete=models.CASCADE)
    days = models.ManyToManyField(to=WeekDay)
    start_hour = models.TimeField()
    end_hour = models.TimeField()
    exam_date = models.DateTimeField()

    def __str__(self):
        return f'{self.code}: {self.name} - {self.professor}'
