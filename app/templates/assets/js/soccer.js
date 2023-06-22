function update_match(self) {
    let match_id = self.dataset.match_id;
    let prediction = self.dataset.prediction;
    let team = self.dataset.team;
    let stage = self.dataset.stage;
    // get body object
    let selected_quinela = document.getElementsByTagName("body")[0].dataset.quinela;
    // send data to server using post
    let response = fetch("/matchupdate/" + selected_quinela , {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            "match_id": match_id,
            "prediction": prediction,
            "team": team,
            "stage": stage
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