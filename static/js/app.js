// Este archivo contiene lógica del frontend.
// Su función principal es permitir agregar más proyectos al reporte
// y calcular automáticamente la suma de porcentajes antes de enviar.

function addRow() {
    const rows = document.getElementById("rows");
    const firstRow = document.querySelector(".report-row");
    const newRow = firstRow.cloneNode(true);

    const input = newRow.querySelector("input");
    input.value = "";

    rows.appendChild(newRow);
    attachPercentageListeners();
}

function calculateTotal() {
    const inputs = document.querySelectorAll("input[name='percentage']");
    let total = 0;

    inputs.forEach(input => {
        const value = parseFloat(input.value);
        if (!isNaN(value)) {
            total += value;
        }
    });

    document.getElementById("total").innerText = total.toFixed(2);
}

function attachPercentageListeners() {
    const inputs = document.querySelectorAll("input[name='percentage']");
    inputs.forEach(input => {
        input.removeEventListener("input", calculateTotal);
        input.addEventListener("input", calculateTotal);
    });
}

document.addEventListener("DOMContentLoaded", attachPercentageListeners);
