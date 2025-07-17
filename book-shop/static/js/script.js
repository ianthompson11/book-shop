document.addEventListener('DOMContentLoaded', function () {
    // 🔐 Botones de registro/login
    const signUpBtn = document.querySelector('.sign-up-btn');
    const signInBtn = document.querySelector('.sign-in-btn');

    if (signUpBtn) {
        signUpBtn.addEventListener('click', function () {
            const container = document.querySelector('.container-form');
            container.classList.remove('sign-in', 'active');
            container.classList.add('sign-up', 'active');
            window.location.href = "/accounts/signup/";
        });
    }

    if (signInBtn) {
        signInBtn.addEventListener('click', function () {
            const container = document.querySelector('.container-form');
            container.classList.remove('sign-up', 'active');
            container.classList.add('sign-in', 'active');
            window.location.href = "/accounts/login/";
        });
    }

    // 📦 Panel de Usuario en Header
    const toggleButton = document.querySelector(".btn-panel-toggle");
    const panel = document.getElementById("userPanel");
    let open = false;

    if (toggleButton && panel) {
        toggleButton.addEventListener("click", () => {
            open = !open;
            panel.style.maxHeight = open ? panel.scrollHeight + "px" : "0px";
        });

        document.addEventListener("click", function (e) {
            if (!e.target.closest(".user-panel-dropdown")) {
                panel.style.maxHeight = "0px";
                open = false;
            }
        });
    }
});
