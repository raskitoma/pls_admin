document.addEventListener("DOMContentLoaded", () => {
    $('#doc_modal').on('hidden.bs.modal', function (e) {
        $('#loadingModal').modal('hide');
    });
    $('#errorData').on('hidden.bs.modal', function (e) {
        $('#loadingModal').modal('hide');
    })
    $('#doc_modal').on('submit', function (e) {
        let submit_button = document.getElementById('doc_submit');
        submit_button.disabled = true;
        submit_button.innerHTML = 'Saving...&nbsp;<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
        $('#loadingModal').modal('show');
    });    
});

function start_button_action(my_source) {
    let elements = document.querySelectorAll('button[data-doc_action]');
    elements.forEach(function(object) {
        object.addEventListener('click', function(event) {
            let action = object.getAttribute('data-doc_action');
            let ajaxurl = `${window.location.origin}${my_source}${action}`;
            let send_data = {
                object_id: object.getAttribute('data-object_id'),
                doc_id: object.getAttribute('data-doc_id'),
                my_source: object.getAttribute('data-source'),
            };
            let call_method = 'POST';
            let confirm_msg = 'Are you sure you want to ';
            switch(action) {
                case 'doc_status':
                    confirm_msg += 'change the status of this document?';
                    break;
                case 'doc_delete':
                    confirm_msg += 'delete this document? This action is irreversible!';
                    call_method = 'DELETE';
                    break;
                case 'doc_edit':
                    confirm_msg += 'edit this document? This action is irreversible!';
                    break;
                case 'doc_new':
                    confirm_msg += 'add a new document?';
                    break;
                default:
                    return;
            }
            if (action=='doc_edit') {
                // open modal 
                document.getElementById('doc_modallabel').innerHTML = 'Replace Document';
                document.querySelector('#doc_modal [name="mod_doc_id"]').value = send_data.doc_id;
                document.querySelector('#doc_modal [name="action"]').value = 'edit';
                if (confirm(confirm_msg))
                    $('#doc_modal').modal('show');
            } else if (action=='doc_new') {
                // open modal 
                document.getElementById('doc_modallabel').innerHTML = 'Add Document';
                document.querySelector('#doc_modal [name="mod_doc_id"]').value = '';
                document.querySelector('#doc_modal [name="action"]').value = 'save';
                if (confirm(confirm_msg))
                    $('#doc_modal').modal('show');
            } else {
                if (confirm(confirm_msg)) {
                    $('#loadingModal').modal('show');
                    fetch(ajaxurl, {
                        method: call_method,
                        body: JSON.stringify(send_data),
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        $('#loadingModal').modal('hide');
                        if (data.status==200) {
                            let refresh_location=`${window.location.origin}${my_source}xtrasdocs?id=${send_data.object_id}`;
                            location.href=refresh_location;
                        }
                    })
                    .catch((error) => {
                        console.error('Error:', error);
                    });
                }
            }
        }); 
    });
}