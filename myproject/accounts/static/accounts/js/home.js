const sections = document.querySelectorAll('.section');
let currentIndex = 0;
let isScrolling = false;

function showSlide(index) {
  if (index < 0 || index >= sections.length || isScrolling) return;

  isScrolling = true;

  sections.forEach(sec => sec.classList.remove('active'));
  const targetSection = sections[index];
  targetSection.classList.add('active');
  currentIndex = index;

  const id = targetSection.id;

  setTimeout(() => {
    location.href = `#${id}`;  // 👈 This ensures the hash is visible in Chrome too
    isScrolling = false;
  }, 10);
}


// Scroll using mouse wheel
window.addEventListener('wheel', (e) => {
  if (isScrolling) return;

  if (e.deltaY > 50) {
    showSlide(currentIndex + 1);
  } else if (e.deltaY < -50) {
    showSlide(currentIndex - 1);
  }
});

// Scroll using arrow keys
window.addEventListener('keydown', (e) => {
  if (isScrolling) return;

  if (e.key === 'ArrowDown') {
    showSlide(currentIndex + 1);
  } else if (e.key === 'ArrowUp') {
    showSlide(currentIndex - 1);
  }
});

// Inside your existing nav bar JS file (navBar.js)
document.querySelector('.logo a').addEventListener('click', function (e) {
    e.preventDefault(); // prevent default anchor jump
    goToSlide(0); 
  });

  
// ✨ Handle nav link clicks
document.querySelectorAll('.nav-links a').forEach(link => {
  link.addEventListener('click', (e) => {
    e.preventDefault(); // prevent default anchor jump

    const targetId = link.getAttribute('href');
    const targetSection = document.querySelector(targetId);

    if (targetSection) {
      const index = Array.from(sections).indexOf(targetSection);
      showSlide(index);
    }
  });
});
