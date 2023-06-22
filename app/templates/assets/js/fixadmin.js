let subtreeicons = ['fas fa-database', 'fas fa-globe-americas', 'fas fa-user-secret', 'fas fa-hammer']
let separator = 'fas fa-chevron-right'
$(document).ready(function () {
    let treeViewElements = document.querySelectorAll('i.dropdown-submenu');
    treeViewElements.forEach((element, index) => {
        element.className = `${subtreeicons[index]}  dropdown-submenu dropright nav-icon`;
        element.parentElement.innerHTML = `<i class="${separator}"></i> ${element.parentElement.innerHTML}`;
    });
            
    let otherMenues = document.querySelectorAll('a.nav-link');
    otherMenues.forEach((element) => {
        
        if(element.href.includes('#')) {
            return;
        } 
        if (element.href.includes(`<i class="${separator}"></i>`)) {
            return;
        }
        element.innerHTML = `<i class="${separator}"></i> ${element.innerHTML}`;
    })
});

