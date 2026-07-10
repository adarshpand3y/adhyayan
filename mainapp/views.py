from dotenv import load_dotenv, dotenv_values
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.core import signing
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import AlbumImage, Course, EnrolledCourse, Lecture, PremiumCourse, PremiumLecture, JaapSession, JaapSessionParticipant
from .r2 import get_master_manifest, get_sub_playlist_with_presigned_segments
from django.db.models import Count, Sum
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


load_dotenv()
_env = dotenv_values()

# Create your views here.
def index(request):
    images = AlbumImage.objects.all().order_by('-id')[:4]
    return render(request, "index.html", {"images": images})

def courses(request):
    courses = Course.objects.all()
    premium_courses = PremiumCourse.objects.all()

    enrolled_ids = set()
    if request.user.is_authenticated:
        enrolled_ids = set(EnrolledCourse.objects.filter(user=request.user).values_list('course_id', flat=True))
        
    return render(request, "courses.html", {
        "courses": courses,
        "premium_courses": premium_courses,
        "enrolled_ids": enrolled_ids,
    })

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
    is_enrolled = request.user.is_authenticated and EnrolledCourse.objects.filter(user=request.user, course=course).exists()
    context = {
        "course": course,
        "description_array": description_array,
        "elligibility_array": elligibility_array,
        "key_highlights_array": key_highlights_array,
        "why_learn_array": why_learn_array,
        "is_enrolled": is_enrolled,
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

def premium_lecture(request, courseslug, lectureslug):
    course = get_object_or_404(PremiumCourse, slug=courseslug)
    lecture = get_object_or_404(PremiumLecture, slug=lectureslug, course=course)
    lectures = PremiumLecture.objects.filter(course=course)
    context = {
        'course': course,
        'lecture': lecture,
        'lectures': lectures,
        'manifest_url': f"/course/premium/{courseslug}/{lectureslug}/manifest.m3u8",
    }
    return render(request, 'premium_lecture.html', context)


def premium_lecture_manifest(request, courseslug, lectureslug):
    course = get_object_or_404(PremiumCourse, slug=courseslug)
    lecture = get_object_or_404(PremiumLecture, slug=lectureslug, course=course)
    sub_playlist_base_url = f"/course/premium/{courseslug}/{lectureslug}/playlist"
    manifest = get_master_manifest(lecture.r2_key, sub_playlist_base_url)
    return HttpResponse(manifest, content_type='application/vnd.apple.mpegurl')


def premium_lecture_sub_playlist(request, courseslug, lectureslug, subpath):
    course = get_object_or_404(PremiumCourse, slug=courseslug)
    lecture = get_object_or_404(PremiumLecture, slug=lectureslug, course=course)
    base_dir = lecture.r2_key.rsplit('/', 1)[0]
    playlist_key = f"{base_dir}/{subpath}"
    key_url = None
    if lecture.aes_key:
        token = signing.dumps({'id': str(lecture.id)})
        key_url = request.build_absolute_uri(f'/hls-key/{lecture.id}?token={token}')
    manifest = get_sub_playlist_with_presigned_segments(playlist_key, key_url=key_url)
    return HttpResponse(manifest, content_type='application/vnd.apple.mpegurl')


def hls_key(request, lecture_id):
    if not request.user.is_authenticated:
        return HttpResponse(status=403)
    token = request.GET.get('token', '')
    try:
        data = signing.loads(token, max_age=int(_env.get('HLS_EXPIRY', 18000)))
        if str(data.get('id')) != str(lecture_id):
            return HttpResponse(status=403)
    except Exception:
        return HttpResponse(status=403)
    lecture = get_object_or_404(PremiumLecture, id=lecture_id)
    if not lecture.aes_key:
        return HttpResponse(status=404)
    return HttpResponse(bytes.fromhex(lecture.aes_key), content_type='application/octet-stream')

def signup(request):
    if request.user.is_authenticated:
        return redirect('my_courses')
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        if not name or not email or not password:
            messages.error(request, 'All fields are required.')
        elif password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        elif len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
        elif not any(c.isupper() for c in password):
            messages.error(request, 'Password must contain at least one uppercase letter.')
        elif not any(c.islower() for c in password):
            messages.error(request, 'Password must contain at least one lowercase letter.')
        elif not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            messages.error(request, 'Password must contain at least one special character.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists.')
        else:
            user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
            auth_login(request, user)
            return redirect('my_courses')
    return render(request, "signup.html")

def login(request):
    if request.user.is_authenticated:
        return redirect('my_courses')
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            next_url = request.GET.get('next', '')
            return redirect(next_url if next_url else 'my_courses')
        else:
            messages.error(request, 'Invalid email or password.')
    return render(request, "login.html")

def logout(request):
    auth_logout(request)
    return redirect('home')

@login_required(login_url='/login')
def my_courses(request):
    enrolled_courses = PremiumCourse.objects.filter(enrolledcourse__user=request.user)
    context = { 'enrolled_courses': enrolled_courses }
    return render(request, "my_courses.html", context)

@login_required(login_url='/login')
def study(request, courseslug):
    course = get_object_or_404(PremiumCourse, slug=courseslug)

    if not EnrolledCourse.objects.filter(user=request.user, course=course).exists():
        messages.error(request, 'You are not enrolled in this course.')
        return redirect('my_courses')

    lectures = PremiumLecture.objects.filter(course=course).order_by('-order')
    context = {
        'course': course,
        'lectures': lectures,
    }
    return render(request, 'study.html', context)

@login_required(login_url='/login')
def study_lecture(request, courseslug, lectureslug):
    course = get_object_or_404(PremiumCourse, slug=courseslug)
    lecture = get_object_or_404(PremiumLecture, slug=lectureslug, course=course)

    lecture.description = [item for item in lecture.description.split("\r\n") if item]

    if not EnrolledCourse.objects.filter(user=request.user, course=course).exists():
        messages.error(request, 'You are not enrolled in this course.')
        return redirect('my_courses')

    lectures = PremiumLecture.objects.filter(course=course).order_by('-order')
    context = {
        'course': course,
        'lecture': lecture,
        'lectures': lectures,
        'manifest_url': f"/course/premium/{courseslug}/{lectureslug}/manifest.m3u8",
    }
    return render(request, 'study_lecture.html', context)

@login_required(login_url='/login')
def jaap_sessions(request):
    now = timezone.now()
    active_sessions = JaapSession.objects.filter(is_active=True).annotate(participant_count=Count('participants')).order_by('-created_at')
    upcoming_sessions = JaapSession.objects.filter(is_active=False, scheduled_at__gt=now).annotate(participant_count=Count('participants')).order_by('scheduled_at')
    past_sessions = JaapSession.objects.filter(is_active=False).exclude(scheduled_at__gt=now).annotate(participant_count=Count('participants')).order_by('-created_at')[:10]
    return render(request, 'jaap_sessions.html', {
        'active_sessions': active_sessions,
        'upcoming_sessions': upcoming_sessions,
        'past_sessions': past_sessions,
    })

@login_required(login_url='/login')
def jaap_room(request, session_id):
    session = get_object_or_404(JaapSession, id=session_id)
    participant = JaapSessionParticipant.objects.filter(session=session, user=request.user).first()
    participants = None
    total_malas = None
    if not session.is_active:
        participants = session.participants.select_related('user').order_by('-mala_count')
        total_malas = participants.aggregate(total=Sum('mala_count'))['total'] or 0
    participant_count = session.participants.count()
    return render(request, 'jaap_room.html', {
        'session': session,
        'participant': participant,
        'participants': participants,
        'total_malas': total_malas,
        'participant_count': participant_count,
    })

def jaap_status(request, session_id):
    session = get_object_or_404(JaapSession, id=session_id)
    return JsonResponse({'is_active': session.is_active})

@require_POST
@login_required(login_url='/login')
def jaap_increment(request, session_id):
    session = get_object_or_404(JaapSession, id=session_id, is_active=True)
    participant, _ = JaapSessionParticipant.objects.get_or_create(
        session=session, user=request.user
    )
    participant.mala_count += 1
    participant.save()
    return JsonResponse({'mala_count': participant.mala_count})
