$(document).ready(function() {
    actionable_buttons();

});


function actionable_buttons() {
    let elements = document.querySelectorAll('button[data-object_id]');
    elements.forEach(function(object) {
        // lets get button status
        let my_object_id = object.getAttribute('data-object_id');
        let action = object.getAttribute('data-action');
        let doc_url = `${window.location.origin}/admin/docs_core/doc_status`;
        let doc_data = {
            object_id: my_object_id,
        };
        let doc_method = 'POST';
        fetch (doc_url, { method:doc_method, body: JSON.stringify(doc_data), headers: {'Content-Type': 'application/json',} })
        .then(response => response.json())
        .then(data => {
            let doc_status = data;
            switch(action) {
                case 'doc_review':
                case 'doc_delete':
                    if (!doc_status.in_db) 
                        object.setAttribute('disabled', 'disabled');
                    if (doc_status.in_db && !doc_status.in_mayan)
                        object.setAttribute('disabled', 'disabled');
                    break;
                case 'doc_upload':
                    switch(doc_status.in_mayan) {
                        case true:
                            object.setAttribute('disabled', 'disabled');
                            break;
                        case false:
                            object.removeAttribute('disabled');
                    }
                    break;

            }
            object.addEventListener('click', function(event) {
                let ajaxurl = `${window.location.origin}/admin/docs_core/doc_handler`;
                let send_data = {
                    object_id: my_object_id,
                    doc_id: object.getAttribute('data-doc_id'),
                };
                let call_method = 'POST';
                let confirm_msg = 'Are you sure you want to ';
                switch(action) {
                    case 'doc_review':
                        call_method = 'GET';
                        confirm_msg += 'review this document?';
                        break;
                    case 'doc_delete':
                        confirm_msg += 'unlink this document? This action is irreversible!';
                        call_method = 'DELETE';
                        break;
                    case 'doc_upload':
                        confirm_msg += 'upload a new document?';
                        break;
                    default:
                        return;
                }
                if (confirm(confirm_msg)) {
                    if (action=='doc_upload') {
                        // set the value of hidden field 'object_id' inside the modal "doc_modal"
                        let doc_modal = $('#doc_modal');
                        let doc_modal_input = doc_modal.find('input[name="object_id"]');
                        doc_modal_input.val(my_object_id);
                        doc_modal.modal('show');
                        return;
                    } else if (action=='doc_review') {
                        let doc_url = `${ajaxurl}?object_id=${my_object_id}`;
                        // open a new tab to review the document
                        window.open(doc_url);
                        return;
                    } else if (action=='doc_delete') {
                        fetch(ajaxurl, {
                            method: call_method,
                            body: JSON.stringify(send_data),
                            headers: {
                                'Content-Type': 'application/json',
                            }
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.status==200) {
                                let refresh_location=`${window.location.origin}/admin/docs_core`;
                                location.href=refresh_location;
                            }
                        })
                        .catch((error) => {
                            console.error('Error:', error);
                        });
                    }
                }
            });
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });
}