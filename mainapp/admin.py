from django.contrib import admin
from .models import AlbumImage, Course, Lecture, PremiumCourse, PremiumLecture, EnrolledCourse, JaapSession, JaapSessionParticipant

# Register your models here.
admin.site.register(AlbumImage)
admin.site.register(Course)
admin.site.register(Lecture)
admin.site.register(PremiumCourse)
admin.site.register(PremiumLecture)
admin.site.register(EnrolledCourse)
admin.site.register(JaapSession)
admin.site.register(JaapSessionParticipant)