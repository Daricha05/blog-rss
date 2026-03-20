from django.contrib import admin
from .models import Article, RSSArticle

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_at', 'update_at')
    list_filter = ('published_at',)
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(RSSArticle)
class RSSArticleAdmin(admin.ModelAdmin):
    list_display = ('date','title', 'suggested_post')
    list_filter = ('date',)
    search_fields = ('title',)