document.addEventListener("DOMContentLoaded", () => {
    $('#contractData').on('hidden.bs.modal', function (e) {
        $('#loadingModal').modal('hide');
    });
    $('#errorData').on('hidden.bs.modal', function (e) {
        $('#loadingModal').modal('hide');
    })    
    let trs = document.querySelectorAll("tr");
    trs.forEach(tr => {
        tr.onclick = async () => {
            let checkbox = tr.querySelector("input[type='checkbox'][name='rowid']");
            if (checkbox) {
                $('#loadingModal').modal('show');
                let request_url = window.location.origin + "/admin/contract_view/get_contract_view";
                let response = await fetch(request_url, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ rowid: checkbox.value })
                });
                if (response.status == 200) {
                    let data = await response.json();
                    let cd_title = document.querySelector("#contractData .modal-title");
                    cd_title.innerHTML = `${data.property} - ${data.tenant}<br>${data.status}`;
                    document.querySelector("#contractData #property").innerHTML = data.property;
                    document.querySelector("#contractData #tenant").innerHTML = data.tenant;
                    document.querySelector("#contractData #startdate").innerHTML = data.start;
                    document.querySelector("#contractData #enddate").innerHTML = data.end;
                    document.querySelector("#contractData #rent").innerHTML = data.rent;
                    document.querySelector("#contractData #parking").innerHTML = data.parking;
                    let iframe_url = `${window.location.origin}/admin/contract_view/get_contract_signed/${data.id}/`;
                    document.querySelector("#contractData iframe").setAttribute("src", iframe_url);
                    $('#contractData').modal('show');
                } else {
                    document.querySelector("#errorData #errorData_message").innerHTML = response;
                    $('#errorData').modal('show');
                }
            }
        }
    });
});