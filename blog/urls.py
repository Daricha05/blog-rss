from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'blog'

urlpatterns = [    
    # Articles normaux
    path('', views.article_lists, name='article_lists'),
    path('article/<slug:slug>/', views.detail_article, name='detail_article'),
    
    # Articles RSS
    path('rss/', views.rss_article_lists, name='rss_article_lists'),
    path('rss/<slug:slug>/', views.rss_article_detail, name='rss_article_detail'),
    
    # Admin URLs
    path('admin/create/', views.create_article, name='create_article'),
    path('admin/create-rss/', views.create_rss_article, name='create_rss_article'),
    path('admin/edit/<slug:slug>/', views.edit_article, name='edit_article'),
    path('admin/delete/<slug:slug>/', views.delete_article, name='delete_article'),
    
    # Admin URLs pour RSS
    path('admin/rss/create/', views.create_rss_article, name='create_rss_article'),
    path('admin/rss/edit/<slug:slug>/', views.edit_rss_article, name='edit_rss_article'),
    path('admin/rss/delete/<slug:slug>/', views.delete_rss_article, name='delete_rss_article'),

    # Déconnexion personnalisée
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]
