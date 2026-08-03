/* ==========================================
   CivicConnect - Complaint Form Script
   Handles:
   1. Area → Ward auto-selection
   2. Image preview before upload
   3. SweetAlert2 error popup
========================================== */

document.addEventListener("DOMContentLoaded", function () {

    // ---- Area → Ward Auto-select ----

    const areaInput = document.getElementById("areaInput");
    const wardSelect = document.getElementById("wardSelect");

    function autoSelectWard() {

        const typedArea = areaInput.value.trim().toLowerCase();

        const match = window.AREA_WARD_MAP.find(
            item => item.area.toLowerCase() === typedArea
        );

        if (match) {
            wardSelect.value = match.ward_number;
        }
    }

    if (areaInput && wardSelect) {
        areaInput.addEventListener("input", autoSelectWard);
        areaInput.addEventListener("change", autoSelectWard);
    }

    // ---- Image Preview ----

    const imageInput = document.getElementById("imageInput");
    const imagePreviewBox = document.getElementById("imagePreviewBox");
    const imagePreview = document.getElementById("imagePreview");

    if (imageInput) {

        imageInput.addEventListener("change", function () {

            const file = imageInput.files[0];

            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    imagePreview.src = e.target.result;
                    imagePreviewBox.style.display = "block";
                };
                reader.readAsDataURL(file);
            } else {
                imagePreviewBox.style.display = "none";
            }

        });
    }

    // ---- SweetAlert2 Error Popup ----

    if (window.COMPLAINT_ERROR) {
        Swal.fire({
            icon: "error",
            title: "Oops!",
            text: window.COMPLAINT_ERROR,
            confirmButtonColor: "#0d6efd"
        });
    }

});