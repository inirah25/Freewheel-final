// ✅ Generate sample employee data with name, title (type), and shift
const users = JSON.parse(document.getElementById("user-data").textContent);
const shifts = ['S1', 'S2', 'S3'];
const types = ['E1', 'E2', 'E3', 'E4', 'Manager'];
 
const employees = users.map((user, i) => ({
  name: user.name,
  role: user.role,
  image: `https://i.pravatar.cc/150?img=${(i % 70) + 1}`,
}));

let filteredEmployees = [...employees]; // dynamic filtered list
 
const cardsPerPage = 10;
let currentPage = 0;
 
const cardContainer = document.getElementById("cardContainer");
const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");
const slideNav = document.getElementById("slideNav");
 
function getTotalPages() {
  return Math.ceil(filteredEmployees.length / cardsPerPage);
}
 
function renderCards(direction = 'right') {
  cardContainer.classList.remove('slide-left', 'slide-right');
  void cardContainer.offsetWidth;
 
  const totalPages = getTotalPages();
  const start = currentPage * cardsPerPage;
  const end = start + cardsPerPage;                                        
  const currentEmployees = filteredEmployees.slice(start, end);
 
  cardContainer.innerHTML = "";

  if (currentEmployees.length === 0) {
    // Disable animation and buttons
    cardContainer.classList.remove('slide-left', 'slide-right');
    prevBtn.disabled = true;
    nextBtn.disabled = true;
    slideNav.innerHTML = "";
  
    // Create container box
    const noDataWrapper = document.createElement("div");
    noDataWrapper.classList.add("no-results-wrapper");
  
    const noDataMessage = document.createElement("div");
    noDataMessage.classList.add("no-results");
    noDataMessage.innerText = "No users found !";
  
    noDataWrapper.appendChild(noDataMessage);
    cardContainer.appendChild(noDataWrapper);
    return;
  }
  

 else {
  currentEmployees.forEach(emp => {
    const card = document.createElement("div");
    card.classList.add("card");
    card.innerHTML = `
  <img src="${emp.image}" alt="${emp.name}" />
  <div class='card-bar'>
    <h2>${emp.name}</h2>
    <p>Type: ${emp.role} | Shift: ${emp.shift}</p>
    <div class="hover-details">                    
      <p><strong>Email:</strong> ${emp.email}</p>
      <p><strong>Status:</strong> ${emp.status}</p>
      <p><strong>Manager:</strong> ${emp.manager}</p>
      <p><a href="${emp.teamsLink}" target="_blank">Join Teams</a></p>
    </div>
  </div>
`;

    cardContainer.appendChild(card);
  });
}

 
  cardContainer.classList.add(direction === 'left' ? 'slide-left' : 'slide-right');
 
  prevBtn.disabled = currentPage === 0;
  nextBtn.disabled = (currentPage + 1) * cardsPerPage >= filteredEmployees.length;
 
  updateDots();
}
 
function createDots() {
  const totalPages = getTotalPages();
  slideNav.innerHTML = "";
  for (let i = 0; i < totalPages; i++) {
    const dot = document.createElement("div");
    dot.classList.add("dot");
    if (i === currentPage) dot.classList.add("active");
    dot.addEventListener("click", () => {
      if (i !== currentPage) {
        const direction = i > currentPage ? 'right' : 'left';
        currentPage = i;
        renderCards(direction);
      }
    });
    slideNav.appendChild(dot);
  }
}
 
function updateDots() {
  const dots = slideNav.querySelectorAll('.dot');
  dots.forEach((dot, idx) => {
    dot.classList.toggle("active", idx === currentPage);
  });
}
 
// ✅ Mouse scroll and keyboard navigation (from home.js)
let slideScrollLock = false;
 
function handlePageScroll(e) {
  if (slideScrollLock) return;
 
  const delta = e.deltaY;
  if (Math.abs(delta) < 50) return;
 
  const totalPages = getTotalPages();
 
  if (delta > 0 && currentPage < totalPages - 1) {
    currentPage++;
    renderCards('right');
  } else if (delta < 0 && currentPage > 0) {
    currentPage--;
    renderCards('left');
  }
 
  slideScrollLock = true;
  setTimeout(() => {
    slideScrollLock = false;
  }, 800);
}
 
window.addEventListener('wheel', handlePageScroll);
 
window.addEventListener('keydown', (e) => {
  if (slideScrollLock) return;
 
  const totalPages = getTotalPages();
 
  if (e.key === 'ArrowDown' && currentPage < totalPages - 1) {
    currentPage++;
    renderCards('right');
  } else if (e.key === 'ArrowUp' && currentPage > 0) {
    currentPage--;
    renderCards('left');
  }
 
  slideScrollLock = true;
  setTimeout(() => {
    slideScrollLock = false;
  }, 800);
});
 
// ✅ Button clicks
prevBtn.addEventListener("click", () => {
  if (currentPage > 0) {
    currentPage--;
    renderCards('left');
  }
});
 
nextBtn.addEventListener("click", () => {
  const totalPages = getTotalPages();
  if (currentPage < totalPages - 1) {
    currentPage++;
    renderCards('right');
  }
});
 
// ✅ Filter logic
function getCheckedValues(name) {
  return Array.from(document.querySelectorAll(`input[name="${name}"]:checked`)).map(cb => cb.value);
}
 
