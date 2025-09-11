from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('create/', views.create_ad, name='create_ad'),
    path('ads/<int:ad_id>/offer/', views.create_offer, name='create_offer'),
    path('edit/<int:ad_id>/', views.edit_ad, name='edit_ad'),
    path('delete/<int:ad_id>/', views.delete_ad, name='delete_ad'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
