import uuid
from django.db import models
from django.utils.text import slugify
from cloudinary.models import CloudinaryField
import random
import string

def generate_unique_slug(base_slug, model_class):
    """
    Generate a unique slug by appending a random string if necessary.
    """
    slug = base_slug
    while model_class.objects.filter(slug=slug).exists():
        # Append a random string to the base_slug if it already exists
        random_suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
        slug = f"{base_slug}-{random_suffix}"
    return slug

# Create your models here.
class AlbumImage(models.Model):
    image = CloudinaryField('image')

class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True, editable=False)
    thumbnail = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self) -> str:
        return self.name
    
    def save(self, *args, **kwargs):
        # if not self.thumbnail:
        #     lecture = Lecture.objects.filter(course=self)[0]
        #     self.thumbnail = f"https://img.youtube.com/vi/{lecture.url}/maxresdefault.jpg"

        if not self.slug:
            # Generate a base slug from the course name
            base_slug = slugify(self.name)
            self.slug = generate_unique_slug(base_slug, Course)
        super().save(*args, **kwargs)

class Lecture(models.Model):
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    url = models.CharField(max_length=11)
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True, editable=True)
    length = models.CharField(max_length=20, editable=True, default="1hr 20min")

    def __str__(self) -> str:
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate a base slug from the course name
            base_slug = slugify(self.name)
            self.slug = generate_unique_slug(base_slug, Lecture)
        super().save(*args, **kwargs)

class PremiumLecture(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(default="This is some default description.")
    course = models.ForeignKey('PremiumCourse', on_delete=models.SET_NULL, null=True, blank=True)
    r2_key = models.CharField(max_length=500, help_text="Path to the .m3u8 file in R2, e.g. courses/slug/lecture-1/index.m3u8")
    aes_key = models.CharField(max_length=32, blank=True, help_text="Hex-encoded 16-byte AES-128 key from key generation step")
    length = models.CharField(max_length=20, default="")
    order = models.PositiveIntegerField(default=0)
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True, editable=False)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            self.slug = generate_unique_slug(base_slug, PremiumLecture)
        super().save(*args, **kwargs)


class PremiumCourse(models.Model):
    name = models.CharField(max_length=100)
    one_line_description = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.CharField(max_length=50, default="3 months")
    mode = models.CharField(max_length=100, default="Live + Recorded")
    length = models.CharField(max_length=100, default="70+ lectures")
    elligibility = models.TextField(null=True, blank=True)
    why_learn = models.TextField()
    key_highlights = models.TextField()
    price = models.IntegerField(help_text="Actual price shown to users.")
    striked_price = models.IntegerField(null=True, blank=True, help_text="Original price shown struck-through above the current offer price. Leave blank to hide.")
    is_demo = models.BooleanField(default=False, help_text="Demo courses are only shown to accounts whose email is in DEMO_ACCOUNT_EMAILS.")
    thumbnail = CloudinaryField('image')
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True, editable=False)

    def __str__(self) -> str:
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate a base slug from the course name
            base_slug = slugify(self.name)
            self.slug = generate_unique_slug(base_slug, PremiumCourse)
        super().save(*args, **kwargs)

class EnrolledCourse(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    course = models.ForeignKey(PremiumCourse, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')

class JaapSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    god_name = models.CharField(default="Jai Shree Hari", max_length=100)
    is_active = models.BooleanField(default=True)
    scheduled_at = models.DateTimeField(null=True, blank=True, help_text="Set to a future time to show this session as upcoming before it goes live.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class JaapSessionParticipant(models.Model):
    session = models.ForeignKey(JaapSession, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    mala_count = models.PositiveIntegerField(default=0)
    last_mala_at = models.DateTimeField(null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session', 'user')
        ordering = ['-mala_count']

    def __str__(self):
        return f"{self.session.name} - {self.user.first_name or self.user.username} - {self.mala_count} malas"
