from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from core.permissoes import filtrar_por_dono

from .forms import AlertaForm
from .models import Alerta


def _alertas_visiveis(request):
    alertas = Alerta.objects.select_related("cisterna", "cisterna__usuario")
    return filtrar_por_dono(alertas, request.user, "cisterna__usuario")


@login_required
def alerta_listar(request):
    alertas = _alertas_visiveis(request)

    contexto = {
        "titulo_pagina": "Alertas cadastrados",
        "alertas": alertas,
        "quantidade_alertas": alertas.count(),
    }

    return render(request, "alertas/listar.html", contexto)


@login_required
def alerta_criar(request):
    if request.method == "POST":
        form = AlertaForm(request.POST, usuario_logado=request.user)

        if form.is_valid():
            alerta = form.save()

            messages.success(
                request,
                f"Alerta {alerta.id} cadastrado com sucesso.",
            )

            return redirect("alerta_listar")

    else:
        form = AlertaForm(usuario_logado=request.user)

    contexto = {
        "titulo_pagina": "Cadastrar alerta",
        "form": form,
    }

    return render(request, "alertas/formulario.html", contexto)


@login_required
def alerta_detalhar(request, pk):
    alerta = get_object_or_404(_alertas_visiveis(request), pk=pk)

    contexto = {
        "titulo_pagina": "Detalhes do alerta",
        "alerta": alerta,
    }

    return render(request, "alertas/detalhes.html", contexto)


@login_required
def alerta_editar(request, pk):
    alerta = get_object_or_404(_alertas_visiveis(request), pk=pk)

    if request.method == "POST":
        form = AlertaForm(
            request.POST,
            instance=alerta,
            usuario_logado=request.user,
        )

        if form.is_valid():
            alerta = form.save()

            messages.success(
                request,
                f"Alerta {alerta.id} atualizado com sucesso.",
            )

            return redirect("alerta_detalhar", pk=alerta.pk)

    else:
        form = AlertaForm(instance=alerta, usuario_logado=request.user)

    contexto = {
        "titulo_pagina": "Editar alerta",
        "form": form,
        "alerta": alerta,
        "modo_edicao": True,
    }

    return render(request, "alertas/formulario.html", contexto)


@login_required
def alerta_excluir(request, pk):
    alerta = get_object_or_404(_alertas_visiveis(request), pk=pk)

    if request.method == "POST":
        identificador = alerta.id
        alerta.delete()

        messages.success(
            request,
            f"Alerta {identificador} excluído com sucesso.",
        )

        return redirect("alerta_listar")

    contexto = {
        "titulo_pagina": "Excluir alerta",
        "objeto_nome": f"Alerta {alerta.id}",
        "url_cancelar": "alerta_detalhar",
        "objeto_pk": alerta.pk,
    }

    return render(request, "core/confirmar_exclusao.html", contexto)