from django import forms
from .models import Article, RSSArticle

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'image_url', 'published_at']
        widgets = {
            'published_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'content': forms.Textarea(attrs={'rows': 15}),
        }

class RSSArticleForm(forms.ModelForm):
    class Meta:
        model = RSSArticle
        fields = ['date', 'title', 'suggested_post', 'image_url', 'published']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'suggested_post': forms.Textarea(attrs={'rows': 10}),
        }