from django.shortcuts import render, get_object_or_404
from .models import Article, RSSArticle

def article_lists(request):
    articles = Article.objects.all()
    return render(request, 'blog/lists.html', {'articles': articles})

def rss_article_lists(request):
    articles = RSSArticle.objects.filter(published=True).order_by('-date')
    return render(request, 'blog/rsslists.html', {'articles': articles})

def detail_article(request, slug):
    article = get_object_or_404(Article, slug=slug)
    return render(request, 'blog/detail.html', {'article': article})

def rss_article_detail(request, slug):
    article = get_object_or_404(RSSArticle, slug=slug, published=True)
    return render(request, 'blog/rss_detail.html', {'article': article})