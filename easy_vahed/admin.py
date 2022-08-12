from django.contrib import admin
from .models import University, Major, Chart, Professor, Student, Course


admin.site.register(University)
admin.site.register(Major)
admin.site.register(Chart)
admin.site.register(Professor)
admin.site.register(Student)
admin.site.register(Course)
