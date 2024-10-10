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

class PremiumCourse(models.Model):
    name = models.CharField(max_length=100)
    one_line_description = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.CharField(max_length=50, default="3 months")
    mode = models.CharField(max_length=100, default="Live + Recorded")
    length = models.CharField(max_length=100, default="70+ lectures")
    elligibility = models.TextField()
    why_learn = models.TextField()
    key_highlights = models.TextField()
    price = models.IntegerField()
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
