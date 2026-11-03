from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


def pagina_inicial(request):
    return render(request, "core/landing.html")


@login_required
def inicio(request):
    return redirect("cisterna_listar")