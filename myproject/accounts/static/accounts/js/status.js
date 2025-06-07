const statusSelect = document.getElementById('status');
const shiftContainer = document.getElementById('shiftContainer');
const statusDisplay = document.getElementById('statusDisplay');


statusSelect.addEventListener('change', () => {
  const value = statusSelect.value;

  // Show shift selection only if "Logged In"
  if (value === 'logged-in') {
    shiftContainer.classList.add('show');
  } else {
    shiftContainer.classList.remove('show');
  }

  // Update status display
  let statusText = '';
  let statusClass = '';

  switch (value) {
    case 'logged-in':
      statusText = 'You are Logged In';
      statusClass = 'logged-in';
      break;
    case 'brb':
      statusText = 'Be Right Back';
      statusClass = 'brb';
      break;
    case 'logged-off':
      statusText = 'You are Logged Off';
      statusClass = 'logged-off';
      break;
    case 'back':
      statusText = 'You are Back';
      statusClass = 'back';
      break;
    default:
      statusText = 'Please select a status';
  }

  statusDisplay.textContent = statusText;
  statusDisplay.className = `status-indicator ${statusClass}`;
});

const container = document.querySelector('.container');
const modeBtn = document.getElementById('confirm-workmode');
const modeSelect = document.getElementById('mode');

// Remove 'active1' class when the page loads
window.addEventListener('load', () => {
setTimeout(() => {
    container.classList.remove('active1');
    container.classList.add('active0');
    }, 100);
});


modeBtn.addEventListener('click', (e) => {
const selectedValue = modeSelect.value;

if (selectedValue && selectedValue !== "none" && selectedValue !== "") {
container.classList.remove('active0');
container.classList.add('active');
} else {
e.preventDefault(); // prevent form submission
alert("Please select a valid work mode.");
}
});