from django.shortcuts import render, get_object_or_404
from .models import Course, Lecture

# Create your views here.
def index(request):
    return render(request, "index.html")

def courses(reqeust):
    courses = Course.objects.all()
    return render(reqeust, "courses.html", {"courses": courses})

def course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    lectures = Lecture.objects.filter(course=course)
    return render(request, "course.html", {"course": course, "lectures": lectures, "first_slug": lectures[0].slug})

def lecture(request, courseslug, lectureslug):
    lecture = Lecture.objects.get(slug=lectureslug)
    course = Course.objects.get(slug=courseslug)
    lectures_in_course = Lecture.objects.filter(course=course)
    context = {"course": course, "lecture": lecture, "lectures": lectures_in_course}
    return render(request, "lecture.html", context)

def services(request):
    return render(request, "services.html")

def about(request):
    return render(request, "about.html")

def album(request):
    return render(request, "album.html")

def login(request):
    return render(request, "login.html")

def logout(request):
    return render(request, "logout.html")