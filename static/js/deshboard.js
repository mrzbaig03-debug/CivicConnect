/* ==========================================
   CivicConnect - Dashboard Script
   Shows a success popup after a complaint
   has just been submitted (?submitted=1 in URL).
========================================== */

document.addEventListener("DOMContentLoaded", function () {

    if (window.COMPLAINT_SUBMITTED) {
        Swal.fire({
            icon: "success",
            title: "Complaint Submitted!",
            text: "Your complaint has been registered successfully.",
            confirmButtonColor: "#0d6efd"
        });
    }

});