function start_forgot(user_mail) {
    let otp_kind = "forgot";
    let otp_path = "/password-forgot";
    start_otp(user_mail, otp_kind, otp_path);
}

function check_otp(otp, user_mail) {
    let otp_source = "forgot";
    let otp_path = "/otp_reset";
    recheck_otp(otp, user_mail, otp_source, otp_path);
}

function change_pass(mail, password, confirm_password) {
    let response = fetch("/password-reset" , {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            "mail_to": mail,
            "password": password,
            "confirm_password": confirm_password
        })
    })
    .then(response => response.json())
    .then(result => {
        if (result.status == 200) {
            toaster("Contraseña actualizada!", "success");
            document.getElementById("alerterotp2").innerHTML = '<div class="alert alert-success" role="alert" data-bs-animation="true" data-bs-autohide="true" data-bs-delay="1000" >' + result.message + '</div>';
            $("#pass_change").modal("hide");
            $("#reset_success").modal("show");	
            // redirect user to Login after 5 seconds:
            setTimeout(function(){ window.location.href = "/"; }, 5000);
        } else {
            toaster(result.message, "danger");
            document.getElementById("alerterotp2").innerHTML = '<div class="alert alert-danger" role="alert" data-bs-animation="true" data-bs-autohide="true" data-bs-delay="2000" >' + result.message + '</div>';
        }
        document.getElementById("password").disabled = false;
        document.getElementById("password_repeat").disabled = false;
        document.getElementById("passBtn").innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Cambiar contraseña';
        document.getElementById("passBtn").disabled = false;
        document.getElementById("cancelPass").disabled = false;
    })
    .catch(error => {
        console.log(response, error);
        toaster(error, 'danger');
        document.getElementById("alerterotp").innerHTML = '<div class="alert alert-danger" role="alert" data-bs-animation="true" data-bs-autohide="true" data-bs-delay="2000" >' + error + '</div>';
    });
}

$(document).ready(function() {
    $("#forgot_form").submit(function(e) {
        e.preventDefault();
        let user_mail = document.getElementById("mail");
        document.getElementById("forgot_btn").disabled = true;
        document.getElementById("mail").disabled = true;
        document.getElementById("forgot_btn").innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Enviando mail, no cerrar ni recargar esta ventana! Por favor espere...';
        start_forgot(user_mail.value);
    });

    $("#forgot_otp").submit(function(e) {
        e.preventDefault();
    });

    $("#reset_form").submit(function(e) {
        e.preventDefault();
    });

    $("#passBtn").click(function(e) {
        let mail_to = document.getElementById("mail").value;
        let password = document.getElementById("password").value;
        let confirm_password = document.getElementById("password_repeat").value;
        if (password == '' || confirm_password == '') {
            toaster("Por favor, rellena todos los campos", "danger");
            document.getElementById("alerterotp2").innerHTML = '<div class="alert alert-danger" role="alert" data-bs-animation="true" data-bs-autohide="true" data-bs-delay="2000" >Por favor, rellena todos los campos</div>';
            return false;
        }
        if (password != confirm_password) {
            toaster("Las contraseñas no coinciden!", "danger");
            document.getElementById("alerterotp2").innerHTML = '<div class="alert alert-danger" role="alert" data-bs-animation="true" data-bs-autohide="true" data-bs-delay="2000" >Las contraseñas no coinciden!</div>';
            return false;
        }
        document.getElementById("password").disabled = true;
        document.getElementById("password_repeat").disabled = true;
        document.getElementById("passBtn").innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Cambiando contraseña...';
        document.getElementById("passBtn").disabled = true;
        document.getElementById("cancelPass").disabled = true;
        change_pass(mail_to, password, confirm_password);
    });

    $("#cancelPass").click(function(e) {  // Cancel OTP
        document.getElementById("reset_form").reset();
        $("#dmail2").val(document.getElementById("mail").value);
        document.getElementById("passBtn").disabled = false;
        document.getElementById("passBtn").innerHTML = 'Confirmar Código';
    });
});
