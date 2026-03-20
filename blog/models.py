from django.utils import timezone
from django.utils.text import slugify
from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    published_at = models.DateTimeField(default=timezone.now)
    update_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-published_at']
    
    def __str__(self) -> str:
        return self.title

class RSSArticle(models.Model):
    date = models.DateField()
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    suggested_post = models.TextField()
    published = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.title