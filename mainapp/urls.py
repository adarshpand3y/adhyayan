from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    path('courses', views.courses, name="courses"),
    path('services', views.services, name="services"),
    path('about', views.about, name="about"),
    path('album', views.album, name="album"),
    path('login', views.login, name="login"),
    path('logout', views.logout, name="logout"),
    path('course/<slug:slug>', views.course, name="course"),
    path('course/<slug:courseslug>/<slug:lectureslug>', views.lecture, name="lecture"),
]
