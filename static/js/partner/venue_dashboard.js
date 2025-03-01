document.addEventListener('DOMContentLoaded', function() {
    initVenueDashboard();
});

function initVenueDashboard() {
    initStatusToggle();
    initQuickActions();
    loadUpcomingEvents();
    initCalendar();
    initStats();
}

function initStatusToggle() {
    const statusToggle = document.querySelector('.venue-status input');
    const statusText = document.querySelector('.status-text');

    statusToggle.addEventListener('change', function() {
        if (this.checked) {
            statusText.textContent = 'Available for Booking';
            updateVenueStatus('available');
        } else {
            statusText.textContent = 'Unavailable';
            updateVenueStatus('unavailable');
        }
    });
}

function updateVenueStatus(status) {
    // API call to update venue status
    console.log(`Venue status updated to: ${status}`);
}

function initQuickActions() {
    const addPackageBtn = document.querySelector('.action-btn:nth-child(1)');
    const updateGalleryBtn = document.querySelector('.action-btn:nth-child(2)');
    const manageCalendarBtn = document.querySelector('.action-btn:nth-child(3)');

    addPackageBtn.addEventListener('click', () => {
        // Implement add package functionality
        console.log('Add event package clicked');
    });

    updateGalleryBtn.addEventListener('click', () => {
        // Implement gallery update functionality
        console.log('Update gallery clicked');
    });

    manageCalendarBtn.addEventListener('click', () => {
        // Implement calendar management functionality
        console.log('Manage calendar clicked');
    });
}

function loadUpcomingEvents() {
    // Sample events data
    const upcomingEvents = [
        {
            id: 'EVT123',
            date: '2024-03-15',
            type: 'Wedding',
            client: 'Smith Family',
            guests: 200,
            amount: '₹1,50,000'
        }
    ];

    const eventsContainer = document.querySelector('.upcoming-events');
    upcomingEvents.forEach(event => {
        eventsContainer.appendChild(createEventCard(event));
    });
}

function createEventCard(event) {
    const card = document.createElement('div');
    card.className = 'event-card';
    card.innerHTML = `
        <div class="event-header">
            <span class="event-date">${formatDate(event.date)}</span>
            <span class="event-type">${event.type}</span>
        </div>
        <div class="event-details">
            <div class="client-info">
                <i class="fas fa-user"></i>
                <span>${event.client}</span>
            </div>
            <div class="event-info">
                <div>
                    <i class="fas fa-users"></i>
                    <span>${event.guests} Guests</span>
                </div>
                <div>
                    <i class="fas fa-rupee-sign"></i>
                    <span>${event.amount}</span>
                </div>
            </div>
        </div>
        <div class="event-actions">
            <button class="view-btn">View Details</button>
            <button class="edit-btn">Edit Event</button>
        </div>
    `;
    return card;
}

function formatDate(dateString) {
    const options = { weekday: 'short', day: 'numeric', month: 'short' };
    return new Date(dateString).toLocaleDateString('en-IN', options);
}

function initCalendar() {
    // Initialize calendar functionality
    // This would typically use a calendar library like FullCalendar
    console.log('Calendar initialized');
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
        events: 3,
        revenue: '₹2,50,000',
        rating: 4.7
    };

    document.querySelector('.stat-value:nth-child(1)').textContent = stats.events;
    document.querySelector('.stat-value:nth-child(2)').textContent = stats.revenue;
    document.querySelector('.stat-value:nth-child(3)').textContent = stats.rating;
} 