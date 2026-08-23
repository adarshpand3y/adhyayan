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
from datetime import timedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings


load_dotenv()
_env = dotenv_values()

# Create your views here.
GOOGLE_REVIEW_URL = "https://www.google.com/searchviewer/10?svid=CAwSHRIbCgNwdnESFENnMHZaeTh4TVc0emJGOXVibXhxGAo#sv=CAESzQEKuQEStgEKd0FKaVQ0dElSeXItUDV6cUlMVzlmeVI5NF9Ram41T2NNVkx1cU1saUpfaUt5UkEzdkZXQU50eXpKN25GTGQzNTdLZm5XdUtGUG1WS3hGa1V5UlRzRk1oeUNDaXROTF9tbDJILVBXY0JHdFBsSzUzUHVkRW4zMlY4EhdZX0ZGYXB5d09zeXQ0LUVQMTRpRXFRURoiQURzcjlmUzQ5WWtWWGVoWkxxZlRXU2lJVWoxaUJNZVM5QRIEODA1MRoBMyoAMAA4AUAAGAAgisGByAhKAhAC"

INSTAGRAM_TESTIMONIALS = [
    "https://www.instagram.com/s/aGlnaGxpZ2h0OjE4MDQwMzI5ODc3NjYxMzY5?story_media_id=3299019660803747342&igsh=ajY2NWM0Mmw0OWJv",
    "https://www.instagram.com/s/aGlnaGxpZ2h0OjE3ODg2ODY4MDM1MDk1Mjc3?story_media_id=3450334216806482919&igsh=OG4xNG5pMnFjYm4z",
    "https://www.instagram.com/s/aGlnaGxpZ2h0OjE3ODQ3NzMwMDM1MzQ4ODc3?story_media_id=3506756818951570554&igsh=ajZ1cjdud216cGg4",
    "https://www.instagram.com/s/aGlnaGxpZ2h0OjE4MDMwNjc4ODU3MjIzNDcx?story_media_id=3535019316729254699&igsh=MTF1dTMyaHo4eXkzNA==",
    "https://www.instagram.com/s/aGlnaGxpZ2h0OjE4MDU0MDExODEzMTIyNTAz?story_media_id=3560379339495946347&igsh=am82Z2pwb3F3czI1",
    "https://www.instagram.com/s/aGlnaGxpZ2h0OjE3OTAxNzQxODkxMTA3MzY1?story_media_id=3571225653443850164&igsh=MXF1dTk3anJlOWV0bQ==",
    "https://www.instagram.com/s/aGlnaGxpZ2h0OjE4MDcwNjE5MjAwODgyMTc5?story_media_id=3586439422830918906&igsh=OHB6em00NGVqNWIx",
    "https://www.instagram.com/s/aGlnaGxpZ2h0OjE4MDMxOTI1NjU0NjQyMTE0?story_media_id=3610592441306479636&igsh=MWh6d2pwamp5NjlqdQ==",
    "https://www.instagram.com/s/aGlnaGxpZ2h0OjE4MTA4NzM1MTMzNDkzNjMw?story_media_id=3626677792961954014&igsh=dDV2anB2bnNrYjBj",
    "https://www.instagram.com/s/aGlnaGxpZ2h0OjE3ODk4NDI2MjI4MjA2OTkw?story_media_id=3640888850299709164&igsh=MWszZWRvenpyZjEwYQ==",
    "https://www.instagram.com/s/aGlnaGxpZ2h0OjE3ODQ3ODkxMTIzNTAyNzUw?story_media_id=3663317028020174787&igsh=eXUwd3BqNmZiMTJh",
    "https://www.instagram.com/s/aGlnaGxpZ2h0OjE4MDkzNzU5NjMxNzU4MDE4?story_media_id=3811043956164225879&igsh=MXU4enVoeGxoM2ZzdA==",
    "https://www.instagram.com/s/aGlnaGxpZ2h0OjE3OTUxMDQ4OTg1MDg2MjIz?story_media_id=3830135438452042167&igsh=MTl2ajFkeXE2c2xyNQ==",
    "https://www.instagram.com/s/aGlnaGxpZ2h0OjE4MTAwMTI1MzU2MzA1MDk2?story_media_id=3866452666122078664&igsh=cGR6anZ2aGl1NWZ4",
    "https://www.instagram.com/s/aGlnaGxpZ2h0OjE3OTMyMDU5MDc1MDcyMzAw?story_media_id=3886176037269375365&igsh=MTNuZHhmZDRqYXk2dA==",
    "https://www.instagram.com/s/aGlnaGxpZ2h0OjE4MDY1MTYzOTM1NzAzNTMy?story_media_id=3911476898354631645&igsh=MTE5bWxrdGJrejBqdA==",
    "https://www.instagram.com/s/aGlnaGxpZ2h0OjE4NTM1NTg3MTkzMDc4OTg4?story_media_id=3919437724197800460&igsh=OGNpNjJuZXQ0NzRh",
]


