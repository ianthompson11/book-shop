document.addEventListener('DOMContentLoaded', function() {
    const signUpBtn = document.querySelector('.sign-up-btn');
    const signInBtn = document.querySelector('.sign-in-btn');

    if (signUpBtn) {
        signUpBtn.addEventListener('click', function() {
            const container = document.querySelector('.container-form');
            container.classList.remove('sign-in', 'active');
            container.classList.add('sign-up', 'active');
            // Forzar redirección inmediata
            window.location.href = "{% url 'account_signup' %}";
        });
    }

    if (signInBtn) {
        signInBtn.addEventListener('click', function() {
            const container = document.querySelector('.container-form');
            container.classList.remove('sign-up', 'active');
            container.classList.add('sign-in', 'active');
            // Forzar redirección inmediata
            window.location.href = "{% url 'account_login' %}";
        });
    }
});