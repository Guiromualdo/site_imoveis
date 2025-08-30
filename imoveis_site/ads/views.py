from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import WantedAdForm, OfferForm  # Adicione OfferForm aqui
from .models import WantedAd, Offer  # Adicione Offer aqui

@login_required
def create_ad(request):
    if request.method == 'POST':
        form = WantedAdForm(request.POST)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.created_by = request.user
            ad.save()
            return redirect('index')
    else:
        form = WantedAdForm()
    return render(request, 'create_ad.html', {'form': form})

def index(request):
    ads = WantedAd.objects.all()[:5]  # Limita a 5 itens pra testar
    return render(request, 'index.html', {'ads': ads})

@login_required
def create_offer(request, ad_id):
    ad = WantedAd.objects.get(id=ad_id)
    if request.method == 'POST':
        form = OfferForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.wanted_ad = ad
            offer.sender = request.user
            offer.save()
            return redirect('index')
    else:
        form = OfferForm()
    return render(request, 'create_offer.html', {'form': form, 'ad': ad})