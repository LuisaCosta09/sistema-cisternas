from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods

from .forms import (
    AbastecimentoForm,
    AlertaForm,
    CisternaForm,
    MonitoramentoForm,
    UsuarioAtualizacaoForm,
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

# CRUD de usuários


@require_GET
def usuario_detalhar(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)

    contexto = {
        "titulo_pagina": "Detalhes do usuário",
        "usuario": usuario,
    }

    return render(
        request,
        "usuario/detalhes.html",
        contexto,
    )


@require_http_methods(["GET", "POST"])
def usuario_editar(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == "POST":
        form = UsuarioAtualizacaoForm(
            request.POST,
            instance=usuario,
        )

        if form.is_valid():
            usuario = form.save()

            messages.success(
                request,
                f"Usuário {usuario.nome} atualizado com sucesso.",
            )

            return redirect(
                "usuario_detalhar",
                pk=usuario.pk,
            )

    else:
        form = UsuarioAtualizacaoForm(instance=usuario)

    contexto = {
        "titulo_pagina": "Editar usuário",
        "form": form,
        "usuario": usuario,
        "modo_edicao": True,
    }

    return render(
        request,
        "usuario/formulario.html",
        contexto,
    )


@require_http_methods(["GET", "POST"])
def usuario_excluir(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == "POST":
        nome = usuario.nome
        usuario.delete()

        messages.success(
            request,
            f"Usuário {nome} excluído com sucesso.",
        )

        return redirect("usuario_listar")

    contexto = {
        "titulo_pagina": "Excluir usuário",
        "objeto_nome": usuario.nome,
        "aviso_exclusao": (
            "As cisternas e os monitoramentos pertencentes e "
            "relacionados também serão excluídos."
        ),
        "url_cancelar": "usuario_detalhar",
        "objeto_pk": usuario.pk,
    }

    return render(
        request,
        "cisternas/confirmar_exclusao.html",
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

# CRUD de alertas
@require_GET
def alerta_detalhar(request, pk):
    alerta = get_object_or_404(
        Alerta.objects.select_related("cisterna", "cisterna__usuario"),
        pk=pk,
    )
    contexto = {
        "titulo_pagina": "Detalhes do alerta",
        "alerta": alerta,
    }
    return render(request, "cisternas/alerta/detalhes.html", contexto)

@require_http_methods(["GET", "POST"])
def alerta_editar(request, pk):
    alerta = get_object_or_404(Alerta, pk=pk)

    if request.method == "POST":
        form = AlertaForm(request.POST, instance=alerta)

        if form.is_valid():
            alerta = form.save()

            messages.success(
                request,
                f"Alerta {alerta.id} atualizado com sucesso.",
            )

            return redirect("alerta_detalhar", pk=alerta.pk)

    else:
        form = AlertaForm(instance=alerta)

    contexto = {
        "titulo_pagina": "Editar alerta",
        "form": form,
        "alerta": alerta,
        "modo_edicao": True,
    }

    return render(request, "cisternas/alerta/formulario.html", contexto)


@require_http_methods(["GET", "POST"])
def alerta_excluir(request, pk):
    alerta = get_object_or_404(Alerta, pk=pk)

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

    return render(
        request,
        "cisternas/confirmar_exclusao.html",
        contexto,
    )

    # CRUD de abastecimentos
@require_GET
def abastecimento_detalhar(request, pk):
    abastecimento = get_object_or_404(
        Abastecimento.objects.select_related("usuario", "cisterna"),
        pk=pk,
    )

    contexto = {
        "titulo_pagina": "Detalhes do abastecimento",
        "abastecimento": abastecimento,
    }

    return render(
        request,
        "cisternas/abastecimento/detalhes.html",
        contexto,
    )

@require_http_methods(["GET", "POST"])
def abastecimento_editar(request, pk):
    abastecimento = get_object_or_404(
        Abastecimento,
        pk=pk,
    )

    if request.method == "POST":
        form = AbastecimentoForm(
            request.POST,
            instance=abastecimento,
        )

        if form.is_valid():
            abastecimento = form.save()

            messages.success(
                request,
                f"Abastecimento {abastecimento.id} atualizado com sucesso.",
            )

            return redirect(
                "abastecimento_detalhar",
                pk=abastecimento.pk,
            )

    else:
        form = AbastecimentoForm(instance=abastecimento)

    contexto = {
        "titulo_pagina": "Editar abastecimento",
        "form": form,
        "abastecimento": abastecimento,
        "modo_edicao": True,
    }

    return render(
        request,
        "cisternas/abastecimento/formulario.html",
        contexto,
    )

@require_http_methods(["GET", "POST"])
def abastecimento_excluir(request, pk):
    abastecimento = get_object_or_404(
        Abastecimento,
        pk=pk,
    )

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

    return render(
        request,
        "cisternas/confirmar_exclusao.html",
        contexto,
    )