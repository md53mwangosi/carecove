
// CareCove JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    
    // Newsletter subscription
    const newsletterForm = document.getElementById('newsletterForm');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const button = this.querySelector('button[type="submit"]');
            const originalHtml = button.innerHTML;
            
            // Show loading state
            button.innerHTML = '<div class="spinner"></div>';
            button.disabled = true;
            
            fetch('/newsletter/subscribe/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast('Thank you for subscribing!', 'success');
                    this.reset();
                } else {
                    showToast('Please enter a valid email address.', 'error');
                }
            })
            .catch(error => {
                showToast('Something went wrong. Please try again.', 'error');
            })
            .finally(() => {
                button.innerHTML = originalHtml;
                button.disabled = false;
            });
        });
    }
    
    // Add to cart functionality
    const addToCartForms = document.querySelectorAll('.add-to-cart-form');
    addToCartForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const button = this.querySelector('button[type="submit"]');
            const originalHtml = button.innerHTML;
            
            // Show loading state
            button.innerHTML = '<div class="spinner"></div> Adding...';
            button.disabled = true;
            
            fetch('/cart/add/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateCartBadge(data.cart_total_items);
                    showToast('Product added to cart!', 'success');
                } else {
                    showToast('Failed to add product to cart.', 'error');
                }
            })
            .catch(error => {
                showToast('Something went wrong. Please try again.', 'error');
            })
            .finally(() => {
                button.innerHTML = originalHtml;
                button.disabled = false;
            });
        });
    });
    
    // Cart quantity update
    const quantityInputs = document.querySelectorAll('.quantity-input');
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            updateCartItem(this);
        });
    });
    
    // Remove from cart
    const removeButtons = document.querySelectorAll('.remove-from-cart');
    removeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            removeFromCart(this);
        });
    });
    
    // WhatsApp integration
    const whatsappButtons = document.querySelectorAll('.whatsapp-btn');
    whatsappButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const message = this.dataset.message || 'Hello, I\'m interested in your Sea Moss products!';
            const phoneNumber = '255742604651';
            const whatsappUrl = `https://wa.me/${phoneNumber}?text=${encodeURIComponent(message)}`;
            window.open(whatsappUrl, '_blank');
        });
    });
    
    // Product image gallery
    const productThumbnails = document.querySelectorAll('.product-thumbnail');
    productThumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('click', function() {
            const mainImage = document.querySelector('.product-main-image');
            if (mainImage) {
                mainImage.src = this.src;
                mainImage.alt = this.alt;
                
                // Update active thumbnail
                productThumbnails.forEach(thumb => thumb.classList.remove('active'));
                this.classList.add('active');
            }
        });
    });
    
    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Product filtering
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const filterValue = this.dataset.filter;
            
            // Update active filter button
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Filter products
            const products = document.querySelectorAll('.product-card');
            products.forEach(product => {
                if (filterValue === 'all' || product.dataset.category === filterValue) {
                    product.style.display = 'block';
                    product.classList.add('fade-in-up');
                } else {
                    product.style.display = 'none';
                }
            });
        });
    });
    
    // Search functionality
    const searchInput = document.querySelector('input[name="q"]');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.closest('form').submit();
            }
        });
    }
    
    // Rating stars interaction
    const ratingStars = document.querySelectorAll('.rating-star');
    ratingStars.forEach((star, index) => {
        star.addEventListener('click', function() {
            const rating = index + 1;
            const ratingInput = document.querySelector('input[name="rating"]');
            
            if (ratingInput) {
                ratingInput.value = rating;
            }
            
            // Update visual stars
            ratingStars.forEach((s, i) => {
                if (i < rating) {
                    s.classList.add('active');
                } else {
                    s.classList.remove('active');
                }
            });
        });
    });
    
    // Lazy loading for images
    const lazyImages = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    lazyImages.forEach(img => imageObserver.observe(img));
});

// Helper functions
function updateCartBadge(count) {
    const badge = document.querySelector('.cart-badge');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'flex' : 'none';
    }
}

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
    formData.append('csrfmiddlewaretoken', getCSRFToken());
    
    fetch('/cart/update/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCartBadge(data.cart_total_items);
            location.reload(); // Reload to update cart totals
        }
    })
    .catch(error => {
        showToast('Failed to update cart.', 'error');
    });
}

function removeFromCart(element) {
    const itemId = element.dataset.itemId;
    
    if (!confirm('Are you sure you want to remove this item from cart?')) {
        return;
    }
    
    const formData = new FormData();
    formData.append('item_id', itemId);
    formData.append('csrfmiddlewaretoken', getCSRFToken());
    
    fetch('/cart/remove/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCartBadge(data.cart_total_items);
            location.reload();
        }
    })
    .catch(error => {
        showToast('Failed to remove item from cart.', 'error');
    });
}

