function qcalculate() {
    let response = fetch("/qcalculate" , {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
    })
    .then(response => response.json())
    .then(result => {
        console.log(result);
        if (result.status == 200) {
            toaster(result.message, "success");
        } else {
            toaster(result.message, "danger");
        }
        document.getElementById("calculateForm").disabled = false;
        document.getElementById("calculateBtn").disabled = false;
        document.getElementById("calculateBtn").innerHTML = 'Calcular Tarjetas/Partidos';
    })
    .catch(error => {
        console.log(response, error);
        toaster('No se puede realizar cálculo. Intente más tarde. Error: '+ error, 'danger');
    });
}

$(document).ready(function() {
    $("#calculateBtn").click(function(e) {
        document.getElementById("calculateForm").disabled = true; 
        document.getElementById("calculateBtn").disabled = true;
        document.getElementById("calculateBtn").innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Calculando, espere...';
        qcalculate();
    });

    $("#calculateForm").submit(function(e) { 
        e.preventDefault();
    });

});

