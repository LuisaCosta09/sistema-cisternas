from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_http_methods

from .forms import CisternaForm, MonitoramentoForm, UsuarioForm
from .models import Cisterna, Monitoramento, Usuario


@require_GET
def inicio(request):
    return redirect("cisterna_listar")


@require_GET
def cisterna_listar(request):
    cisternas = Cisterna.objects.select_related("usuario").all()

    contexto = {
        "titulo_pagina": "Cisternas cadastradas",
        "cisternas": cisternas,
        "quantidade_cisternas": cisternas.count(),
    }

    return render(
        request,
        "cisternas/cisterna_listar.html",
        contexto,
    )


@require_http_methods(["GET", "POST"])
def cisterna_criar(request):
    if request.method == "POST":
        form = CisternaForm(request.POST)

        if form.is_valid():
            cisterna = form.save()

            messages.success(
                request,
                f"Cisterna {cisterna.id} cadastrada com sucesso.",
            )

            return redirect("cisterna_listar")

    else:
        form = CisternaForm()

    contexto = {
        "titulo_pagina": "Cadastrar cisterna",
        "form": form,
    }

    return render(
        request,
        "cisternas/cisterna_formulario.html",
        contexto,
    )


@require_GET
def usuario_listar(request):
    usuarios = Usuario.objects.order_by("nome", "username")

    contexto = {
        "titulo_pagina": "Usuários cadastrados",
        "usuarios": usuarios,
        "quantidade_usuarios": usuarios.count(),
    }

    return render(
        request,
        "usuario/listar.html",
        contexto,
    )


@require_http_methods(["GET", "POST"])
def usuario_criar(request):
    if request.method == "POST":
        form = UsuarioForm(request.POST)

        if form.is_valid():
            usuario = form.save()

            messages.success(
                request,
                f"Usuário {usuario.nome} cadastrado com sucesso.",
            )

            return redirect("usuario_listar")

    else:
        form = UsuarioForm()

    contexto = {
        "titulo_pagina": "Cadastrar usuário",
        "form": form,
    }

    return render(
        request,
        "usuario/formulario.html",
        contexto,
    )


@require_GET
def monitoramento_listar(request):
    monitoramentos = Monitoramento.objects.select_related(
        "usuario",
        "cisterna",
    ).all()

    contexto = {
        "titulo_pagina": "Monitoramentos cadastrados",
        "monitoramentos": monitoramentos,
        "quantidade_monitoramentos": monitoramentos.count(),
    }

    return render(
        request,
        "monitoramento/listar.html",
        contexto,
    )


@require_http_methods(["GET", "POST"])
def monitoramento_criar(request):
    if request.method == "POST":
        form = MonitoramentoForm(request.POST)

        if form.is_valid():
            monitoramento = form.save()

            messages.success(
                request,
                f"Monitoramento {monitoramento.id} cadastrado com sucesso.",
            )

            return redirect("monitoramento_listar")

    else:
        form = MonitoramentoForm()

    contexto = {
        "titulo_pagina": "Cadastrar monitoramento",
        "form": form,
    }

    return render(
        request,
        "monitoramento/formulario.html",
        contexto,
    )