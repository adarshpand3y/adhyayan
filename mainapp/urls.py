from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    path('courses', views.courses, name="courses"),
    path('course/<slug:slug>', views.course, name="course"),
    path('course/<slug:courseslug>/<slug:lectureslug>', views.lecture, name="lecture"),
]
