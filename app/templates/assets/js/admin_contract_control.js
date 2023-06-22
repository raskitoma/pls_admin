$(document).ready(function() {
    let base_rent = document.getElementById('base_rent');
    let base_rent_2 = document.getElementById('base_rent_2');
    let base_rent_3 = document.getElementById('base_rent_3');
    let base_rent_4 = document.getElementById('base_rent_4');
    let base_rent_5 = document.getElementById('base_rent_5');
    let increase_year = document.getElementById('increase_year');
    let security_deposit = document.getElementById('security_deposit');
    let first_month_rent = document.getElementById('first_month_rent');
    let last_month_rent = document.getElementById('last_month_rent');
    let monthly_rent = document.getElementById('monthly_rent');

    if (base_rent) 
    base_rent.addEventListener('keyup', function(event) {
        let base_value = event.target.value;
        let increase_value = increase_year.value;
        if (base_value > 0 && !isNaN(base_value)) {
            let monthly_fee = parseFloat((base_value / 12).toFixed(2));
            security_deposit.value = monthly_fee;
            first_month_rent.value = monthly_fee;
            last_month_rent.value = monthly_fee;
            monthly_rent.value = monthly_fee;
            // updates base_rent_n
            base_rent_2.value = base_value * (1 + increase_value / 100);
            base_rent_3.value = base_rent_2.value * (1 + increase_value / 100);
            base_rent_4.value = base_rent_3.value * (1 + increase_value / 100);
            base_rent_5.value = base_rent_4.value * (1 + increase_value / 100);
        }
    });

    if (increase_year)
    increase_year.addEventListener('keyup', function(event) {
        let increase_value = event.target.value;
        let base_value = base_rent.value;
        if (base_value > 0 && !isNaN(base_value)) {
            // updates base_rent_n
            base_rent_2.value = base_value * (1 + increase_value / 100);
            base_rent_3.value = base_rent_2.value * (1 + increase_value / 100);
            base_rent_4.value = base_rent_3.value * (1 + increase_value / 100);
            base_rent_5.value = base_rent_4.value * (1 + increase_value / 100);
        }
    });
});

async function set_tenant_signee_info(tenant) {
    let signee_tenant_field = document.getElementById('signee_tenant');
    let signee_tenant_title_field = document.getElementById('signee_tenant_title');
    let selectedOption = tenant.options[tenant.selectedIndex];
    let selectedId = selectedOption.value;
    let signee_data = await get_data_admin(selectedId, 'get_tenant_info');
    if (signee_data) {
        if (signee_data.business_signee!='' || signee_data.business_signee!=null) {
            signee_tenant_field.value = signee_data.business_signee;
            signee_tenant_title_field.value = signee_data.business_signee_title;
        } else {
            signee_tenant_field.value = signee_data.full_name;
            signee_tenant_title_field.value = '';
        }
    }
}

async function set_landlord_signee_info(landlord) {
    let landlord_tenant_field = document.getElementById('signee_landlord');
    let landlord_tenant_title_field = document.getElementById('signee_landlord_title');
    let selectedOption = landlord.options[landlord.selectedIndex];
    let selectedId = selectedOption.value;
    // let signee_data = await get_data_admin(selectedId, 'get_landlord_info'); // this should be enabled when controller is ready
    let signee_data = await get_data_admin(1, 'get_landlord_info'); // fixed to one single landlord
    if (signee_data) {
        landlord_tenant_field.value = signee_data.signee;
        landlord_tenant_title_field.value = signee_data.signee_title;
    }
}

async function get_data_admin(what_id, from_where) {
    let data = {
        what_id: what_id,
    };

    // set the url as the current site url and adds '/' and the from_where as action
    let ajaxurl = window.location.origin + '/admin/contract/' + from_where;
    
    try {
        let response = await fetch(ajaxurl, {
            method: 'POST',
            body: JSON.stringify(data),
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if(!response.ok) {
            throw new Error('HTTP error, status = ' + response.status);
        }
        let responseData = await response.json();
        return responseData;
    } catch (error) {
        console.error(error);

    }
}
