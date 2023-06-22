// function that shows a timer based on object and minutes:
function timer(object, minutes) {
    let seconds = 60;
    let mins = minutes
    function tick() {
        let counter = document.getElementById(object);
        let current_minutes = mins-1
        seconds--;
        counter.innerHTML = 'Código expira en: ' + current_minutes.toString() + ":" + (seconds < 10 ? "0" : "") + String(seconds);
        if( seconds > 0 ) {
            setTimeout(tick, 1000);
        } else {
            if(mins > 1){
                timer(object, mins-1);
            }
        }
    }
    tick();
}

$('.digit-group').find('input').each(function() {
    $(this).attr('maxlength', 1);
    $(this).on('keyup', function(e) {
        let parent = $($(this).parent());
        if(e.keyCode === 8 || e.keyCode === 37) {
            let prev = parent.find('input#' + $(this).data('previous'));
            if(prev.length) {
                $(prev).select();
            }
            } else if((e.keyCode >= 48 && e.keyCode <= 57) || (e.keyCode >= 65 && e.keyCode <= 90) || (e.keyCode >= 96 && e.keyCode <= 105) || e.keyCode === 39) {
                let next = parent.find('input#' + $(this).data('next'));
                if(next.length) {
                    $(next).select();
                } else {
                    if(parent.data('autosubmit')) {
                        parent.submit();
                    }
                }
            }
        });
    }
);

$(document).ready(function() {
    $("#cancelBtn").click(function(e) {  // Cancel OTP
        document.getElementById("forgot_otp").reset();
        $("#dmail").val(document.getElementById("mail").value);
        document.getElementById("otpBtn").disabled = false;
        document.getElementsByClassName("digit-group").disabled = false;
        $('.digit-group').find('input').each(function() {
            $(this).prop("disabled", false);
        });
        document.getElementById("otpBtn").innerHTML = 'Confirmar Código';
    });

    $("#otpBtn").click(function(e) {  // Sending OTP and check!
        let user_mail = document.getElementById("mail");
        // disable button and mail
        document.getElementById("otpBtn").disabled = true;
        document.getElementsByClassName("digit-group").disabled = true;
        let otp_to_check = document.getElementById("digit-1").value + document.getElementById("digit-2").value + document.getElementById("digit-3").value + document.getElementById("digit-4").value + document.getElementById("digit-5").value + document.getElementById("digit-6").value;
        $('.digit-group').find('input').each(function() {
            $(this).prop("disabled", true);
        });
        document.getElementById("otpBtn").innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Confirmando código...';
        check_otp(otp_to_check, user_mail.value);
    });

});