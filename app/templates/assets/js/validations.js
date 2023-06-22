function final_rec(target) {
    let items = target.parentNode.parentNode.parentNode.getElementsByTagName("select"), current = null;
    console.log(current);
    // check duplicates
    let start_values = [];
    let validate_errors = false;
    for (let i of items) {
        // get the selected value
        let selected_value = i.options[i.selectedIndex].value;
        // check if the value is already in the list
        if (start_values.includes(selected_value)) {
            // if it is, show an error
            toaster("No se pueden repetir equipos", "danger");
            // set red background to select
            i.classList.add("is-invalid");
            validate_errors = true;
        } else if (isNaN(selected_value)) {
            i.classList.add("is-invalid");
            validate_errors = true;
        } else {
            i.classList.remove("is-invalid");
            start_values.push(selected_value);
        }
    }
    if (!validate_errors) {
        // if there are no errors, continue
        for (let i of items) {
            // get the selected value
            let selected_value = i.options[i.selectedIndex].value;
            let position = i.getAttribute("data-position");
            let stage = i.getAttribute("data-stage");
            let json_body = {
                "position": position,
                "stage": stage,
                "team": selected_value
            }
            // get body object
            let selected_quinela = document.getElementsByTagName("body")[0].dataset.quinela;
            // send data to server using post
           let response = fetch("/finalupdate/" + selected_quinela , {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(json_body)
            })
            .then(response => response.json())
            .then(result => {
                if(result.status==200) {
                    console.log(result.message);
                    toaster(result.message, "success");
                } else {
                    toaster(result.message, "danger");
                }
            })
            .catch(error => {
                console.log(response, error);
                toaster(error, "danger");
            });
        }
    }

}

function group_rec(target) {
    let current_group = target.getAttribute("data-group");
    let targetSelector = "[data-select-" + current_group + "]";
    let items = document.querySelectorAll(targetSelector), current = null;
    console.log(current);
    // check duplicates
    let start_values = [];
    let validate_errors = false;
    for (let i of items) {
        // get the selected value
        let selected_value = i.options[i.selectedIndex].value;
        // check if the value is already in the list
        if (start_values.includes(selected_value)) {
            // if it is, show an error
            toaster("No se pueden repetir equipos", "danger");
            // set red background to select
            i.classList.add("is-invalid");
            validate_errors = true;
        } else if (isNaN(selected_value)) {
            i.classList.add("is-invalid");
            validate_errors = true;
        } else {
            i.classList.remove("is-invalid");
            start_values.push(selected_value);
        }
    }

    if (!validate_errors) {
        // if there are no errors, continue
        let currentpos = 1;
        let group_positions = {};
        for (let i of items) {
            // get the selected value
            let selected_value = i.options[i.selectedIndex].value;
            let selected_label = i.options[i.selectedIndex].text;
            let position = i.getAttribute("data-position");
            let group = i.getAttribute("data-group");
            group_positions[currentpos] = {
                "position": position,
                "group": group,
                "id": selected_value,
                "team": selected_label
            }
            currentpos++;
        }
       // get body object
       let selected_quinela = document.getElementsByTagName("body")[0].dataset.quinela;
       // send data to server using post
       let response = fetch("/groupupdate/" + selected_quinela , {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                "quinela": selected_quinela,
                "group_positions": group_positions
            })
        })
        .then(response => response.json())
        .then(result => {
            if(result.status==200) {
                console.log(result.message);
                toaster(result.message, "success");
            } else {
                toaster(result.message, "danger");
            }
        })
        .catch(error => {
            console.log(response, error);
            toaster(error, "danger");
        });
    }
}
