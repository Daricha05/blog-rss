from django.contrib import admin
from .models import Article, RSSArticle

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_at', 'update_at')
    list_filter = ('published_at', 'update_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'

@admin.register(RSSArticle)
class RSSArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'published', 'created_at']
    list_filter = ['published', 'date']
    search_fields = ['title', 'suggested_post']
    prepopulated_fields = {'slug': ('title',)}
    actions = ['publish_articles', 'unpublish_articles']
    
    def publish_articles(self, request, queryset):
        queryset.update(published=True)
    publish_articles.short_description = "Publier les articles sélectionnés"
    
    def unpublish_articles(self, request, queryset):
        queryset.update(published=False)
    unpublish_articles.short_description = "Dépublier les articles sélectionnés"
