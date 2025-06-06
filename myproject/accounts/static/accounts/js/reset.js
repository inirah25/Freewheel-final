const container = document.querySelector('.container');

window.addEventListener('load', () => {
  setTimeout(() => {
    container.classList.remove('active');
  }, 100); // Adjust delay if needed for visual smoothness
});

document.getElementById('confirm-btn').addEventListener('click', () => {
    // Prevent default form submission and page refresh

  const password = document.getElementById('password').value;
  const confirmPassword = document.getElementById('password1').value;

  // Validate passwords match
  if (password !== confirmPassword) {
    alert("Passwords do not match!");
    return;
  }

  // Hide the reset password form
  document.getElementById('reset-password-div').style.display = 'none';

  // Show the success message
  document.getElementById('success-message').style.display = 'block';

  // Wait 15 seconds then redirect to login page
  // setTimeout(() => {
  //   window.location.href = '/login/';  // Change '/login' to your actual login page URL
  // }, 1000); // 15000 milliseconds = 15 seconds
});
  

function setupEyeToggle(eyeId, inputId) {
    const eye = document.getElementById(eyeId);
    const input = document.getElementById(inputId);
  
    eye.addEventListener('mouseover', () => {
      input.type = 'text';
      eye.classList.replace('fa-eye', 'fa-eye-low-vision');
    });
  
    eye.addEventListener('mouseout', () => {
      input.type = 'password';
      eye.classList.replace('fa-eye-low-vision', 'fa-eye');
    });
  }
  
  setupEyeToggle('eye-icon', 'password');
  setupEyeToggle('eye-icon1', 'password1');
  

  document.addEventListener('DOMContentLoaded', function () {
    const passwordInput = document.getElementById("password");
    const strengthText = document.getElementById("strength-text");
  
    passwordInput.addEventListener("input", function () {
      const password = passwordInput.value;
      let strength = "";
  
      if (password.length < 8) {
        strength = "Too short";
        strengthText.style.color = "red";
      } else if (!/[0-9]/.test(password)) {
        strength = "Add at least one number";
        strengthText.style.color = "orange";
      } else if (!/[!@#$%^&*]/.test(password)) {
        strength = "Add a special character";
        strengthText.style.color = "orange";
      } else {
        strength = "Strong password";
        strengthText.style.color = "green";
      }
  
      strengthText.textContent = strength;
    });
  });
  