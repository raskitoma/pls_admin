function canjeup(pin) {
    let response = fetch("/redeem" , {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            "pin": pin
        })
    })
    .then(response => response.json())
    .then(result => {
        if (result.status == 200) {
            toaster("Canje exitoso! Redirigiendo a pronóstico en 5 segundos.", "success");
            setTimeout(function(){ window.location.href = "/pronosticos?quinela=" + result.quinelas ; }, 5000);
        } else {
            toaster(result.message, "danger");
        }
        document.getElementById("canjeupPin").value = "";
        document.getElementById("canjeupPin").disabled = false;        
        document.getElementById("canjeupBtn").disabled = false;
        document.getElementById("canjeupBtn").innerHTML = 'Canjear';
        document.getElementById("canjeupPin").focus();
    })
    .catch(error => {
        console.log(response, error);
        toaster('Pin no pudo ser canjeado. Intente más tarde. Error: '+ error, 'danger');
    });
}

$(document).ready(function() {
    $("#canjeupBtn").click(function(e) {
        let pin = document.getElementById("canjeupPin").value;
        document.getElementById("canjeupPin").disabled = true; 
        document.getElementById("canjeupBtn").disabled = true;
        document.getElementById("canjeupBtn").innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Espere';
        canjeup(pin);
    });

    $("#canjeup").submit(function(e) { 
        e.preventDefault();
    });

});
