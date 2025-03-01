document.addEventListener('DOMContentLoaded', function() {
    initRestaurantDashboard();
});

function initRestaurantDashboard() {
    initStatusToggle();
    initQuickActions();
    loadMenuItems();
    initStats();
}

function initStatusToggle() {
    const statusToggle = document.querySelector('.restaurant-status input');
    const statusText = document.querySelector('.status-text');

    statusToggle.addEventListener('change', function() {
        if (this.checked) {
            statusText.textContent = 'Open for Orders';
            updateRestaurantStatus('open');
        } else {
            statusText.textContent = 'Closed';
            updateRestaurantStatus('closed');
        }
    });
}

function updateRestaurantStatus(status) {
    // API call to update restaurant status
    console.log(`Restaurant status updated to: ${status}`);
}

function initQuickActions() {
    const addMenuBtn = document.querySelector('.action-btn:nth-child(1)');
    const updatePhotosBtn = document.querySelector('.action-btn:nth-child(2)');
    const updateTimingsBtn = document.querySelector('.action-btn:nth-child(3)');

    addMenuBtn.addEventListener('click', () => {
        // Implement add menu item functionality
        console.log('Add menu item clicked');
    });

    updatePhotosBtn.addEventListener('click', () => {
        // Implement photo update functionality
        console.log('Update photos clicked');
    });

    updateTimingsBtn.addEventListener('click', () => {
        // Implement timing update functionality
        console.log('Update timings clicked');
    });
}

function loadMenuItems() {
    // Sample menu data
    const menuItems = [
        { name: 'Pizza', category: 'Main Course', price: '₹250', status: 'available' },
        { name: 'Burger', category: 'Fast Food', price: '₹150', status: 'available' },
        // Add more items as needed
    ];

    const menuContainer = document.querySelector('.menu-items');
    menuItems.forEach(item => {
        const itemElement = createMenuItem(item);
        menuContainer.appendChild(itemElement);
    });
}

function createMenuItem(item) {
    const div = document.createElement('div');
    div.className = 'menu-item';
    div.innerHTML = `
        <div class="item-details">
            <h3>${item.name}</h3>
            <p class="category">${item.category}</p>
            <p class="price">${item.price}</p>
        </div>
        <div class="item-actions">
            <button class="edit-btn"><i class="fas fa-edit"></i></button>
            <button class="toggle-btn ${item.status}">
                <i class="fas fa-power-off"></i>
            </button>
        </div>
    `;
    return div;
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
        orders: 45,
        revenue: '₹12,500',
        rating: 4.5
    };

    document.querySelector('.stat-value:nth-child(1)').textContent = stats.orders;
    document.querySelector('.stat-value:nth-child(2)').textContent = stats.revenue;
    document.querySelector('.stat-value:nth-child(3)').textContent = stats.rating;
} 