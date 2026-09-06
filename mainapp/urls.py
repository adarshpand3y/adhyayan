from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    path('courses', views.courses, name="courses"),
    path('services', views.services, name="services"),
    path('album', views.album_redirect, name="album_redirect"),
    path('album/<int:page>', views.album, name="album"),
    path('signup', views.signup, name="signup"),
    path('login', views.login, name="login"),
    path('logout', views.logout, name="logout"),
    path('course/free/<slug:slug>', views.course, name="free_course"),
    path('course/free/<slug:courseslug>/<slug:lectureslug>', views.lecture, name="free_lecture"),
    path('course/premium/<slug:slug>', views.premium_course, name="paid_course"),
    path('course/premium/<slug:courseslug>/<slug:lectureslug>', views.premium_lecture, name="premium_lecture"),
    path('course/premium/<slug:courseslug>/<slug:lectureslug>/manifest.m3u8', views.premium_lecture_manifest, name="premium_lecture_manifest"),
    path('course/premium/<slug:courseslug>/<slug:lectureslug>/playlist/<path:subpath>', views.premium_lecture_sub_playlist, name="premium_lecture_sub_playlist"),
    path('hls-key/<uuid:lecture_id>', views.hls_key, name="hls_key"),
    path('my-courses', views.my_courses, name="my_courses"),
    path('study/<slug:courseslug>', views.study, name="study"),
    path('study/<slug:courseslug>/<slug:lectureslug>', views.study_lecture, name="study_lecture"),
    path('jaap', views.jaap_sessions, name="jaap_sessions"),
    path('jaap/<uuid:session_id>', views.jaap_room, name="jaap_room"),
    path('jaap/<uuid:session_id>/status', views.jaap_status, name="jaap_status"),
    path('jaap/<uuid:session_id>/increment', views.jaap_increment, name="jaap_increment"),
    path('kundli', views.kundli, name="kundli"),
]
