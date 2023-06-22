function start_confirm(self) {
    let otp_kind = "confirm";
    let otp_path = "/otp";
    start_otp(user_mail, otp_kind, otp_path);
}

function check_otp(otp, user_mail) {
    let otp_kind = "confirm";
    let otp_path = "/otp_check";
    recheck_otp(otp, user_mail, otp_kind, otp_path);
}

$(document).ready(function() {
    $("#confirm_start").click(function(e) {
        let user_mail = document.getElementById("confirm_start").dataset.user_mail;
        document.getElementById("confirm_start").disabled = true;
        document.getElementById("confirm_start").innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Enviando mail...';
        start_confirm(user_mail);
    });
});
