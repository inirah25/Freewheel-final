const profileImg = document.getElementById('profile-img');
const dropdown = document.getElementById('dropdown');

profileImg.addEventListener('mouseenter', () => {
  dropdown.classList.add('show');
});

profileImg.addEventListener('mouseleave', () => {
  setTimeout(() => {
    if (!dropdown.matches(':hover')) {
      dropdown.classList.remove('show');
    }
  }, 200);
});

dropdown.addEventListener('mouseleave', () => {
  dropdown.classList.remove('show');
});

dropdown.addEventListener('mouseenter', () => {
  dropdown.classList.add('show');
});

const input = document.querySelector('.search-box input');
const suggestionList = document.getElementById('suggestion-list');

const suggestions = ['Kitchen Cleaning', 'Floor Cleaning', 'AC Service', 'Bathroom Deep Clean'];

input.addEventListener('input', () => {
  const value = input.value.toLowerCase();
  suggestionList.innerHTML = '';

  if (value) {
    const filtered = suggestions.filter(item => item.toLowerCase().includes(value));
    filtered.forEach(item => {
      const li = document.createElement('li');
      li.textContent = item;
      li.addEventListener('click', () => {
        input.value = item;
        suggestionList.classList.remove('show');
      });
      suggestionList.appendChild(li);
    });
    if (filtered.length > 0) {
      suggestionList.classList.add('show');
    } else {
      suggestionList.classList.remove('show');
    }
  } else {
    suggestionList.classList.remove('show');
  }
});

// Hide suggestions when clicking outside
document.addEventListener('click', (e) => {
  if (!document.querySelector('.search-box').contains(e.target)) {
    suggestionList.classList.remove('show');
  }
});
