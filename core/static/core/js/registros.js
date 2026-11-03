const camposComContador = document.querySelectorAll("[data-contador-campo]");

function obterLimite(campo) {
    const limite = Number(campo.getAttribute("maxlength"));

    if (Number.isNaN(limite) || limite <= 0) {
        return null;
    }

    return limite;
}

function localizarContador(campo) {
    const idContador = campo.dataset.contadorCampo;

    if (!idContador) {
        return null;
    }

    return document.getElementById(idContador);
}

function atualizarContador(campo) {
    const contador = localizarContador(campo);
    const limite = obterLimite(campo);

    if (!contador || limite === null) {
        return;
    }

    const usados = campo.value.length;
    const restantes = limite - usados;

    contador.textContent = `${usados}/${limite} caracteres`;
    contador.dataset.proximoLimite = restantes <= 25 ? "true" : "false";
}

function prepararCampo(campo) {
    atualizarContador(campo);

    campo.addEventListener("input", function () {
        atualizarContador(campo);
    });
}

camposComContador.forEach(prepararCampo);
