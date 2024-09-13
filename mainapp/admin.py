from django.contrib import admin
from .models import AlbumImage, Course, Lecture, PremiumCourse

# Register your models here.
admin.site.register(AlbumImage)
admin.site.register(Course)
admin.site.register(Lecture)
admin.site.register(PremiumCourse)