function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `alert alert-${type === 'error' ? 'danger' : 'success'} alert-dismissible fade show`;
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to messages container
    let messagesContainer = document.querySelector('.messages-container');
    if (!messagesContainer) {
        messagesContainer = document.createElement('div');
        messagesContainer.className = 'messages-container';
        document.body.appendChild(messagesContainer);
    }
    
    messagesContainer.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, 5000);
}

function getCSRFToken() {
    const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
    return tokenElement ? tokenElement.value : '';
}

// Intersection Observer for animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in-up');
        }
    });
}, observerOptions);

// Observe elements for animation
document.addEventListener('DOMContentLoaded', function() {
    const animatedElements = document.querySelectorAll('.product-card, .testimonial-card, .section');
    animatedElements.forEach(el => observer.observe(el));
});

// Chatbot functionality
class ChatBot {
    constructor() {
        this.isOpen = false;
        this.isLoading = false;
        this.init();
    }

    init() {
        this.createChatWidget();
        this.bindEvents();
        this.loadChatHistory();
        this.loadQuickResponses();
        this.showWelcomeMessage();
    }

    createChatWidget() {
        const chatHTML = `
            <div class="chat-widget">
                <button class="chat-toggle-btn" id="chatToggle">
                    <i class="fas fa-comments"></i>
                    <span class="chat-notification" id="chatNotification" style="display: none;">1</span>
                </button>
                
                <div class="chat-container" id="chatContainer">
                    <div class="chat-header">
                        <div class="chat-header-content">
                            <h4>
                                <i class="fas fa-leaf"></i>
                                CareCove Assistant
                            </h4>
                            <p>How can I help you with our Sea Moss products?</p>
                        </div>
                        <button class="chat-close" id="chatClose">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    
                    <div class="chat-messages" id="chatMessages">
                        <div class="typing-indicator" id="typingIndicator">
                            <div class="typing-dots">
                                <div class="typing-dot"></div>
                                <div class="typing-dot"></div>
                                <div class="typing-dot"></div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="quick-responses" id="quickResponses">
                        <!-- Quick responses will be loaded here -->
                    </div>
                    
                    <div class="chat-input-container">
                        <form class="chat-input-form" id="chatForm">
                            <textarea 
                                class="chat-input" 
                                id="chatInput" 
                                placeholder="Type your message..."
                                rows="1"
                            ></textarea>
                            <button type="submit" class="chat-send-btn" id="chatSend">
                                <i class="fas fa-paper-plane"></i>
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', chatHTML);
    }

    bindEvents() {
        const chatToggle = document.getElementById('chatToggle');
        const chatClose = document.getElementById('chatClose');
        const chatForm = document.getElementById('chatForm');
        const chatInput = document.getElementById('chatInput');
        
        chatToggle.addEventListener('click', () => this.toggleChat());
        chatClose.addEventListener('click', () => this.closeChat());
        chatForm.addEventListener('submit', (e) => this.sendMessage(e));
        
        // Auto-resize textarea
        chatInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 60) + 'px';
        });
        
        // Enter to send (Shift+Enter for new line)
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage(e);
            }
        });
    }

    toggleChat() {
        const container = document.getElementById('chatContainer');
        const toggleBtn = document.getElementById('chatToggle');
        const notification = document.getElementById('chatNotification');
        
        this.isOpen = !this.isOpen;
        
        if (this.isOpen) {
            container.classList.add('active');
            toggleBtn.classList.add('active');
            toggleBtn.innerHTML = '<i class="fas fa-times"></i>';
            notification.style.display = 'none';
            
            // Focus input
            setTimeout(() => {
                document.getElementById('chatInput').focus();
            }, 300);
        } else {
            this.closeChat();
        }
    }

    closeChat() {
        const container = document.getElementById('chatContainer');
        const toggleBtn = document.getElementById('chatToggle');
        
        this.isOpen = false;
        container.classList.remove('active');
        toggleBtn.classList.remove('active');
        toggleBtn.innerHTML = '<i class="fas fa-comments"></i><span class="chat-notification" id="chatNotification" style="display: none;">1</span>';
    }

    async sendMessage(e) {
        e.preventDefault();
        
        if (this.isLoading) return;
        
        const input = document.getElementById('chatInput');
        const message = input.value.trim();
        
        if (!message) return;
        
        // Clear input
        input.value = '';
        input.style.height = 'auto';
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Show typing indicator
        this.showTyping();
        
        this.isLoading = true;
        const sendBtn = document.getElementById('chatSend');
        sendBtn.disabled = true;
        
        try {
            const response = await fetch('/chatbot/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ message })
            });
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Hide typing indicator
            this.hideTyping();
            
            // Add bot response
            this.addMessage(data.message, 'bot');
            
            // Show product recommendations if available
            if (data.product_recommendations && data.product_recommendations.length > 0) {
                this.showProductRecommendations(data.product_recommendations);
            }
            
        } catch (error) {
            this.hideTyping();
            this.addMessage('Sorry, I encountered an error. Please try again or contact our support team via WhatsApp.', 'bot');
            console.error('Chat error:', error);
        } finally {
            this.isLoading = false;
            sendBtn.disabled = false;
        }
    }

    addMessage(content, type) {
        const messagesContainer = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${type}`;
        
        const timestamp = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        messageDiv.innerHTML = `
            <div class="message-content">
                ${content.replace(/\n/g, '<br>')}
            </div>
            <div class="message-timestamp">${timestamp}</div>
        `;
        
        // Insert before typing indicator
        const typingIndicator = document.getElementById('typingIndicator');
        messagesContainer.insertBefore(messageDiv, typingIndicator);
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    showProductRecommendations(products) {
        const messagesContainer = document.getElementById('chatMessages');
        const recommendationsDiv = document.createElement('div');
        recommendationsDiv.className = 'message message-bot';
        
        let productsHTML = '<h6>Recommended Products:</h6>';
        products.forEach(product => {
            productsHTML += `
                <div class="product-recommendation" onclick="window.location.href='${product.url}'">
                    <strong>${product.name}</strong> - <span class="price">$${product.price}</span><br>
                    <small>${product.description}</small>
                </div>
            `;
        });
        
        recommendationsDiv.innerHTML = `
            <div class="message-content">
                <div class="product-recommendations">
                    ${productsHTML}
                </div>
            </div>
        `;
        
        const typingIndicator = document.getElementById('typingIndicator');
        messagesContainer.insertBefore(recommendationsDiv, typingIndicator);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    showTyping() {
        document.getElementById('typingIndicator').classList.add('active');
        const messagesContainer = document.getElementById('chatMessages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    hideTyping() {
        document.getElementById('typingIndicator').classList.remove('active');
    }

    async loadQuickResponses() {
        try {
            const response = await fetch('/chatbot/api/quick-responses/');
            const data = await response.json();
            
            const container = document.getElementById('quickResponses');
            container.innerHTML = '';
            
            data.quick_responses.forEach(qr => {
                const button = document.createElement('button');
                button.className = 'quick-response-btn';
                button.innerHTML = `<i class="${qr.icon}"></i> ${qr.title}`;
                button.title = qr.description;
                
                button.addEventListener('click', () => {
                    if (qr.action_type === 'whatsapp') {
                        this.transferToWhatsApp();
                    } else {
                        // Send as user message
                        document.getElementById('chatInput').value = qr.title;
                        this.sendMessage(new Event('submit'));
                    }
                });
                
                container.appendChild(button);
            });
        } catch (error) {
            console.error('Failed to load quick responses:', error);
        }
    }

    async transferToWhatsApp() {
        try {
            const response = await fetch('/chatbot/api/transfer-whatsapp/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            const data = await response.json();
            
            if (data.whatsapp_url) {
                this.addMessage('Transferring you to WhatsApp for personal assistance...', 'system');
                
                // Add WhatsApp transfer button
                const messagesContainer = document.getElementById('chatMessages');
                const transferDiv = document.createElement('div');
                transferDiv.className = 'message message-bot';
                transferDiv.innerHTML = `
                    <div class="message-content">
                        <button class="whatsapp-transfer-btn" onclick="window.open('${data.whatsapp_url}', '_blank')">
                            <i class="fab fa-whatsapp"></i>
                            Continue on WhatsApp
                        </button>
                    </div>
                `;
                
                const typingIndicator = document.getElementById('typingIndicator');
                messagesContainer.insertBefore(transferDiv, typingIndicator);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
        } catch (error) {
            console.error('WhatsApp transfer error:', error);
            this.addMessage('Failed to transfer to WhatsApp. Please contact us directly.', 'bot');
        }
    }

    async loadChatHistory() {
        try {
            const response = await fetch('/chatbot/api/chat-history/');
            const data = await response.json();
            
            const messagesContainer = document.getElementById('chatMessages');
            
            data.messages.forEach(msg => {
                if (msg.type !== 'system') {
                    this.addMessage(msg.content, msg.type);
                }
            });
            
        } catch (error) {
            console.error('Failed to load chat history:', error);
        }
    }

    showWelcomeMessage() {
        setTimeout(() => {
            if (!this.isOpen) {
                const notification = document.getElementById('chatNotification');
                notification.style.display = 'flex';
                
                // Auto-hide notification after 10 seconds
                setTimeout(() => {
                    if (notification && !this.isOpen) {
                        notification.style.display = 'none';
                    }
                }, 10000);
            }
        }, 3000);
    }

    getCSRFToken() {
        const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        return tokenElement ? tokenElement.value : '';
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if not in admin area
    if (!window.location.pathname.startsWith('/admin/')) {
        window.chatBot = new ChatBot();
    }
});
