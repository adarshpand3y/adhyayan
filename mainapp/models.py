from django.db import models
from django.utils.text import slugify
import random
import string


def generate_random_string(length=5):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

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
class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True, editable=False)
    thumbnail = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self) -> str:
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.thumbnail:
            lecture = Lecture.objects.filter(course=self)[0]
            self.thumbnail = f"https://img.youtube.com/vi/{lecture.url}/maxresdefault.jpg"

        if not self.slug:
            # Generate a base slug from the course name
            base_slug = slugify(self.name)
            self.slug = generate_unique_slug(base_slug, Course)
        super().save(*args, **kwargs)

class Lecture(models.Model):
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, default=generate_random_string())
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
