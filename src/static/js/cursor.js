// Get the custom cursor element
const cursor = document.querySelector('.custom-cursor');

// Track mouse movement
document.addEventListener('mousemove', (e) => {
    // Update cursor position
    cursor.style.left = `${e.clientX}px`;
    cursor.style.top = `${e.clientY}px`;
});

// Implement aggressive scroll
let isScrolling = false;

window.addEventListener('wheel', (e) => {
    if (!isScrolling) {
        isScrolling = true;
        if (e.deltaY > 0) {
            // Scroll down
            window.scrollTo({
                top: window.innerHeight,
                behavior: 'smooth'
            });
        } else {
            // Scroll up
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        }
        setTimeout(() => {
            isScrolling = false;
        }, 1000);
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const stages = document.querySelectorAll('.stage');
    
    stages.forEach(stage => {
        stage.addEventListener('click', function () {
            const targetId = stage.getAttribute('data-target');
            const targetSection = document.getElementById(targetId);
            
            if (targetSection) {
                targetSection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});

