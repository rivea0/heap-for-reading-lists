// Toggle dark mode

document.addEventListener('DOMContentLoaded', () => {
    let dark = document.querySelector('.dark-mode-btn');

    dark.addEventListener('click', () => {
        pages = document.querySelectorAll('body, th, td, .accordion-body, .accordion-button, .card-body, .link-dark, .btn-sm');
        pages.forEach(darkModeToggle);
    });
    
    function darkModeToggle(page) {
        page.classList.toggle('dark-mode');  
    };
});
