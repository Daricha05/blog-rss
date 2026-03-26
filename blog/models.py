from django.utils import timezone
from django.utils.text import slugify
from django.db import models
from django.urls import reverse

class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    published_at = models.DateTimeField(default=timezone.now)
    update_at = models.DateTimeField(auto_now=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    
    class Meta:
        ordering = ['-published_at']
    
    def __str__(self) -> str:
        return self.title
    
    def get_absolute_url(self):
        return reverse("detail_article", kwargs={"slug": self.slug})
    

class RSSArticle(models.Model):
    date = models.DateField()
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, max_length=100)
    suggested_post = models.TextField()
    image_url = models.URLField(max_length=500, blank=True, null=True)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            base_slug = base_slug[:50]
            
            # Vérifier l'unicité
            unique_slug = base_slug
            counter = 1
            while RSSArticle.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug[:47]}-{counter}"
                counter += 1
            
            self.slug = unique_slug
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("rss_article_detail", kwargs={"slug": self.slug})
    