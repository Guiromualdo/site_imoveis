from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required  # Se isso estiver aqui e o usuário não estiver logado, redireciona para LOGIN_URL.
def criar_anuncio(request):
    if request.method == 'POST':
        # Lógica para salvar o anúncio
        return redirect('lista_anuncios')  # Redirecione para a listagem após sucesso.
    else:
        # Renderize o form
        return render(request, 'anuncios/criar.html', {})  # Certifique-se de que esse template existe.

    def listar_anuncios(request):
        anuncios = Anuncio.objects.filter(created_by=request.user)
        return render(request, 'anuncios/listar.html', {'anuncios': anuncios})      
