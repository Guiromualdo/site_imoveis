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
    
    # URLs do Chat
    path('chat/start/<int:ad_id>/', views.start_chat, name='start_chat'),
    path('chat/room/<int:room_id>/', views.chat_room, name='chat_room'),
    path('chat/my-chats/', views.my_chats, name='my_chats'),
    path('chat/archive/<int:room_id>/', views.archive_chat, name='archive_chat'),
    path('api/chat/unread-count/', views.get_unread_count_api, name='get_unread_count_api'),
    path('api/chat/<int:room_id>/messages/', views.get_new_messages_api, name='get_new_messages_api'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
