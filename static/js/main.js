
// CareCove Main JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all functionality
    initializeNavigation();
    initializeCart();
    initializeSearch();
    initializeChatbot();
    initializeNewsletterForm();
    initializeWhatsApp();
    initializeProductFeatures();
    initializeFormValidation();
});

// Navigation functionality
function initializeNavigation() {
    // Mobile menu toggle
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
        });
    }
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Sticky header effect
    window.addEventListener('scroll', function() {
        const header = document.querySelector('.header');
        if (header) {
            if (window.scrollY > 100) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        }
    });
}

// Cart functionality
function initializeCart() {
    // Add to cart forms
    document.querySelectorAll('.add-to-cart-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            addToCart(this);
        });
    });
    
    // Quantity controls
    document.querySelectorAll('.quantity-input').forEach(input => {
        input.addEventListener('change', function() {
            updateCartItem(this);
        });
    });
    
    // Remove from cart buttons
    document.querySelectorAll('.remove-from-cart').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            removeFromCart(this);
        });
    });
}

// Add to cart function
function addToCart(form) {
    const formData = new FormData(form);
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    
    // Show loading state
    submitButton.disabled = true;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Adding...';
    
    fetch('/cart/add/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update cart badge
            updateCartBadge(data.cart_total_items);
            
            // Show success message
            showMessage('Product added to cart!', 'success');
            
            // Reset button
            submitButton.disabled = false;
            submitButton.innerHTML = originalText;
            
            // Optional: Show mini cart or redirect
            if (data.redirect) {
                window.location.href = data.redirect;
            }
        } else {
            showMessage(data.message || 'Error adding product to cart', 'error');
            submitButton.disabled = false;
            submitButton.innerHTML = originalText;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage('Error adding product to cart', 'error');
        submitButton.disabled = false;
        submitButton.innerHTML = originalText;
    });
}

// Update cart item quantity
function updateCartItem(input) {
    const itemId = input.dataset.itemId;
    const quantity = input.value;
    
    if (quantity < 1) {
        removeFromCart(input);
        return;
    }
    
    const formData = new FormData();
    formData.append('item_id', itemId);
    formData.append('quantity', quantity);
    formData.append('csrfmiddlewaretoken', getCsrfToken());
    
    fetch('/cart/update/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCartBadge(data.cart_total_items);
            updateCartTotals(data.cart_total_price);
            showMessage('Cart updated!', 'success');
        } else {
            showMessage(data.message || 'Error updating cart', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage('Error updating cart', 'error');
    });
}

// Remove from cart
function removeFromCart(button) {
    const itemId = button.dataset.itemId;
    
    if (confirm('Are you sure you want to remove this item from your cart?')) {
        const formData = new FormData();
        formData.append('item_id', itemId);
        formData.append('csrfmiddlewaretoken', getCsrfToken());
        
        fetch('/cart/remove/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Remove the item row
                const cartItem = button.closest('.cart-item');
                if (cartItem) {
                    cartItem.remove();
                }
                
                updateCartBadge(data.cart_total_items);
                updateCartTotals(data.cart_total_price);
                showMessage('Item removed from cart', 'success');
                
                // If cart is empty, show empty cart message
                if (data.cart_total_items === 0) {
                    location.reload();
                }
            } else {
                showMessage(data.message || 'Error removing item', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage('Error removing item', 'error');
        });
    }
}

// Update cart badge
function updateCartBadge(count) {
    const badge = document.querySelector('.cart-badge');
    if (badge) {
        if (count > 0) {
            badge.textContent = count;
            badge.style.display = 'inline-block';
        } else {
            badge.style.display = 'none';
        }
    }
}

// Update cart totals
function updateCartTotals(total) {
    const totalElements = document.querySelectorAll('.cart-total');
    totalElements.forEach(element => {
        element.textContent = `$${total.toFixed(2)}`;
    });
}

// Search functionality
function initializeSearch() {
    const searchForm = document.querySelector('.search-form');
    const searchInput = document.querySelector('.search-input');
    
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const query = searchInput.value.trim();
            if (query) {
                window.location.href = `/search/?q=${encodeURIComponent(query)}`;
            }
        });
    }
    
    // Live search suggestions (optional)
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const query = this.value.trim();
                if (query.length > 2) {
                    // Implement live search suggestions here
                    // fetchSearchSuggestions(query);
                }
            }, 300);
        });
    }
}

// Newsletter form
function initializeNewsletterForm() {
    const newsletterForm = document.getElementById('newsletterForm');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const submitButton = this.querySelector('button[type="submit"]');
            const originalHTML = submitButton.innerHTML;
            
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            
            fetch('/newsletter/subscribe/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage('Thank you for subscribing!', 'success');
                    this.reset();
                } else {
                    showMessage(data.message || 'Error subscribing to newsletter', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('Error subscribing to newsletter', 'error');
            })
            .finally(() => {
                submitButton.disabled = false;
                submitButton.innerHTML = originalHTML;
            });
        });
    }
}

// WhatsApp functionality
function initializeWhatsApp() {
    document.querySelectorAll('.whatsapp-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const message = this.dataset.message || 'Hi! I\'m interested in your Sea Moss products.';
            const phone = this.dataset.phone || '+255742604651';
            const url = `https://wa.me/${phone}?text=${encodeURIComponent(message)}`;
            window.open(url, '_blank');
        });
    });
}

