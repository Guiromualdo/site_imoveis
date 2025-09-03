from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import WantedAdForm, OfferForm  # Adicione OfferForm aqui
from .models import WantedAd, Offer
from .models import Anuncio  # Adicione Anuncio aqui

@login_required
def create_ad(request):
    if request.method == 'POST':
        form = WantedAdForm(request.POST)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.created_by = request.user
            ad.save()
            return redirect('index')  # Redireciona pra listagem após salvar
    else:
        form = WantedAdForm()
    return render(request, 'create_ad.html', {'form': form})

def index(request):
    anuncios = Anuncio.objects.all()  # Pega todos os anúncios
    return render(request, 'index.html', {'ads': anuncios})

@login_required
def create_offer(request, ad_id):
    ad = Anuncio.objects.get(id=ad_id)  # Corrige para o modelo Anuncio
    if request.method == 'POST':
        form = OfferForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.ad = ad
            offer.save()
            return redirect('index')
    else:
        form = OfferForm()
    return render(request, 'create_offer.html', {'form': form, 'ad': ad})