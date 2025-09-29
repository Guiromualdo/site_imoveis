from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from .models import WantedAd, Offer, AdImage
from .forms import CustomUserCreationForm, UserProfileForm
from django.http import JsonResponse
from django.db.models import Q, Max
from django.core.paginator import Paginator
from .models import WantedAd, ChatRoom, ChatMessage
from django.utils import timezone
from datetime import datetime

# View para a página principal
def index(request):
    ads = WantedAd.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'index.html', {'ads': ads})

# View para registro de usuário
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada para {username}! Você já pode fazer login.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# View para perfil do usuário
@login_required
def profile(request):
    user_ads = WantedAd.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'registration/profile.html', {
        'user_ads': user_ads,
        'total_ads': user_ads.count(),
        'active_ads': user_ads.filter(is_active=True).count()
    })

# View para editar perfil
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'registration/edit_profile.html', {'form': form})

# View para criar anúncio
@login_required
def create_ad(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        location = request.POST.get('location')
        price = request.POST.get('price')
        reward = request.POST.get('reward')
        
        ad = WantedAd.objects.create(
            title=title,
            description=description,
            category=category,
            location=location,
            price=price,
            reward=reward,
            created_by=request.user
        )
        
        # Processar imagens se houver
        images = request.FILES.getlist('images')
        for image in images:
            AdImage.objects.create(ad=ad, image=image)
        
        messages.success(request, 'Anúncio criado com sucesso!')
        return redirect('index')
    
    return render(request, 'create_ad.html')

# View para editar anúncio
@login_required
def edit_ad(request, ad_id):
    ad = get_object_or_404(WantedAd, id=ad_id, created_by=request.user)
    
    if request.method == 'POST':
        ad.title = request.POST.get('title')
        ad.description = request.POST.get('description')
        ad.category = request.POST.get('category')
        ad.location = request.POST.get('location')
        ad.price = request.POST.get('price')
        ad.reward = request.POST.get('reward')
        ad.save()
        
        messages.success(request, 'Anúncio atualizado com sucesso!')
        return redirect('index')
    
    return render(request, 'edit_ad.html', {'ad': ad})

# View para deletar anúncio
@login_required
def delete_ad(request, ad_id):
    ad = get_object_or_404(WantedAd, id=ad_id, created_by=request.user)
    
    if request.method == 'POST':
        ad.delete()
        messages.success(request, 'Anúncio excluído com sucesso!')
        return redirect('index')
    
    return render(request, 'delete_ad.html', {'ad': ad})

# View para criar oferta
@login_required
def create_offer(request, ad_id):
    ad = get_object_or_404(WantedAd, id=ad_id)
    
    if request.method == 'POST':
        message = request.POST.get('message')
        Offer.objects.create(
            wanted_ad=ad,
            sender=request.user,
            message=message
        )
        messages.success(request, 'Sua oferta foi enviada!')
        return redirect('index')
    
    return render(request, 'create_offer.html', {'ad': ad})

@login_required
def start_chat(request, ad_id):
    """Inicia um chat com o dono do anúncio"""
    ad = get_object_or_404(WantedAd, id=ad_id, is_active=True)
    
    # Não pode conversar consigo mesmo
    if ad.created_by == request.user:
        messages.error(request, '❌ Você não pode conversar consigo mesmo!')
        return redirect('index')
    
    # Busca ou cria a sala de chat
    chat_room, created = ChatRoom.get_or_create_room(
        ad=ad,
        user1=request.user,
        user2=ad.created_by
    )
    
    if created:
        messages.success(request, f'💬 Chat iniciado! Converse com {ad.created_by.get_full_name() or ad.created_by.username} sobre: {ad.title}')
    else:
        messages.info(request, f'💬 Continuando conversa sobre: {ad.title}')
    
    return redirect('chat_room', room_id=chat_room.id)

@login_required
def chat_room(request, room_id):
    """Exibe a sala de chat"""
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    
    # Verifica se o usuário pode acessar este chat
    if request.user not in [chat_room.participant_1, chat_room.participant_2]:
        messages.error(request, '🚫 Você não tem permissão para acessar este chat.')
        return redirect('index')
    
    # Marca mensagens como lidas (apenas as que não são do próprio usuário)
    ChatMessage.objects.filter(
        chat_room=chat_room,
        is_read=False
    ).exclude(sender=request.user).update(is_read=True)
    
    # Processa envio de nova mensagem
    if request.method == 'POST':
        message_text = request.POST.get('message', '').strip()
        if message_text:
            ChatMessage.objects.create(
                chat_room=chat_room,
                sender=request.user,
                message=message_text
            )
            messages.success(request, '✅ Mensagem enviada!')
            return redirect('chat_room', room_id=room_id)
        else:
            messages.error(request, '❌ Não é possível enviar mensagem vazia.')
    
    # Busca mensagens paginadas (últimas 50 mensagens)
    chat_messages = chat_room.messages.all().order_by('-created_at')[:50]
    chat_messages = reversed(chat_messages)  # Inverte para mostrar mais antigas primeiro
    
    # Informações do outro participante
    other_participant = chat_room.get_other_participant(request.user)
    
    context = {
        'chat_room': chat_room,
        'chat_messages': chat_messages,
        'other_participant': other_participant,
        'ad': chat_room.ad,
    }
    
    return render(request, 'chat/chat_room.html', context)

@login_required
def my_chats(request):
    """Lista todos os chats do usuário"""
    # Busca chats onde o usuário é participante
    chat_rooms = ChatRoom.objects.filter(
        Q(participant_1=request.user) | Q(participant_2=request.user),
        is_active=True
    ).select_related('ad', 'participant_1', 'participant_2').prefetch_related('messages').order_by('-updated_at')
    
    # Adiciona informações extras para cada chat
    chat_list = []
    for room in chat_rooms:
        other_user = room.get_other_participant(request.user)
        last_message = room.get_last_message()
        unread_count = room.get_unread_count_for_user(request.user)
        
        chat_info = {
            'room': room,
            'other_user': other_user,
            'last_message': last_message,
            'unread_count': unread_count,
            'ad': room.ad
        }
        chat_list.append(chat_info)
    
    context = {
        'chat_list': chat_list,
        'total_chats': len(chat_list)
    }
    
    return render(request, 'chat/my_chats.html', context)

@login_required  
def archive_chat(request, room_id):
    """Arquiva um chat (não exclui, apenas oculta)"""
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    
    # Verifica permissão
    if request.user not in [chat_room.participant_1, chat_room.participant_2]:
        messages.error(request, '🚫 Você não tem permissão para arquivar este chat.')
        return redirect('my_chats')
    
    if request.method == 'POST':
        chat_room.is_active = False
        chat_room.save()
        messages.success(request, '📁 Chat arquivado com sucesso!')
        return redirect('my_chats')
    
    other_participant = chat_room.get_other_participant(request.user)
    
    context = {
        'chat_room': chat_room,
        'other_participant': other_participant,
        'ad': chat_room.ad
    }
    
    return render(request, 'chat/archive_chat.html', context)

# =============================================================================
# API PARA ATUALIZAÇÃO DO CHAT EM TEMPO REAL (OPCIONAL)
# =============================================================================

@login_required
def get_new_messages_api(request, room_id):
    """API para buscar novas mensagens via AJAX"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    
    # Verifica permissão
    if request.user not in [chat_room.participant_1, chat_room.participant_2]:
        return JsonResponse({'error': 'Sem permissão'}, status=403)
    
    # Pega timestamp da última verificação
    last_check = request.GET.get('last_check')
    if last_check:
        try:
            last_check_dt = datetime.fromisoformat(last_check.replace('Z', '+00:00'))
            new_messages = chat_room.messages.filter(
                created_at__gt=last_check_dt
            ).order_by('created_at')
        except (ValueError, TypeError):
            new_messages = chat_room.messages.none()
    else:
        # Se não tem last_check, retorna as últimas 5 mensagens
        new_messages = chat_room.messages.order_by('-created_at')[:5]
        new_messages = reversed(new_messages)
    
    # Converte mensagens para JSON
    messages_data = []
    for msg in new_messages:
        messages_data.append({
            'id': msg.id,
            'sender': msg.sender.get_full_name() or msg.sender.username,
            'sender_username': msg.sender.username,
            'message': msg.message,
            'created_at': msg.created_at.isoformat(),
            'is_own': msg.sender == request.user,
            'formatted_time': msg.created_at.strftime('%H:%M')
        })
    
    # Marca mensagens como lidas
    if messages_data:
        chat_room.messages.filter(
            is_read=False
        ).exclude(sender=request.user).update(is_read=True)
    
    return JsonResponse({
        'messages': messages_data,
        'count': len(messages_data),
        'current_time': timezone.now().isoformat()
    })

@login_required
def get_unread_count_api(request):
    """API para buscar contador de mensagens não lidas"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    # Conta todas as mensagens não lidas do usuário
    unread_count = ChatMessage.objects.filter(
        chat_room__participant_1=request.user,
        is_read=False
    ).exclude(sender=request.user).count()
    
    unread_count += ChatMessage.objects.filter(
        chat_room__participant_2=request.user,
        is_read=False
    ).exclude(sender=request.user).count()
    
    return JsonResponse({
        'unread_count': unread_count
    })