// Product features
function initializeProductFeatures() {
    // Product image gallery
    const thumbnails = document.querySelectorAll('.thumbnail-img');
    const mainImage = document.getElementById('mainImage');
    
    thumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('click', function() {
            if (mainImage) {
                mainImage.src = this.src;
                mainImage.alt = this.alt;
            }
        });
    });
    
    // Product tabs
    const productTabs = document.querySelectorAll('#productTabs button');
    productTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const targetId = this.dataset.bsTarget;
            const targetPanel = document.querySelector(targetId);
            
            // Update active tab
            productTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // Update active panel
            document.querySelectorAll('.tab-pane').forEach(panel => {
                panel.classList.remove('show', 'active');
            });
            if (targetPanel) {
                targetPanel.classList.add('show', 'active');
            }
        });
    });
    
    // Product filters
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            const filterType = this.dataset.filter;
            if (filterType) {
                filterProducts(filterType);
            }
        });
    });
}

// Form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Real-time validation
    const inputs = document.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
    });
}

// Chatbot functionality
function initializeChatbot() {
    const chatButton = document.getElementById('chatButton');
    const chatWidget = document.getElementById('chatWidget');
    const chatClose = document.getElementById('chatClose');
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    const chatMessages = document.getElementById('chatMessages');
    
    if (chatButton) {
        chatButton.addEventListener('click', function() {
            chatWidget.classList.add('active');
            chatInput.focus();
        });
    }
    
    if (chatClose) {
        chatClose.addEventListener('click', function() {
            chatWidget.classList.remove('active');
        });
    }
    
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            sendChatMessage();
        });
    }
    
    // Load quick responses
    loadQuickResponses();
}

// Send chat message
function sendChatMessage() {
    const chatInput = document.getElementById('chatInput');
    const message = chatInput.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addMessageToChat(message, 'user');
    
    // Clear input
    chatInput.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    // Send message to backend
    fetch('/chatbot/chat/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            message: message,
            session_id: getChatSessionId()
        })
    })
    .then(response => response.json())
    .then(data => {
        hideTypingIndicator();
        if (data.response) {
            addMessageToChat(data.response, 'bot');
        }
        if (data.quick_responses) {
            showQuickResponses(data.quick_responses);
        }
    })
    .catch(error => {
        console.error('Chat error:', error);
        hideTypingIndicator();
        addMessageToChat('Sorry, I encountered an error. Please try again.', 'bot');
    });
}

// Add message to chat
function addMessageToChat(message, sender) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}`;
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.textContent = message;
    
    const messageTime = document.createElement('div');
    messageTime.className = 'message-time';
    messageTime.textContent = new Date().toLocaleTimeString();
    
    messageDiv.appendChild(messageContent);
    messageDiv.appendChild(messageTime);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Show typing indicator
function showTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'chat-message bot typing';
    typingDiv.id = 'typing-indicator';
    typingDiv.innerHTML = `
        <div class="message-content">
            <span class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </span>
        </div>
    `;
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Hide typing indicator
function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Load quick responses
function loadQuickResponses() {
    fetch('/chatbot/quick-responses/')
    .then(response => response.json())
    .then(data => {
        if (data.quick_responses) {
            showQuickResponses(data.quick_responses);
        }
    })
    .catch(error => {
        console.error('Error loading quick responses:', error);
    });
}

// Show quick responses
function showQuickResponses(responses) {
    const quickResponsesDiv = document.getElementById('quickResponses');
    if (!quickResponsesDiv) return;
    
    quickResponsesDiv.innerHTML = '';
    
    responses.forEach(response => {
        const button = document.createElement('button');
        button.className = 'btn btn-outline-primary btn-sm me-2 mb-2';
        button.textContent = response.text;
        button.addEventListener('click', function() {
            document.getElementById('chatInput').value = response.text;
            sendChatMessage();
        });
        quickResponsesDiv.appendChild(button);
    });
}

// Utility functions
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

function getChatSessionId() {
    return sessionStorage.getItem('chatSessionId') || generateSessionId();
}

function generateSessionId() {
    const sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    sessionStorage.setItem('chatSessionId', sessionId);
    return sessionId;
}

function validateField(field) {
    const isValid = field.checkValidity();
    const feedback = field.nextElementSibling;
    
    if (!isValid) {
        field.classList.add('is-invalid');
        if (feedback && feedback.classList.contains('invalid-feedback')) {
            feedback.style.display = 'block';
        }
    } else {
        field.classList.remove('is-invalid');
        if (feedback && feedback.classList.contains('invalid-feedback')) {
            feedback.style.display = 'none';
        }
    }
    
    return isValid;
}

function showMessage(message, type = 'success') {
    // Create toast message
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 5000);
}

function filterProducts(filterType) {
    const products = document.querySelectorAll('.product-card');
    
    products.forEach(product => {
        const productType = product.dataset.type;
        
        if (filterType === 'all' || productType === filterType) {
            product.style.display = 'block';
        } else {
            product.style.display = 'none';
        }
    });
}

// Animation on scroll
function initializeScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // Observe elements with animation classes
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });
}

// Initialize scroll animations
document.addEventListener('DOMContentLoaded', function() {
    initializeScrollAnimations();
});

// Export functions for global use
window.CareCove = {
    addToCart,
    updateCartItem,
    removeFromCart,
    sendChatMessage,
    showMessage,
    validateField
};
