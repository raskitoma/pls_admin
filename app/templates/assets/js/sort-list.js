function slist (target) {
    // (A) SET CSS + GET ALL LIST ITEMS
    target.classList.add("slist");
    let items = target.getElementsByTagName("li"), current = null;
  
    // (B) MAKE ITEMS DRAGGABLE + SORTABLE
    for (let i of items) {
      // (B1) ATTACH DRAGGABLE
      i.draggable = true;
      
      // (B2) DRAG START - YELLOW HIGHLIGHT DROPZONES
      i.ondragstart = (ev) => {
        current = i;
        for (let it of items) {
          if (it != current) { it.classList.add("hint"); }
        }
      };
      
      // (B3) DRAG ENTER - RED HIGHLIGHT DROPZONE
      i.ondragenter = (ev) => {
        if (i != current) { i.classList.add("active"); }
      };
  
      // (B4) DRAG LEAVE - REMOVE RED HIGHLIGHT
      i.ondragleave = () => {
        i.classList.remove("active");
      };
  
      // (B5) DRAG END - REMOVE ALL HIGHLIGHTS
      i.ondragend = () => { for (let it of items) {
          it.classList.remove("hint");
          it.classList.remove("active");
      }};
   
      // (B6) DRAG OVER - PREVENT THE DEFAULT "DROP", SO WE CAN DO OUR OWN
      i.ondragover = (evt) => { evt.preventDefault(); };
   
      // (B7) ON DROP - DO SOMETHING
      i.ondrop = (evt) => {
        evt.preventDefault();
        if (i != current) {
          let currentpos = 0, droppedpos = 0;
          for (let it=0; it<items.length; it++) {
            if (current == items[it]) { currentpos = it; }
            if (i == items[it]) { droppedpos = it; }
          }
          if (currentpos < droppedpos) {
            i.parentNode.insertBefore(current, i.nextSibling);
          } else {
            i.parentNode.insertBefore(current, i);
          }
          let newpos = items[1].dataset;
          console.log(newpos);
        }
        let currentpos = 1;
        let group_positions = {};
        for (let it of items) {
            group_positions[currentpos] = {
                "position": currentpos,
                "group": it.dataset.group,
                "id": it.dataset.teamid,
                "team": it.dataset.team
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
          if(result.status == 200) {
            toaster(result.message, "success");
          } else {
              toaster(result.message, "danger");
          }
        })
        .catch(error => {
          toaster(error, "danger");
        });
        if(response.status == 200) {
          console.log(response);
        }
      };
    }
}