function applyFilters() {
  const employeeSelected = document.querySelector('.dropdown-e .selected-e').innerText.trim().toLowerCase();
  const managerSelected = document.querySelector('.dropdown-m .selected-m').innerText.trim().toLowerCase();

  let filteredName = "";
  let filterBy = "";

  if (employeeSelected !== "all employees") {
    filteredName = employeeSelected;
    filterBy = "employee";
  } else if (managerSelected !== "all managers") {
    filteredName = managerSelected;
    filterBy = "manager";
  }

  const selectedShifts = getCheckedValues("shift");
  const selectedTypes = getCheckedValues("type");

  filteredEmployees = employees.filter(emp => {
    const matchName =
  filterBy === "employee" ? emp.name.toLowerCase().includes(filteredName) :
  filterBy === "manager" ? (emp.manager || "").toLowerCase().includes(filteredName) :
  true;

    const matchShift = selectedShifts.length === 0 || selectedShifts.includes(emp.shift);
    const matchType = selectedTypes.length === 0 || selectedTypes.includes(emp.role);
    return matchName && matchShift && matchType;
  });

  currentPage = 0;
  createDots();
  renderCards();
 
}
 
 
// ✅ Checkbox active class toggling
document.querySelectorAll('.toggle-option input[type="checkbox"]').forEach(input => {
  input.addEventListener('change', () => {
    input.parentElement.classList.toggle('active', input.checked);
  
    // Reset employee and manager filters
    const empSelected = document.querySelector('.dropdown-e .selected-e');
    const mgrSelected = document.querySelector('.dropdown-m .selected-m');
  
    if (empSelected && empSelected.innerText !== "All Employees") {
      empSelected.innerText = "All Employees";
      document.querySelectorAll('.dropdown-e .menu-e li').forEach(li => li.classList.remove('active'));
      document.querySelector('.dropdown-e .menu-e li:first-child').classList.add('active');
    }
  
    if (mgrSelected && mgrSelected.innerText !== "All Managers") {
      mgrSelected.innerText = "All Managers";
      document.querySelectorAll('.dropdown-m .menu-m li').forEach(li => li.classList.remove('active'));
      document.querySelector('.dropdown-m .menu-m li:first-child').classList.add('active');
    }
  
    applyFilters();
  });
  
});
 
// ✅ Form change triggers filtering
document.getElementById("employeeFilterForm").addEventListener("input", () => {
  // Reset employee and manager filters
  const empSelected = document.querySelector('.dropdown-e .selected-e');
  const mgrSelected = document.querySelector('.dropdown-m .selected-m');

  if (empSelected && empSelected.innerText !== "All Employees") {
    empSelected.innerText = "All Employees";
    document.querySelectorAll('.dropdown-e .menu-e li').forEach(li => li.classList.remove('active'));
    document.querySelector('.dropdown-e .menu-e li:first-child').classList.add('active');
  }

  if (mgrSelected && mgrSelected.innerText !== "All Managers") {
    mgrSelected.innerText = "All Managers";
    document.querySelectorAll('.dropdown-m .menu-m li').forEach(li => li.classList.remove('active'));
    document.querySelector('.dropdown-m .menu-m li:first-child').classList.add('active');
  }

  applyFilters();
});

 
// ✅ Initial render
document.addEventListener("DOMContentLoaded", () => {
  createDots();
  renderCards();
});
 
function initDropdown(dropdownClass, selectClass, menuClass, selectedClass, openClass) {
  const dropdowns = document.querySelectorAll(`.${dropdownClass}`);
 
  dropdowns.forEach(dropdown => {
    const select = dropdown.querySelector(`.${selectClass}`);
    const menu = dropdown.querySelector(`.${menuClass}`);
    const options = dropdown.querySelectorAll(`.${menuClass} li`);
    const selected = dropdown.querySelector(`.${selectedClass}`);
 
    let isOverDropdown = false;
 
    const showMenu = () => menu.classList.add(openClass);
    const hideMenu = () => {
      if (!isOverDropdown) {
        menu.classList.remove(openClass);
      }
    };
 
    // Show menu when mouse enters dropdown (select or menu)
    dropdown.addEventListener('mouseenter', () => {
      isOverDropdown = true;
      showMenu();
    });
 
    // Hide menu when mouse leaves dropdown area
    dropdown.addEventListener('mouseleave', () => {
      isOverDropdown = false;
      hideMenu();
    });
 
    // On clicking an option
    options.forEach(option => {
      option.addEventListener('click', () => {
        selected.innerText = option.innerText;
        menu.classList.remove(openClass);
 
        options.forEach(opt => opt.classList.remove('active'));
        option.classList.add('active');
 
        applyFilters();
      });
    });
  });
}
 
// Call the function for your dropdown
initDropdown('dropdown-e', 'select-e', 'menu-e', 'selected-e', 'menu-open-e');
initDropdown('dropdown-m', 'select-m', 'menu-m', 'selected-m', 'menu-open-m');

// Clear manager dropdown when employee is selected
document.querySelectorAll('.dropdown-e .menu-e li').forEach(item => {
  item.addEventListener('click', () => {
    const managerSelected = document.querySelector('.dropdown-m .selected-m');
    if (managerSelected && managerSelected.innerText !== "All Managers") {
      managerSelected.innerText = "All Managers";
      document.querySelectorAll('.dropdown-m .menu-m li').forEach(li => li.classList.remove('active'));
      document.querySelector('.dropdown-m .menu-m li:first-child').classList.add('active');
    }
  });
});

// Clear employee dropdown when manager is selected
document.querySelectorAll('.dropdown-m .menu-m li').forEach(item => {
  item.addEventListener('click', () => {
    const employeeSelected = document.querySelector('.dropdown-e .selected-e');
    if (employeeSelected && employeeSelected.innerText !== "All Employees") {
      employeeSelected.innerText = "All Employees";
      document.querySelectorAll('.dropdown-e .menu-e li').forEach(li => li.classList.remove('active'));
      document.querySelector('.dropdown-e .menu-e li:first-child').classList.add('active');
    }
  });
});

 