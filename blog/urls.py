from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.article_lists, name='liste'),
    path('rss/', views.rss_article_lists, name='rss_liste'),
    path('<slug:slug>/', views.detail_article, name='detail'),
    path('rss/<slug:slug>/', views.rss_article_detail, name='rss_detail'),
]
