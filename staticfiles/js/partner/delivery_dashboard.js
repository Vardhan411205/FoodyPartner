document.addEventListener('DOMContentLoaded', function() {
    initDeliveryDashboard();
});

function initDeliveryDashboard() {
    initMap();
    initStatusToggle();
    loadActiveOrders();
    initStats();
}

function initMap() {
    // Initialize the delivery map using Leaflet
    const map = L.map('delivery-map').setView([20.5937, 78.9629], 13);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Get current location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(position => {
            const { latitude, longitude } = position.coords;
            map.setView([latitude, longitude], 15);
            
            // Add delivery partner marker
            L.marker([latitude, longitude], {
                icon: L.divIcon({
                    className: 'delivery-marker',
                    html: '<i class="fas fa-motorcycle"></i>'
                })
            }).addTo(map);
        });
    }
}

function initStatusToggle() {
    const statusIndicator = document.querySelector('.status-indicator');
    const statusText = document.querySelector('.partner-status span:last-child');

    statusIndicator.addEventListener('click', function() {
        this.classList.toggle('online');
        if (this.classList.contains('online')) {
            statusText.textContent = 'Available for Delivery';
            updateDeliveryStatus('available');
        } else {
            statusText.textContent = 'Offline';
            updateDeliveryStatus('offline');
        }
    });
}

function updateDeliveryStatus(status) {
    // API call to update delivery partner status
    console.log(`Delivery status updated to: ${status}`);
}

function loadActiveOrders() {
    // Sample orders data
    const activeOrders = [
        {
            id: 'ORD123',
            restaurant: 'Pizza Palace',
            customer: 'John Smith',
            items: '2 items',
            amount: '₹450',
            status: 'Pickup'
        }
    ];

    const orderCardsContainer = document.querySelector('.order-cards');
    activeOrders.forEach(order => {
        orderCardsContainer.appendChild(createOrderCard(order));
    });
}

function createOrderCard(order) {
    const card = document.createElement('div');
    card.className = 'order-card';
    card.innerHTML = `
        <div class="order-header">
            <span class="order-id">#${order.id}</span>
            <span class="order-status">${order.status}</span>
        </div>
        <div class="order-details">
            <div class="restaurant-info">
                <i class="fas fa-store"></i>
                <span>${order.restaurant}</span>
            </div>
            <div class="customer-info">
                <i class="fas fa-user"></i>
                <span>${order.customer}</span>
            </div>
            <div class="order-info">
                <span>${order.items}</span>
                <span class="amount">${order.amount}</span>
            </div>
        </div>
        <div class="order-actions">
            <button class="accept-btn">Accept</button>
            <button class="navigate-btn">Navigate</button>
        </div>
    `;
    return card;
}

function initStats() {
    // Real-time stats update
    setInterval(() => {
        updateStats();
    }, 30000); // Update every 30 seconds
}

function updateStats() {
    // API call to get updated stats
    const stats = {
        deliveries: 12,
        earnings: '₹850',
        rating: 4.8
    };

    document.querySelector('.stat-value:nth-child(1)').textContent = stats.deliveries;
    document.querySelector('.stat-value:nth-child(2)').textContent = stats.earnings;
    document.querySelector('.stat-value:nth-child(3)').textContent = stats.rating;
} 