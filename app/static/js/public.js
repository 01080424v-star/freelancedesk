/* Паралакс хіро */
function initParallax() {
    const bg = document.getElementById('parallax-bg');
    if (!bg) return;
    let ticking = false;
    window.addEventListener('scroll', () => {
        if (!ticking) {
            requestAnimationFrame(() => {
                bg.style.transform = `translateY(${window.pageYOffset * 0.45}px)`;
                ticking = false;
            });
            ticking = true;
        }
    }, { passive: true });
}

/* Анімація появи при скролі */
function initReveal() {
    const els = document.querySelectorAll('.reveal');
    if (!els.length) return;
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const delay = entry.target.style.getPropertyValue('--delay') || '0s';
                entry.target.style.animationDelay = delay;
                entry.target.classList.add('revealed');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.12 });
    els.forEach(el => observer.observe(el));
}

/* Мобільне меню */
function initMobileNav() {
    const burger = document.querySelector('.nav-burger');
    const links  = document.querySelector('.nav-links');
    if (!burger || !links) return;
    burger.addEventListener('click', () => links.classList.toggle('open'));
    document.addEventListener('click', e => {
        if (!burger.contains(e.target) && !links.contains(e.target)) {
            links.classList.remove('open');
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    initParallax();
    initReveal();
    initMobileNav();
});
