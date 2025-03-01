// Google Maps location functionality
function getCurrentLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            position => {
                const latitude = position.coords.latitude;
                const longitude = position.coords.longitude;
                reverseGeocode(latitude, longitude);
            },
            error => {
                console.error("Error getting location:", error);
            }
        );
    }
}

function reverseGeocode(latitude, longitude) {
    const geocoder = new google.maps.Geocoder();
    const latlng = { lat: parseFloat(latitude), lng: parseFloat(longitude) };

    geocoder.geocode({ location: latlng }, (results, status) => {
        if (status === "OK") {
            if (results[0]) {
                document.getElementById("location-input").value = results[0].formatted_address;
            }
        }
    });
}

// Navbar scroll functionality
let lastScrollTop = 0;

// Remove or comment out this section
/*
window.addEventListener("scroll", function() {
    let currentScroll = window.pageYOffset || document.documentElement.scrollTop;
    
    if (currentScroll > lastScrollTop) {
        // Scrolling down
        document.querySelector(".navbar").style.transform = "translateY(100%)";
    } else {
        // Scrolling up
        document.querySelector(".navbar").style.transform = "translateY(0)";
    }
    lastScrollTop = currentScroll <= 0 ? 0 : currentScroll;
});
*/

// Profile Menu Toggle
function toggleProfileMenu() {
    const profileDropdown = document.querySelector('.profile-dropdown');
    profileDropdown.classList.toggle('active');

    // Close menu when clicking outside
    document.addEventListener('click', function(event) {
        const isClickInside = event.target.closest('.profile-icon');
        if (!isClickInside && profileDropdown.classList.contains('active')) {
            profileDropdown.classList.remove('active');
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Profile dropdown functionality
    const profileIcon = document.querySelector('.profile-icon');
    const profileDropdown = document.querySelector('.profile-dropdown');

    if (profileIcon) {
        profileIcon.addEventListener('click', function(e) {
            e.stopPropagation();
            profileDropdown.classList.toggle('active');
        });
    }

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (profileDropdown && profileDropdown.classList.contains('active')) {
            if (!profileDropdown.contains(e.target)) {
                profileDropdown.classList.remove('active');
            }
        }
    });

    // Load user data if exists
    const currentUser = JSON.parse(localStorage.getItem('currentUser')) || {
        name: 'Guest User'
    };
    
    // Update profile name
    const profileName = document.querySelector('.profile-header span');
    if (profileName) {
        profileName.textContent = `Hello, ${currentUser.name}`;
    }
});