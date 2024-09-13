from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    path('courses', views.courses, name="courses"),
    path('services', views.services, name="services"),
    path('album', views.album_redirect, name="album_redirect"),
    path('album/<int:page>', views.album, name="album"),
    path('login', views.login, name="login"),
    path('logout', views.logout, name="logout"),
    path('course/free/<slug:slug>', views.course, name="free_course"),
    path('course/free/<slug:courseslug>/<slug:lectureslug>', views.lecture, name="free_lecture"),
    path('course/premium/<slug:slug>', views.premium_course, name="paid_course"),
]
