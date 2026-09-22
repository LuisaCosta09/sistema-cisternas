const campoCpf = document.getElementById("id_cpf");

function manterSomenteNumeros(valor) {
    return valor.replace(/\D/g, "").slice(0, 11);
}

function atualizarCpf(event) {
    const valorDigitado = event.target.value;
    const valorNumerico = manterSomenteNumeros(valorDigitado);

    if (valorDigitado !== valorNumerico) {
        event.target.value = valorNumerico;
    }
}

function impedirCaracterInvalido(event) {
    const teclasPermitidas = [
        "Backspace",
        "Delete",
        "ArrowLeft",
        "ArrowRight",
        "Home",
        "End",
        "Tab",
    ];

    if (teclasPermitidas.includes(event.key)) {
        return;
    }

    if (/^\d$/.test(event.key)) {
        return;
    }

    event.preventDefault();
}

function normalizarCpfColado() {
    window.setTimeout(() => {
        campoCpf.value = manterSomenteNumeros(campoCpf.value);
    }, 0);
}

if (campoCpf) {
    campoCpf.addEventListener("input", atualizarCpf);
    campoCpf.addEventListener("keydown", impedirCaracterInvalido);
    campoCpf.addEventListener("paste", normalizarCpfColado);
}