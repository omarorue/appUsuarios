document.addEventListener("DOMContentLoaded", function() {
    setTimeout(function() {
        var myModal = new bootstrap.Modal(document.getElementById('modalIngreso'));
        myModal.show();
    }, 2000); // 2000 milisegundos = 2 segundos
});