def index(request):
    images = AlbumImage.objects.all().order_by('-id')[:4]
    testimonials = [
        {"label": f"Review {i}", "url": url}
        for i, url in enumerate(INSTAGRAM_TESTIMONIALS, start=1)
    ]
    return render(request, "index.html", {
        "images": images,
        "testimonials": testimonials,
        "google_review_url": GOOGLE_REVIEW_URL,
    })

def courses(request):
    courses = Course.objects.all()
    is_demo_user = request.user.is_authenticated and request.user.email in settings.DEMO_ACCOUNT_EMAILS
    premium_courses = PremiumCourse.objects.all() if is_demo_user else PremiumCourse.objects.filter(is_demo=False)

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
    now = timezone.now()
    if participant.last_mala_at and (now - participant.last_mala_at) < timedelta(seconds=30):
        return JsonResponse({'error': 'rate_limited'}, status=429)
    participant.mala_count += 1
    participant.last_mala_at = now
    participant.save()
    return JsonResponse({'mala_count': participant.mala_count})

# North Indian (diamond) chart layout: fixed house polygons for a 400x400 SVG.
# House 1 (the Ascendant's house) is always the top-center kite; houses run
# counter-clockwise from there. Centroids are used as text anchors.
_NORTH_INDIAN_HOUSE_POLYGONS = [
    {"house": 1, "points": "200,0 300,100 200,200 100,100", "cx": 200, "cy": 100},
    {"house": 2, "points": "0,0 200,0 100,100", "cx": 100, "cy": 33},
    {"house": 3, "points": "0,0 100,100 0,200", "cx": 33, "cy": 100},
    {"house": 4, "points": "0,200 100,100 200,200 100,300", "cx": 100, "cy": 200},
    {"house": 5, "points": "0,400 100,300 0,200", "cx": 33, "cy": 300},
    {"house": 6, "points": "0,400 200,400 100,300", "cx": 100, "cy": 367},
    {"house": 7, "points": "200,400 100,300 200,200 300,300", "cx": 200, "cy": 300},
    {"house": 8, "points": "400,400 300,300 200,400", "cx": 300, "cy": 367},
    {"house": 9, "points": "400,400 400,200 300,300", "cx": 367, "cy": 300},
    {"house": 10, "points": "400,200 300,300 200,200 300,100", "cx": 300, "cy": 200},
    {"house": 11, "points": "400,0 300,100 400,200", "cx": 367, "cy": 100},
    {"house": 12, "points": "400,0 200,0 300,100", "cx": 300, "cy": 33},
]

_PLANET_ABBR = {
    'Sun': 'Su', 'Moon': 'Mo', 'Mars': 'Ma', 'Mercury': 'Me', 'Jupiter': 'Ju',
    'Venus': 'Ve', 'Saturn': 'Sa', 'Rahu': 'Ra', 'Ketu': 'Ke',
}


