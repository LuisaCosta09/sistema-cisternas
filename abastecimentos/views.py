from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from core.permissoes import filtrar_por_dono

from .forms import AbastecimentoForm
from .models import Abastecimento


def _abastecimentos_visiveis(request):
    abastecimentos = Abastecimento.objects.select_related("usuario", "cisterna")
    return filtrar_por_dono(abastecimentos, request.user, "cisterna__usuario")


@login_required
def abastecimento_listar(request):
    abastecimentos = _abastecimentos_visiveis(request)

    contexto = {
        "titulo_pagina": "Abastecimentos cadastrados",
        "abastecimentos": abastecimentos,
        "quantidade_abastecimentos": abastecimentos.count(),
    }

    return render(request, "abastecimentos/listar.html", contexto)


@login_required
def abastecimento_criar(request):
    if request.method == "POST":
        form = AbastecimentoForm(request.POST, usuario_logado=request.user)

        if form.is_valid():
            abastecimento = form.save()

            messages.success(
                request,
                f"Abastecimento {abastecimento.id} cadastrado com sucesso.",
            )

            return redirect("abastecimento_listar")

    else:
        form = AbastecimentoForm(usuario_logado=request.user)

    contexto = {
        "titulo_pagina": "Cadastrar abastecimento",
        "form": form,
    }

    return render(request, "abastecimentos/formulario.html", contexto)


@login_required
def abastecimento_detalhar(request, pk):
    abastecimento = get_object_or_404(_abastecimentos_visiveis(request), pk=pk)

    contexto = {
        "titulo_pagina": "Detalhes do abastecimento",
        "abastecimento": abastecimento,
    }

    return render(request, "abastecimentos/detalhes.html", contexto)


@login_required
def abastecimento_editar(request, pk):
    abastecimento = get_object_or_404(_abastecimentos_visiveis(request), pk=pk)

    if request.method == "POST":
        form = AbastecimentoForm(
            request.POST,
            instance=abastecimento,
            usuario_logado=request.user,
        )

        if form.is_valid():
            abastecimento = form.save()

            messages.success(
                request,
                f"Abastecimento {abastecimento.id} atualizado com sucesso.",
            )

            return redirect("abastecimento_detalhar", pk=abastecimento.pk)

    else:
        form = AbastecimentoForm(
            instance=abastecimento,
            usuario_logado=request.user,
        )

    contexto = {
        "titulo_pagina": "Editar abastecimento",
        "form": form,
        "abastecimento": abastecimento,
        "modo_edicao": True,
    }

    return render(request, "abastecimentos/formulario.html", contexto)


@login_required
def abastecimento_excluir(request, pk):
    abastecimento = get_object_or_404(_abastecimentos_visiveis(request), pk=pk)

    if request.method == "POST":
        identificador = abastecimento.id
        abastecimento.delete()

        messages.success(
            request,
            f"Abastecimento {identificador} excluído com sucesso.",
        )

        return redirect("abastecimento_listar")

    contexto = {
        "titulo_pagina": "Excluir abastecimento",
        "objeto_nome": f"Abastecimento {abastecimento.id}",
        "url_cancelar": "abastecimento_detalhar",
        "objeto_pk": abastecimento.pk,
    }

    return render(request, "core/confirmar_exclusao.html", contexto)