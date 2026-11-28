async function cargar(tabla, parametros = "") {
  const respuesta = await fetch("/api/" + tabla.dataset.recurso + parametros);
  const datos = await respuesta.json();
  if (!Array.isArray(datos) || datos.length === 0) {
    tabla.innerHTML = "<tr><td>Sin resultados</td></tr>";
    return;
  }
  const columnas = Object.keys(datos[0]);
  let html = "<tr>" + columnas.map(c => "<th>" + c + "</th>").join("") + "</tr>";
  datos.forEach(fila => {
    html += "<tr>" + columnas.map(c => "<td>" + (fila[c] ?? "") + "</td>").join("") + "</tr>";
  });
  tabla.innerHTML = html;
}

function cargarVisibles() {
  document.querySelectorAll("section:not([hidden]) table").forEach(tabla => {
    if (tabla.dataset.recurso !== "municipios" && tabla.dataset.recurso !== "localidades") cargar(tabla);
  });
}

document.querySelectorAll("nav button").forEach(boton => {
  boton.addEventListener("click", () => {
    document.querySelectorAll("nav button").forEach(b => b.classList.remove("activo"));
    boton.classList.add("activo");
    document.querySelectorAll("section").forEach(s => s.hidden = s.id !== boton.dataset.modulo);
    cargarVisibles();
  });
});

document.querySelectorAll("form.filtro").forEach(formulario => {
  formulario.addEventListener("submit", evento => {
    evento.preventDefault();
    const datos = new FormData(formulario);
    const tabla = document.querySelector('table[data-recurso="' + formulario.dataset.recurso + '"]');
    cargar(tabla, "?desde=" + encodeURIComponent(datos.get("desde")) + "&hasta=" + encodeURIComponent(datos.get("hasta")));
  });
});

document.querySelectorAll("form.accion").forEach(formulario => {
  formulario.addEventListener("submit", async evento => {
    evento.preventDefault();
    const cuerpo = Object.fromEntries(new FormData(formulario));
    const respuesta = await fetch(formulario.dataset.url, {
      method: formulario.dataset.metodo,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(cuerpo)
    });
    const resultado = await respuesta.json();
    alert(resultado.mensaje);
    formulario.reset();
    cargarVisibles();
  });
});

document.querySelectorAll("form.busqueda").forEach(formulario => {
  formulario.addEventListener("submit", evento => {
    evento.preventDefault();
    const datos = new FormData(formulario);
    const tabla = document.querySelector('table[data-recurso="' + formulario.dataset.recurso + '"]');
    cargar(tabla, "?q=" + encodeURIComponent(datos.get("q")));
  });
});

document.querySelectorAll("table").forEach(tabla => {
  const caja = document.createElement("div");
  caja.className = "caja-tabla";
  tabla.parentNode.insertBefore(caja, tabla);
  caja.appendChild(tabla);
});

cargar(document.querySelector('table[data-recurso="entidades"]'));