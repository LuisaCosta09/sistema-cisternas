from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from core.permissoes import filtrar_por_dono

from .forms import MonitoramentoForm
from .models import Monitoramento


def _monitoramentos_visiveis(request):
    monitoramentos = Monitoramento.objects.select_related("usuario", "cisterna")
    return filtrar_por_dono(monitoramentos, request.user, "cisterna__usuario")


@login_required
def monitoramento_listar(request):
    monitoramentos = _monitoramentos_visiveis(request)

    contexto = {
        "titulo_pagina": "Monitoramentos cadastrados",
        "monitoramentos": monitoramentos,
        "quantidade_monitoramentos": monitoramentos.count(),
    }

    return render(request, "monitoramentos/listar.html", contexto)


@login_required
def monitoramento_criar(request):
    if request.method == "POST":
        form = MonitoramentoForm(request.POST, usuario_logado=request.user)

        if form.is_valid():
            monitoramento = form.save()

            messages.success(
                request,
                f"Monitoramento {monitoramento.id} cadastrado com sucesso.",
            )

            return redirect("monitoramento_listar")

    else:
        form = MonitoramentoForm(usuario_logado=request.user)

    contexto = {
        "titulo_pagina": "Cadastrar monitoramento",
        "form": form,
    }

    return render(request, "monitoramentos/formulario.html", contexto)


@login_required
def monitoramento_detalhar(request, pk):
    monitoramento = get_object_or_404(_monitoramentos_visiveis(request), pk=pk)

    contexto = {
        "titulo_pagina": "Detalhes do monitoramento",
        "monitoramento": monitoramento,
    }

    return render(request, "monitoramentos/detalhes.html", contexto)


@login_required
def monitoramento_editar(request, pk):
    monitoramento = get_object_or_404(_monitoramentos_visiveis(request), pk=pk)

    if request.method == "POST":
        form = MonitoramentoForm(
            request.POST,
            instance=monitoramento,
            usuario_logado=request.user,
        )

        if form.is_valid():
            monitoramento = form.save()

            messages.success(
                request,
                f"Monitoramento {monitoramento.id} atualizado com sucesso.",
            )

            return redirect("monitoramento_detalhar", pk=monitoramento.pk)

    else:
        form = MonitoramentoForm(
            instance=monitoramento,
            usuario_logado=request.user,
        )

    contexto = {
        "titulo_pagina": "Editar monitoramento",
        "form": form,
        "monitoramento": monitoramento,
        "modo_edicao": True,
    }

    return render(request, "monitoramentos/formulario.html", contexto)


@login_required
def monitoramento_excluir(request, pk):
    monitoramento = get_object_or_404(_monitoramentos_visiveis(request), pk=pk)

    if request.method == "POST":
        identificador = monitoramento.id
        monitoramento.delete()

        messages.success(
            request,
            f"Monitoramento {identificador} excluído com sucesso.",
        )

        return redirect("monitoramento_listar")

    contexto = {
        "titulo_pagina": "Excluir monitoramento",
        "objeto_nome": f"Monitoramento {monitoramento.id}",
        "url_cancelar": "monitoramento_detalhar",
        "objeto_pk": monitoramento.pk,
    }

    return render(request, "core/confirmar_exclusao.html", contexto)