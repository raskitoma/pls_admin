function start_otp(user_mail, otp_kind, otp_path) {
    let response = fetch(otp_path , {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            "mail_to": user_mail
        })
    })
    .then(response => response.json())
    .then(result => {
        if (result.status == 200) {
            toaster("Código OTP generado y enviado...", "success");
            $("#otpCheck").modal("show");
            if(otp_kind == "forgot"){
                $("#dmail").val(user_mail);
            }
            $("#mail_sent_to").innerHTML = user_mail;
            document.getElementById("digit-1").focus();
            timer("timer", 10);
        } else {
            toaster(result.message, "danger");
        }
        if(otp_kind == "forgot"){
            document.getElementById("forgot_btn").disabled = false;
            document.getElementById("mail").disabled = false;
            document.getElementById("forgot_btn").innerHTML = 'Recuperar Contraseña';
        }
        if(otp_kind == "confirm"){
            document.getElementById("confirm_start").disabled = false;
            document.getElementById("confirm_start").innerHTML = 'Confirmar correo.';
        }
    })
    .catch(error => {
        console.log(response, error);
        toaster('OTP no pudo ser enviado a su correo. Intente más tarde. Error: '+ error, 'danger');
    });
}

function recheck_otp(otp, user_mail, otp_source, otp_path) {
    let response = fetch(otp_path , {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            "otp_data": otp,
            "mail_to": user_mail
        })
    })
    .then(response => response.json())
    .then(result => {
        if (result.status == 200) {
            toaster("Código OTP validado!", "success");
            document.getElementById("alerterotp").innerHTML = '<div class="alert alert-success" role="alert" data-bs-animation="true" data-bs-autohide="true" data-bs-delay="1000" >' + result.message + '</div>';
            $("#otpCheck").modal("hide");
            if(otp_source == "forgot"){
                $("#pass_change").modal("show");
                $("#dmail2").val(user_mail);
                $("#mail_sent_to2").innerHTML = user_mail;
            }
            if(otp_source == "confirm"){
                $("#confirm_success").modal("show");	
                // redirect user to Login after 5 seconds:
                setTimeout(function(){ window.location.href = "/"; }, 5000);    
            }
        } else {
            toaster(result.message, "danger");
            document.getElementById("alerterotp").innerHTML = '<div class="alert alert-danger" role="alert" data-bs-animation="true" data-bs-autohide="true" data-bs-delay="2000" >' + result.message + '</div>';
        }
        document.getElementById("forgot_otp").reset();
        document.getElementById("otpBtn").disabled = false;
        document.getElementsByClassName("digit-group").disabled = false;
        $('.digit-group').find('input').each(function() {
            $(this).prop("disabled", false);
            $(this).val("");
        });
        document.getElementById("otpBtn").innerHTML = 'Confirmar Código';
    })
    .catch(error => {
        console.log(response, error);
        toaster(error, 'danger');
        document.getElementById("alerterotp").innerHTML = '<div class="alert alert-danger" role="alert" data-bs-animation="true" data-bs-autohide="true" data-bs-delay="2000" >' + error + '</div>';
    });
}