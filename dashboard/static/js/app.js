// Main application JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initTooltips();
    
    // Initialize notifications
    initNotifications();
    
    // Load any saved preferences
    loadPreferences();
});

// Tooltips
function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(el => {
        el.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = this.getAttribute('data-tooltip');
            tooltip.style.position = 'absolute';
            tooltip.style.background = '#333';
            tooltip.style.color = '#fff';
            tooltip.style.padding = '5px 10px';
            tooltip.style.borderRadius = '4px';
            tooltip.style.fontSize = '0.8rem';
            tooltip.style.zIndex = '1000';
            tooltip.style.left = (this.getBoundingClientRect().left + window.scrollX) + 'px';
            tooltip.style.top = (this.getBoundingClientRect().top + window.scrollY - 30) + 'px';
            
            document.body.appendChild(tooltip);
            
            this.addEventListener('mouseleave', function() {
                tooltip.remove();
            }, { once: true });
        });
    });
}

// Notifications
let notificationQueue = [];

function showNotification(message, type = 'info', timeout = 5000) {
    const notification = {
        message: message,
        type: type,
        timeout: timeout
    };
    
    notificationQueue.push(notification);
    
    if (notificationQueue.length === 1) {
        displayNextNotification();
    }
}

function displayNextNotification() {
    if (notificationQueue.length === 0) return;
    
    const notification = notificationQueue[0];
    const notificationElement = document.createElement('div');
    notificationElement.className = `notification notification-${notification.type}`;
    notificationElement.innerHTML = `<i class="fas fa-info-circle"></i> ${notification.message}`;
    notificationElement.style.position = 'fixed';
    notificationElement.style.bottom = '20px';
    notificationElement.style.right = '20px';
    notificationElement.style.padding = '15px';
    notificationElement.style.borderRadius = '4px';
    notificationElement.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
    notificationElement.style.zIndex = '1000';
    notificationElement.style.minWidth = '250px';
    notificationElement.style.maxWidth = '400px';
    notificationElement.style.animation = 'slideIn 0.3s ease-out';
    
    // Style based on type
    if (notification.type === 'success') {
        notificationElement.style.background = '#d4edda';
        notificationElement.style.color = '#155724';
        notificationElement.style.borderLeft = '4px solid #28a745';
    } else if (notification.type === 'error') {
        notificationElement.style.background = '#f8d7da';
        notificationElement.style.color = '#721c24';
        notificationElement.style.borderLeft = '4px solid #dc3545';
    } else if (notification.type === 'warning') {
        notificationElement.style.background = '#fff3cd';
        notificationElement.style.color = '#856404';
        notificationElement.style.borderLeft = '4px solid #ffc107';
    } else {
        notificationElement.style.background = '#d1ecf1';
        notificationElement.style.color = '#0c5460';
        notificationElement.style.borderLeft = '4px solid #17a2b8';
    }
    
    document.body.appendChild(notificationElement);
    
    // Remove notification after timeout
    setTimeout(() => {
        notificationElement.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            notificationElement.remove();
            notificationQueue.shift();
            displayNextNotification();
        }, 300);
    }, notification.timeout);
}

// Preferences
function loadPreferences() {
    // Load from localStorage
    const preferences = localStorage.getItem('newsCrawlerPreferences');
    if (preferences) {
        try {
            const prefs = JSON.parse(preferences);
            // Apply preferences
            if (prefs.theme) {
                document.body.className = prefs.theme;
            }
        } catch (e) {
            console.error('Error loading preferences:', e);
        }
    }
}

function savePreferences(preferences) {
    localStorage.setItem('newsCrawlerPreferences', JSON.stringify(preferences));
}

// Utility functions
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleString();
}

function formatRelativeDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    const intervals = {
        year: 31536000,
        month: 2592000,
        week: 604800,
        day: 86400,
        hour: 3600,
        minute: 60,
        second: 1
    };
    
    for (const [unit, seconds] of Object.entries(intervals)) {
        const interval = Math.floor(diffInSeconds / seconds);
        if (interval >= 1) {
            return `${interval} ${unit}${interval === 1 ? '' : 's'} ago`;
        }
    }
    
    return 'just now';
}

function truncateText(text, maxLength) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
