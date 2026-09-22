from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_http_methods

from .forms import (
    AbastecimentoForm,
    AlertaForm,
    CisternaForm,
    MonitoramentoForm,
    UsuarioForm,
)
from .models import Abastecimento, Alerta, Cisterna, Monitoramento, Usuario


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


@require_GET
def alerta_listar(request):
    alertas = Alerta.objects.select_related(
        "cisterna",
        "cisterna__usuario",
    ).all()

    contexto = {
        "titulo_pagina": "Alertas cadastrados",
        "alertas": alertas,
        "quantidade_alertas": alertas.count(),
    }

    return render(
        request,
        "cisternas/alerta/listar.html",
        contexto,
    )


@require_http_methods(["GET", "POST"])
def alerta_criar(request):
    if request.method == "POST":
        form = AlertaForm(request.POST)

        if form.is_valid():
            alerta = form.save()

            messages.success(
                request,
                f"Alerta {alerta.id} cadastrado com sucesso.",
            )

            return redirect("alerta_listar")

    else:
        form = AlertaForm()

    contexto = {
        "titulo_pagina": "Cadastrar alerta",
        "form": form,
    }

    return render(
        request,
        "cisternas/alerta/formulario.html",
        contexto,
    )


@require_GET
def abastecimento_listar(request):
    abastecimentos = Abastecimento.objects.select_related(
        "usuario",
        "cisterna",
    ).all()

    contexto = {
        "titulo_pagina": "Abastecimentos cadastrados",
        "abastecimentos": abastecimentos,
        "quantidade_abastecimentos": abastecimentos.count(),
    }

    return render(
        request,
        "cisternas/abastecimento/listar.html",
        contexto,
    )


@require_http_methods(["GET", "POST"])
def abastecimento_criar(request):
    if request.method == "POST":
        form = AbastecimentoForm(request.POST)

        if form.is_valid():
            abastecimento = form.save()

            messages.success(
                request,
                (
                    f"Abastecimento {abastecimento.id} "
                    "cadastrado com sucesso."
                ),
            )

            return redirect("abastecimento_listar")

    else:
        form = AbastecimentoForm()

    contexto = {
        "titulo_pagina": "Cadastrar abastecimento",
        "form": form,
    }

    return render(
        request,
        "cisternas/abastecimento/formulario.html",
        contexto,
    )

