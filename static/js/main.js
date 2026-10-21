// main.js — Spendly vanilla JS behaviors

document.addEventListener("DOMContentLoaded", function () {
    initCustomRangeToggle();
});

function initCustomRangeToggle() {
    var toggleBtn = document.querySelector("[data-custom-toggle]");
    var customForm = document.querySelector("[data-custom-form]");

    if (!toggleBtn || !customForm) {
        return;
    }

    function setExpanded(expanded) {
        customForm.classList.toggle("is-hidden", !expanded);
        toggleBtn.setAttribute("aria-expanded", expanded ? "true" : "false");
    }

    var isActive = customForm.getAttribute("data-active") === "true";
    setExpanded(isActive);

    toggleBtn.addEventListener("click", function () {
        var expanded = toggleBtn.getAttribute("aria-expanded") === "true";
        setExpanded(!expanded);
    });
}
