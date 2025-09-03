from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_ad, name='create_ad'),
    path('ads/<int:ad_id>/offer/', views.create_offer, name='create_offer'),
 ]