def _build_north_indian_chart(kundli):
    """Builds the per-house display data (rashi number + one line per planet,
    with degree/retrograde/combust/debilitated/exalted markers) for the fixed
    diamond layout above, given a get_kundli() result."""
    planets_by_house = {}
    for p in kundli['planets']:
        flags = []
        if p['retrograde']:
            flags.append('R')
        if p.get('exalted'):
            flags.append('e')
        if p.get('combust'):
            flags.append('c')
        if p.get('debilitated'):
            flags.append('d')
        flag_str = f"({','.join(flags)})" if flags else ''
        text = f"{_PLANET_ABBR[p['planet']]} {p['degree_in_rashi']:.0f}°{flag_str}"

        if p.get('exalted'):
            color = '#198754'  # exalted: green
        elif p.get('debilitated'):
            color = '#c0392b'  # debilitated: red
        elif p.get('combust'):
            color = '#b45f06'  # combust: amber
        else:
            color = '#1a1a1a'
        planets_by_house.setdefault(p['house'], []).append({'text': text, 'color': color})

    ascendant = kundli['ascendant']
    asc_rashi_index = ascendant['rashi_index']
    chart = []
    for layout in _NORTH_INDIAN_HOUSE_POLYGONS:
        house_num = layout['house']
        rashi_index = (asc_rashi_index + house_num - 1) % 12
        chart.append({
            'points': layout['points'],
            'cx': layout['cx'],
            'cy': layout['cy'],
            'rashi_number': rashi_index + 1,
            'planets': planets_by_house.get(house_num, []),
            'is_ascendant': house_num == 1,
            'asc_degree': f"{ascendant['degree_in_rashi']:.2f}" if house_num == 1 else None,
        })
    return chart


def astro_lab(request):
    """Manual test page for the standalone vedic_astro engine (panchang + kundli + dasha)."""
    import datetime
    from vedic_astro import (
        get_panchang, get_kundli, compute_vimshottari, dasha_breakdown,
        compute_shadbala, compute_bhavabala,
    )

    now = timezone.localtime()
    defaults = {
        'date': timezone.localdate().isoformat(),
        'time': '06:30',
        'latitude': '28.6139',
        'longitude': '77.2090',
        'tz_offset': '5.5',
        'as_of_date': now.date().isoformat(),
        'as_of_time': now.strftime('%H:%M'),
    }
    context = {'form': defaults, 'error': None}

    if request.method == 'POST':
        form = {k: request.POST.get(k, defaults[k]) for k in defaults}
        context['form'] = form
        try:
            date_val = datetime.date.fromisoformat(form['date'])
            time_val = datetime.time.fromisoformat(form['time'])
            lat = float(form['latitude'])
            lon = float(form['longitude'])
            tz_offset = float(form['tz_offset'])
            birth_dt = datetime.datetime.combine(date_val, time_val)

            as_of_date = datetime.date.fromisoformat(form['as_of_date'])
            as_of_time = datetime.time.fromisoformat(form['as_of_time'])
            as_of_dt = datetime.datetime.combine(as_of_date, as_of_time)

            panchang = get_panchang(date_val, lat, lon, tz_offset)
            kundli = get_kundli(birth_dt, lat, lon, tz_offset)
            moon = next(p for p in kundli['planets'] if p['planet'] == 'Moon')
            dashas = compute_vimshottari(moon['longitude'], birth_dt)
            dasha_levels = dasha_breakdown(moon['longitude'], birth_dt, as_of_dt)
            shadbala_raw = compute_shadbala(birth_dt, lat, lon, tz_offset)
            bhavabala = compute_bhavabala(birth_dt, lat, lon, tz_offset, shadbala_raw)

            shadbala = sorted(
                ({'planet': planet, **data} for planet, data in shadbala_raw.items()),
                key=lambda d: d['total_virupa'], reverse=True,
            )
            bhavabala = sorted(bhavabala, key=lambda h: h['total_virupa'], reverse=True)

            context['panchang'] = panchang
            context['kundli'] = kundli
            context['north_indian_chart'] = _build_north_indian_chart(kundli)
            context['dashas'] = dashas
            context['dasha_levels'] = dasha_levels
            context['as_of_dt'] = as_of_dt
            context['shadbala'] = shadbala
            context['bhavabala'] = bhavabala
        except Exception as exc:
            context['error'] = str(exc)

    return render(request, 'astro_lab.html', context)
