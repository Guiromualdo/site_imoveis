from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import WantedAd, Offer, AdImage

# View para a página principal
def index(request):
    # Busca todos os anúncios ativos, ordenados pelos mais recentes
    ads = WantedAd.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'index.html', {'ads': ads})

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
        
        # Criar o anúncio
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

# View para listar anúncios do usuário
@login_required
def listar_anuncios(request):
    anuncios = WantedAd.objects.filter(created_by=request.user)
    return render(request, 'anuncios/listar.html', {'anuncios': anuncios})