let map;
let marker;

document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the restaurant page
    const urlParams = new URLSearchParams(window.location.search);
    const type = urlParams.get('type');
    
    if (type === 'dineout') {
        const heading = document.querySelector('h2');
        const subtitle = document.querySelector('#formSubtitle');
        if (heading) heading.textContent = 'Dineout Registration';
        if (subtitle) subtitle.textContent = 'Partner with us for table reservations';
    }

    // Initialize map if we're on a page with a map
    const mapElement = document.getElementById('map');
    if (mapElement && typeof initMap === 'function') {
        initMap();
    }

    // Image Upload - Only add listener if element exists
    const imageUpload = document.getElementById('establishment-images');
    if (imageUpload) {
        imageUpload.addEventListener('change', handleImageUpload);
    }

    // Password visibility toggle
    document.querySelectorAll('.toggle-password').forEach(toggle => {
        toggle.addEventListener('click', function() {
            const input = this.previousElementSibling;
            if (input.type === 'password') {
                input.type = 'text';
                this.classList.remove('fa-eye-slash');
                this.classList.add('fa-eye');
            } else {
                input.type = 'password';
                this.classList.remove('fa-eye');
                this.classList.add('fa-eye-slash');
            }
        });
    });

    // Form validation
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            this.submit();
        });
    }

    // Venue image upload - Only add listener if element exists
    const venueImagesElement = document.getElementById('venue-images');
    const previewContainer = document.getElementById('image-previews');
    
    if (venueImagesElement && previewContainer) {
        venueImagesElement.addEventListener('change', function(e) {
            const files = Array.from(e.target.files);
            previewContainer.innerHTML = '';
            
            files.forEach(file => {
                if (file.size > 5 * 1024 * 1024) {
                    alert('File size should not exceed 5MB');
                    return;
                }
                
                const reader = new FileReader();
                reader.onload = function(e) {
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.className = 'preview-image';
                    previewContainer.appendChild(img);
                }
                reader.readAsDataURL(file);
            });
        });
    }
});

// Move initMap function outside DOMContentLoaded
function initMap() {
    if (!document.getElementById('map')) return;
    
    map = L.map('map').setView([20.5937, 78.9629], 5);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
    
    // Add geocoder control
    const geocoder = L.Control.geocoder({
        defaultMarkGeocode: false
    }).addTo(map);
    
    geocoder.on('markgeocode', function(e) {
        const latlng = e.geocode.center;
        setMarkerAndAddress(latlng);
        map.setView(latlng, 16);
    });
    
    // Handle map clicks
    map.on('click', function(e) {
        setMarkerAndAddress(e.latlng);
    });
}

function setMarkerAndAddress(latlng) {
    if (marker) {
        map.removeLayer(marker);
    }
    marker = L.marker(latlng).addTo(map);
    
    // Update hidden inputs
    document.getElementById('latitude').value = latlng.lat;
    document.getElementById('longitude').value = latlng.lng;
    
    // Reverse geocode to get address
    fetch(`https://nominatim.openstreetmap.org/reverse?lat=${latlng.lat}&lon=${latlng.lng}&format=json`)
        .then(response => response.json())
        .then(data => {
            const address = data.display_name;
            document.getElementById('selected-address').textContent = address;
            document.getElementById('formatted-address').value = address;
        });
}

function getCurrentLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            position => {
                const latlng = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                setMarkerAndAddress(latlng);
                map.setView(latlng, 16);
            },
            error => {
                console.error('Error getting location:', error);
                alert('Unable to get your location. Please try searching instead.');
            }
        );
    } else {
        alert('Geolocation is not supported by your browser');
    }
}

// Search location by name
async function searchLocation(query) {
    try {
        const response = await fetch(
            `https://nominatim.openstreetmap.org/search?format=json&q=${query}&countrycodes=in&limit=5`,
            {
                headers: {
                    'User-Agent': 'Mr.Foody & Ms.Foody Restaurant App'
                }
            }
        );
        const data = await response.json();
        
        // Show suggestions
        const suggestionsDiv = document.getElementById('search-suggestions');
        suggestionsDiv.innerHTML = '';
        
        if (data && data.length > 0) {
            suggestionsDiv.style.display = 'block';
            
            data.forEach(location => {
                const div = document.createElement('div');
                div.className = 'search-suggestion-item';
                div.textContent = location.display_name;
                
                div.addEventListener('click', () => {
                    const latlng = { 
                        lat: parseFloat(location.lat), 
                        lng: parseFloat(location.lon) 
                    };
                    
                    marker.setLatLng(latlng);
                    map.setView(latlng, 17);
                    updateLocationDetails(latlng);
                    document.getElementById('selected-address').textContent = location.display_name;
                    document.getElementById('location-input').value = location.display_name;
                    suggestionsDiv.style.display = 'none';
                });
                
                suggestionsDiv.appendChild(div);
            });
        } else {
            suggestionsDiv.style.display = 'none';
        }
    } catch (error) {
        console.error('Error searching location:', error);
    }
}

// Add click outside handler to close suggestions
document.addEventListener('click', function(e) {
    const suggestionsDiv = document.getElementById('search-suggestions');
    const searchInput = document.getElementById('location-input');
    
    if (!searchInput.contains(e.target) && !suggestionsDiv.contains(e.target)) {
        suggestionsDiv.style.display = 'none';
    }
});

// Get address from coordinates
async function searchAddress(lat, lng) {
    try {
        const response = await fetch(
            `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`,
            {
                headers: {
                    'User-Agent': 'Mr.Foody & Ms.Foody Restaurant App'
                }
            }
        );
        const data = await response.json();
        
        if (data && data.display_name) {
            document.getElementById('selected-address').textContent = data.display_name;
            document.getElementById('location-input').value = data.display_name;
        }
    } catch (error) {
        console.error('Error getting address:', error);
    }
}

function updateLocationDetails(latlng) {
    document.getElementById('latitude').value = latlng.lat;
    document.getElementById('longitude').value = latlng.lng;
}

// Helper function to debounce search input
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// Image Upload Handler
function handleImageUpload(e) {
    const files = Array.from(e.target.files);
    const previewsDiv = document.getElementById('image-previews');
    previewsDiv.innerHTML = '';

    if (files.length > 5) {
        alert('Please select a maximum of 5 images');
        this.value = '';
        return;
    }

    files.forEach(file => {
        if (file.size > 5 * 1024 * 1024) {
            alert('Each image must be less than 5MB');
            return;
        }

        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.createElement('img');
            preview.src = e.target.result;
            preview.className = 'image-preview';
            preview.style.display = 'block';
            previewsDiv.appendChild(preview);
        }
        reader.readAsDataURL(file);
    });
} 