from django.shortcuts import render, get_object_or_404, redirect
from .models import AlbumImage, Course, Lecture, PremiumCourse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.
def index(request):
    images = AlbumImage.objects.all().order_by('-id')[:4]
    return render(request, "index.html", {"images": images})

def courses(reqeust):
    courses = Course.objects.all()
    premium_courses = PremiumCourse.objects.all()
    return render(reqeust, "courses.html", {"courses": courses, "premium_courses": premium_courses})

def course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    lectures = Lecture.objects.filter(course=course)
    return render(request, "course.html", {"course": course, "lectures": lectures, "first_slug": lectures[0].slug})

def premium_course(request, slug):
    course = get_object_or_404(PremiumCourse, slug=slug)
    description_array = [point for point in course.description.split("\r\n") if point]
    elligibility_array = [point for point in course.elligibility.split("\r\n") if point]
    key_highlights_array = [point for point in course.key_highlights.split("\r\n") if point]
    why_learn_array = [point for point in course.why_learn.split("\r\n") if point]
    print(elligibility_array)
    context = {
        "course": course,
        "description_array": description_array,
        "elligibility_array": elligibility_array,
        "key_highlights_array": key_highlights_array,
        "why_learn_array": why_learn_array
    }
    return render(request, "premiumcourse.html", context)

def lecture(request, courseslug, lectureslug):
    lecture = Lecture.objects.get(slug=lectureslug)
    course = Course.objects.get(slug=courseslug)
    lectures_in_course = Lecture.objects.filter(course=course)
    context = {"course": course, "lecture": lecture, "lectures": lectures_in_course}
    return render(request, "lecture.html", context)

def services(request):
    return render(request, "services.html")

def album_redirect(request):
    return redirect("/album/1")

def album(request, page=1):
    IMAGES_PER_PAGE = 12
    images = AlbumImage.objects.all().order_by('-id')
    p = Paginator(images, IMAGES_PER_PAGE)
    try:
        images = p.get_page(page)
    except PageNotAnInteger:
        images = p.page(1)
    except EmptyPage:
        images = p.page(p.num_pages)
    context = {
        'images': images,
        'current_page': page,
        'last_page': p.num_pages
        }
    return render(request, "album.html", context)

def login(request):
    return render(request, "login.html")

def logout(request):
    return render(request, "logout.html")