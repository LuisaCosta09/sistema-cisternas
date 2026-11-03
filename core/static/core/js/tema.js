(function () {
  var interruptor = document.getElementById("alternar-tema");
  var raiz = document.documentElement;

  if (!interruptor) {
    return;
  }

  interruptor.checked = raiz.getAttribute("data-bs-theme") === "dark";

  interruptor.addEventListener("change", function () {
    var novoTema = interruptor.checked ? "dark" : "light";

    raiz.setAttribute("data-bs-theme", novoTema);

    try {
      localStorage.setItem("tema", novoTema);
    } catch (erro) {
      /* sem armazenamento: o tema vale só até recarregar a página */
    }
  });
})();