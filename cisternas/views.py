from functools import wraps

from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .forms import (
    AbastecimentoForm,
    AlertaForm,
    CisternaForm,
    MonitoramentoForm,
    UsuarioAtualizacaoForm,
    UsuarioForm,
)
from .models import Abastecimento, Alerta, Cisterna, Monitoramento, Usuario

def administrador_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_active or not request.user.is_staff:
            raise PermissionDenied

        return view_func(request, *args, **kwargs)

    return _wrapped_view


def _usuarios_visiveis_para(request):
    usuarios = Usuario.objects.all()
    if not request.user.is_staff:
        usuarios = usuarios.filter(pk=request.user.pk)
    return usuarios

@login_required
def inicio(request):
    return redirect("cisterna_listar")

@login_required
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

@login_required
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

@login_required
def cisterna_detalhar(request, pk):
    cisterna = get_object_or_404(
        Cisterna.objects.select_related("usuario"),
        pk=pk,
    )

    contexto = {
        "titulo_pagina": "Detalhes da cisterna",
        "cisterna": cisterna,
    }

    return render(request, "cisternas/cisterna_detalhes.html", contexto)

@login_required
def cisterna_editar(request, pk):
    cisterna = get_object_or_404(Cisterna, pk=pk)

    if request.method == "POST":
        form = CisternaForm(request.POST, instance=cisterna)

        if form.is_valid():
            cisterna = form.save()

            messages.success(
                request,
                f"Cisterna {cisterna.id} atualizada com sucesso.",
            )

            return redirect("cisterna_detalhar", pk=cisterna.pk)

    else:
        form = CisternaForm(instance=cisterna)

    contexto = {
        "titulo_pagina": "Editar cisterna",
        "form": form,
        "cisterna": cisterna,
        "modo_edicao": True,
    }

    return render(request, "cisternas/cisterna_formulario.html", contexto)

@login_required
def cisterna_excluir(request, pk):
    cisterna = get_object_or_404(Cisterna, pk=pk)

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

    return render(request, "cisternas/confirmar_exclusao.html", contexto)

@login_required
def usuario_listar(request):
    usuarios = _usuarios_visiveis_para(request).order_by("nome", "username")

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

@login_required
@administrador_required
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

@login_required
def usuario_detalhar(request, pk):
    usuario = get_object_or_404(_usuarios_visiveis_para(request), pk=pk)

    contexto = {
        "titulo_pagina": "Detalhes do usuário",
        "usuario": usuario,
    }

    return render(
        request,
        "usuario/detalhes.html",
        contexto,
    )

@login_required
def usuario_editar(request, pk):
    usuario = get_object_or_404(_usuarios_visiveis_para(request), pk=pk)

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

@login_required
def usuario_excluir(request, pk):
    usuario = get_object_or_404(_usuarios_visiveis_para(request), pk=pk)
    excluindo_propria_conta = usuario.pk == request.user.pk

    if request.method == "POST":
        cisternas_do_usuario = Cisterna.objects.filter(usuario=usuario)
        possui_registro_de_terceiro = (
            Monitoramento.objects.filter(cisterna__in=cisternas_do_usuario)
            .exclude(usuario=usuario)
            .exists()
            or Abastecimento.objects.filter(cisterna__in=cisternas_do_usuario)
            .exclude(usuario=usuario)
            .exists()
        )

        if possui_registro_de_terceiro:
            messages.error(
                request,
                "A conta não pode ser excluída porque há monitoramentos ou "
                "abastecimentos de outros usuários vinculados às suas cisternas.",
            )
            return redirect("usuario_detalhar", pk=usuario.pk)

        nome = usuario.nome
        usuario.delete()

        if excluindo_propria_conta:
            logout(request)
            return redirect("entrar")

        messages.success(
            request,
            f"Usuário {nome} excluído com sucesso.",
        )

        return redirect("usuario_listar")

    contexto = {
        "titulo_pagina": "Excluir usuário",
        "objeto_nome": "sua conta" if excluindo_propria_conta else usuario.nome,
        "mensagem_confirmacao": (
            "Tem certeza de que deseja excluir sua conta? Se você continuar, "
            "todos os dados vinculados a esse usuário, incluindo os cadastros "
            "de cisternas, monitoramentos e alertas, também serão excluídos. "
            "Essa ação não poderá ser desfeita. Deseja realmente continuar?"
            if excluindo_propria_conta
            else ""
        ),
        "aviso_exclusao": (
            "Os abastecimentos vinculados às cisternas também serão excluídos."
            if excluindo_propria_conta
            else (
                "As cisternas, os monitoramentos e os abastecimentos "
                "vinculados ao usuário serão excluídos. Os alertas "
                "associados às cisternas também serão excluídos."
            )
        ),
        "url_cancelar": "usuario_detalhar",
        "objeto_pk": usuario.pk,
    }

    return render(
        request,
        "cisternas/confirmar_exclusao.html",
        contexto,
    )

@login_required
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

@login_required
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

@login_required
def monitoramento_detalhar(request, pk):
    monitoramento = get_object_or_404(
        Monitoramento.objects.select_related("usuario", "cisterna"),
        pk=pk,
    )

    contexto = {
        "titulo_pagina": "Detalhes do monitoramento",
        "monitoramento": monitoramento,
    }

    return render(request, "monitoramento/detalhes.html", contexto)

@login_required
def monitoramento_editar(request, pk):
    monitoramento = get_object_or_404(Monitoramento, pk=pk)

    if request.method == "POST":
        form = MonitoramentoForm(request.POST, instance=monitoramento)

        if form.is_valid():
            monitoramento = form.save()

            messages.success(
                request,
                f"Monitoramento {monitoramento.id} atualizado com sucesso.",
            )

            return redirect("monitoramento_detalhar", pk=monitoramento.pk)

    else:
        form = MonitoramentoForm(instance=monitoramento)

    contexto = {
        "titulo_pagina": "Editar monitoramento",
        "form": form,
        "monitoramento": monitoramento,
        "modo_edicao": True,
    }

    return render(request, "monitoramento/formulario.html", contexto)

@login_required
def monitoramento_excluir(request, pk):
    monitoramento = get_object_or_404(Monitoramento, pk=pk)

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

    return render(request, "cisternas/confirmar_exclusao.html", contexto)

@login_required
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

@login_required
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

@login_required
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

@login_required
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
@login_required
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

@login_required
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

@login_required
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
@login_required
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

@login_required
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

@login_required
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