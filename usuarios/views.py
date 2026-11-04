from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from abastecimentos.models import Abastecimento
from cisternas.models import Cisterna
from core.decorators import administrador_required
from monitoramentos.models import Monitoramento

from .forms import UsuarioAtualizacaoForm, UsuarioForm
from .models import Usuario


# ---------------------------------------------------------------------
# Autenticação
# ---------------------------------------------------------------------

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
    formulario.fields["username"].widget.attrs.update(
        {"class": "form-control", "autocomplete": "username"}
    )
    formulario.fields["password"].widget.attrs.update(
        {"class": "form-control", "autocomplete": "current-password"}
    )

    if request.method == "POST" and formulario.is_valid():
        usuario = formulario.get_user()
        login(request, usuario)
        messages.success(request, f"Bem-vindo, {usuario.username}!")
        return redirect(_destino_apos_login(request))

    return render(
        request,
        "usuarios/entrar.html",
        {
            "form": formulario,
            "proximo": request.POST.get("next")
            or request.GET.get("next", ""),
        },
    )


@require_POST
def sair(request):
    logout(request)
    messages.info(request, "Você saiu do sistema.")
    return redirect("entrar")


# ---------------------------------------------------------------------
# CRUD de usuários
# ---------------------------------------------------------------------

def _usuarios_visiveis_para(request):
    usuarios = Usuario.objects.all()
    if not request.user.is_staff:
        usuarios = usuarios.filter(pk=request.user.pk)
    return usuarios


@login_required
@permission_required('usuarios.view_usuario', raise_exception=True)
def usuario_listar(request):
    if not request.user.is_staff:
        return redirect("usuario_detalhar", pk=request.user.pk)

    usuarios = Usuario.objects.order_by("nome", "username")

    contexto = {
        "titulo_pagina": "Usuários cadastrados",
        "usuarios": usuarios,
        "quantidade_usuarios": usuarios.count(),
    }

    return render(
        request,
        "usuarios/listar.html",
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
        "usuarios/formulario.html",
        contexto,
    )


@login_required
@permission_required('usuarios.view_usuario', raise_exception=True)
def usuario_detalhar(request, pk):
    usuario = get_object_or_404(_usuarios_visiveis_para(request), pk=pk)

    contexto = {
        "titulo_pagina": "Detalhes do usuário",
        "usuario": usuario,
        "cisternas": usuario.cisternas.order_by("id"),
    }

    return render(
        request,
        "usuarios/detalhes.html",
        contexto,
    )


@login_required
@permission_required('usuarios.change_usuario', raise_exception=True)
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
        "usuarios/formulario.html",
        contexto,
    )


@login_required
@permission_required('usuarios.delete_usuario', raise_exception=True)
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
        "core/confirmar_exclusao.html",
        contexto,
    )