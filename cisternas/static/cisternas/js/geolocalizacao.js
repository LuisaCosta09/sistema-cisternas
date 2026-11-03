const botaoLocalizacao = document.getElementById("usar-localizacao");
const campoLatitude = document.getElementById("id_latitude");
const campoLongitude = document.getElementById("id_longitude");
const mensagemLocalizacao = document.getElementById("mensagem-localizacao");
const linkConferirMapa = document.getElementById("conferir-mapa");

function atualizarMensagem(texto, tipo) {
  if (!mensagemLocalizacao) {
    return;
  }

  mensagemLocalizacao.textContent = texto;
  mensagemLocalizacao.dataset.tipo = tipo;
}

function atualizarLinkMapa() {
  if (!linkConferirMapa || !campoLatitude || !campoLongitude) {
    return;
  }

  const latitude = Number.parseFloat(campoLatitude.value.replace(",", "."));
  const longitude = Number.parseFloat(campoLongitude.value.replace(",", "."));

  if (Number.isNaN(latitude) || Number.isNaN(longitude)) {
    linkConferirMapa.classList.add("d-none");
    return;
  }

  linkConferirMapa.href =
    "https://www.google.com/maps/search/?api=1&query=" + latitude + "," + longitude;
  linkConferirMapa.classList.remove("d-none");
}

function preencherCoordenadas(position) {
  const latitude = position.coords.latitude;
  const longitude = position.coords.longitude;
  const precisao = Math.round(position.coords.accuracy);

  campoLatitude.value = latitude.toFixed(7);
  campoLongitude.value = longitude.toFixed(7);

  if (precisao > 200) {
    atualizarMensagem(
      "Posição preenchida, mas com precisão baixa (cerca de " +
        precisao +
        " m). Confira no mapa e ajuste se precisar.",
      "erro"
    );
  } else {
    atualizarMensagem(
      "Posição preenchida (precisão de cerca de " + precisao + " m).",
      "sucesso"
    );
  }

  atualizarLinkMapa();
  botaoLocalizacao.disabled = false;
}

function tratarErroLocalizacao(error) {
  let mensagem = "Não foi possível obter a localização. Preencha manualmente.";

  if (error.code === error.PERMISSION_DENIED) {
    mensagem =
      "A permissão de localização foi negada. Preencha as coordenadas manualmente.";
  }

  if (error.code === error.POSITION_UNAVAILABLE) {
    mensagem = "A localização do dispositivo está indisponível no momento.";
  }

  if (error.code === error.TIMEOUT) {
    mensagem = "O tempo para obter a localização foi excedido. Tente novamente.";
  }

  atualizarMensagem(mensagem, "erro");
  botaoLocalizacao.disabled = false;
}

function solicitarLocalizacao() {
  if (!navigator.geolocation) {
    atualizarMensagem(
      "Este navegador não oferece suporte à geolocalização.",
      "erro"
    );
    return;
  }

  botaoLocalizacao.disabled = true;
  atualizarMensagem("Obtendo localização...", "carregando");

  navigator.geolocation.getCurrentPosition(
    preencherCoordenadas,
    tratarErroLocalizacao,
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 0,
    }
  );
}

if (campoLatitude && campoLongitude) {
  campoLatitude.addEventListener("input", atualizarLinkMapa);
  campoLongitude.addEventListener("input", atualizarLinkMapa);
  atualizarLinkMapa();
}

if (
  botaoLocalizacao
  && campoLatitude
  && campoLongitude
  && mensagemLocalizacao
) {
  botaoLocalizacao.addEventListener("click", solicitarLocalizacao);
}