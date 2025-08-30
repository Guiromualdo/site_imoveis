from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_ad, name='create_ad'),
    # Remova ou comente esta linha se não quer usar create_offer ainda
    # path('<int:ad_id>/offer/', views.create_offer, name='create_offer'),
]