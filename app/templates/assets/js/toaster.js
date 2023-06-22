function toaster(message, type) {
    let toastElList = [].slice.call(document.querySelectorAll('.toast'))
    let toastList = toastElList.map(function(toastEl) {
      return new bootstrap.Toast(toastEl)
    })
    toastList.forEach(toast => {
        let toast_class = document.querySelector('.toast').classList;
        toast_class.remove("bg-success");
        toast_class.remove("bg-danger");
        toast_class.remove("bg-warning");
        toast_class.remove("bg-primary");
        toast_class.remove("bg-info");
        toast_class.add("bg-" + type);
        document.querySelector(".toast-body").innerHTML = message;
        toast.show();
    })
  }
  