
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST


def _destino_apos_login(request):
    proximo = request.POST.get("next") or request.GET.get("next", "")

    if proximo and url_has_allowed_host_and_scheme(
        url=proximo,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return proximo

    return reverse("cisterna_listar")


def entrar(request):
    if request.user.is_authenticated:
        return redirect("cisterna_listar")

    formulario = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and formulario.is_valid():
        login(request, formulario.get_user())
        return redirect(_destino_apos_login(request))

    return render(
        request,
        "cisternas/autenticacao/entrar.html",
        {
            "form": formulario,
            "proximo": request.POST.get("next")
            or request.GET.get("next", ""),
        },
    )


@require_POST
def sair(request):
    logout(request)
    return redirect("entrar")
