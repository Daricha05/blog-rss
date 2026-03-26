from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils.text import slugify
from django.core.paginator import Paginator
from .models import Article, RSSArticle
from .forms import ArticleForm, RSSArticleForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout


def custom_logout(request):
    """Vue de déconnexion personnalisée"""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('blog:article_lists')

# Ou avec décorateur
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Déconnexion réussie !')
    return redirect('blog:article_lists')

def article_lists(request):
    articles = Article.objects.all()
    paginator = Paginator(articles, 10)  # 10 articles par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/lists.html', {'articles': page_obj})

def rss_article_lists(request):
    articles = RSSArticle.objects.filter(published=True).order_by('-date')
    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/rsslists.html', {'articles': page_obj})

def detail_article(request, slug):
    article = get_object_or_404(Article, slug=slug)
    return render(request, 'blog/detail.html', {'article': article})

def rss_article_detail(request, slug):
    article = get_object_or_404(RSSArticle, slug=slug, published=True)
    return render(request, 'blog/rss_detail.html', {'article': article})

@staff_member_required
def create_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.slug = slugify(article.title)
            article.save()
            messages.success(request, 'Article créé avec succès !')
            return redirect('detail_article', slug=article.slug)
    else:
        form = ArticleForm()
    return render(request, 'blog/create_article.html', {'form': form})

@staff_member_required
def create_rss_article(request):
    if request.method == 'POST':
        form = RSSArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.slug = slugify(article.title)
            article.save()
            messages.success(request, 'Article RSS créé avec succès !')
            return redirect('rss_article_detail', slug=article.slug)
    else:
        form = RSSArticleForm()
    return render(request, 'blog/create_rss_article.html', {'form': form})

@staff_member_required
def edit_article(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, 'Article modifié avec succès !')
            return redirect('detail_article', slug=article.slug)
    else:
        form = ArticleForm(instance=article)
    return render(request, 'blog/edit_article.html', {'form': form, 'article': article})

@staff_member_required
def delete_article(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if request.method == 'POST':
        article.delete()
        messages.success(request, 'Article supprimé avec succès !')
        return redirect('article_lists')
    return render(request, 'blog/delete_article.html', {'article': article})

@staff_member_required
def edit_rss_article(request, slug):
    article = get_object_or_404(RSSArticle, slug=slug)
    if request.method == 'POST':
        form = RSSArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, 'Article RSS modifié avec succès !')
            return redirect('blog:rss_article_detail', slug=article.slug)
    else:
        form = RSSArticleForm(instance=article)
    return render(request, 'blog/edit_rss_article.html', {'form': form, 'article': article})

@staff_member_required
def delete_rss_article(request, slug):
    article = get_object_or_404(RSSArticle, slug=slug)
    if request.method == 'POST':
        article.delete()
        messages.success(request, 'Article RSS supprimé avec succès !')
        return redirect('blog:rss_article_lists')
    return render(request, 'blog/delete_rss_article.html', {'article': article})