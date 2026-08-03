/* ==========================================
   CivicConnect - Representative Login Script
   Auto-fills email field when a representative
   is selected from the dropdown.
========================================== */

document.addEventListener("DOMContentLoaded", function () {

    const repSelect = document.getElementById("repSelect");
    const emailInput = document.getElementById("emailInput");

    if (repSelect && emailInput) {
        repSelect.addEventListener("change", function () {
            emailInput.value = repSelect.value;
        });
    }

});