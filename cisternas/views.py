from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_http_methods

from .forms import AbastecimentoForm, AlertaForm, CisternaForm
from .models import Abastecimento, Alerta, Cisterna


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
