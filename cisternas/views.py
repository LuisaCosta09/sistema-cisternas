from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from core.permissoes import filtrar_por_dono

from .forms import CisternaForm
from .models import Cisterna


def _cisternas_visiveis(request):
    cisternas = Cisterna.objects.select_related("usuario")
    return filtrar_por_dono(cisternas, request.user, "usuario")


@login_required
def cisterna_listar(request):
    cisternas = _cisternas_visiveis(request)

    contexto = {
        "titulo_pagina": "Cisternas cadastradas",
        "cisternas": cisternas,
        "quantidade_cisternas": cisternas.count(),
    }

    return render(request, "cisternas/cisterna_listar.html", contexto)


@login_required
def cisterna_criar(request):
    if request.method == "POST":
        form = CisternaForm(request.POST, usuario_logado=request.user)

        if form.is_valid():
            cisterna = form.save()

            messages.success(
                request,
                f"Cisterna {cisterna.id} cadastrada com sucesso.",
            )

            return redirect("cisterna_listar")

    else:
        form = CisternaForm(usuario_logado=request.user)

    contexto = {
        "titulo_pagina": "Cadastrar cisterna",
        "form": form,
    }

    return render(request, "cisternas/cisterna_formulario.html", contexto)


@login_required
def cisterna_detalhar(request, pk):
    cisterna = get_object_or_404(_cisternas_visiveis(request), pk=pk)

    contexto = {
        "titulo_pagina": "Detalhes da cisterna",
        "cisterna": cisterna,
    }

    return render(request, "cisternas/cisterna_detalhes.html", contexto)


@login_required
def cisterna_editar(request, pk):
    cisterna = get_object_or_404(_cisternas_visiveis(request), pk=pk)

    if request.method == "POST":
        form = CisternaForm(
            request.POST,
            instance=cisterna,
            usuario_logado=request.user,
        )

        if form.is_valid():
            cisterna = form.save()

            messages.success(
                request,
                f"Cisterna {cisterna.id} atualizada com sucesso.",
            )

            return redirect("cisterna_detalhar", pk=cisterna.pk)

    else:
        form = CisternaForm(instance=cisterna, usuario_logado=request.user)

    contexto = {
        "titulo_pagina": "Editar cisterna",
        "form": form,
        "cisterna": cisterna,
        "modo_edicao": True,
    }

    return render(request, "cisternas/cisterna_formulario.html", contexto)


@login_required
def cisterna_excluir(request, pk):
    cisterna = get_object_or_404(_cisternas_visiveis(request), pk=pk)

    if request.method == "POST":
        identificador = cisterna.id
        cisterna.delete()

        messages.success(
            request,
            f"Cisterna {identificador} excluída com sucesso.",
        )

        return redirect("cisterna_listar")

    contexto = {
        "titulo_pagina": "Excluir cisterna",
        "objeto_nome": f"Cisterna {cisterna.id} - {cisterna.descricao}",
        "aviso_exclusao": (
            "Os monitoramentos, alertas e abastecimentos relacionados "
            "também serão excluídos."
        ),
        "url_cancelar": "cisterna_detalhar",
        "objeto_pk": cisterna.pk,
    }

    return render(request, "core/confirmar_exclusao.html", contexto)