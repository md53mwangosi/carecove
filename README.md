
# CareCove - Premium Sea Moss E-commerce Platform

[![Django Version](https://i.ytimg.com/vi/8zDeeXZ8-X8/maxresdefault.jpg)
[![Python Version](https://i.ytimg.com/vi/4cgpu9L2AE8/maxresdefault.jpg)
[![License](https://i.pinimg.com/originals/aa/d7/7c/aad77c6c55e2b544d326271d039eef77.png)

CareCove is a comprehensive e-commerce platform specifically designed for premium sea moss products from Tanzania. The platform features beautiful Tanzanian beach aesthetics, multi-language support (English/Swahili), AI-powered chatbot assistance, and WhatsApp integration for customer support.

## 🌟 Features

### E-commerce Core
- **Product Management**: Full product catalog with categories, variants, and inventory tracking
- **Shopping Cart & Checkout**: Seamless shopping experience with persistent cart functionality
- **Order Management**: Complete order processing and tracking system
- **User Authentication**: Secure user registration, login, and profile management
- **Payment Integration**: Ready for Pesapal payment gateway integration

### AI-Powered Customer Support
- **Intelligent Chatbot**: LLM-powered chatbot for instant customer assistance
- **WhatsApp Integration**: Seamless handoff to WhatsApp support (+255742604651)
- **FAQ System**: Automated responses for common customer queries
- **Chat History**: Complete conversation tracking and management

### Multi-Language Support
- **English & Swahili**: Full localization support for Tanzanian market
- **Dynamic Language Switching**: Users can switch languages on the fly
- **Localized Content**: Product descriptions and UI elements in both languages

### Beautiful Design
- **Tanzanian Beach Theme**: Authentic coastal imagery and golden yellow branding
- **Responsive Design**: Perfect experience across all devices
- **Modern UI**: Clean, professional interface with smooth animations
- **Product-Focused Layout**: Immediate product showcase on homepage

### Admin Features
- **Django Admin Panel**: Complete backend management interface
- **Product Management**: Easy product and category administration
- **Order Tracking**: Monitor and manage customer orders
- **Customer Support**: View chat sessions and customer inquiries
- **Newsletter Management**: Handle email subscriptions and campaigns

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Git
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
```bash
git clone <your-repository-url>
cd carecove-django
```

2. **Create and activate virtual environment**
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env file with your configuration
```

5. **Run database migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser (admin account)**
```bash
python manage.py createsuperuser
```

7. **Load sample data (optional)**
```bash
python manage.py seed_data
python manage.py seed_chatbot_data
```

8. **Collect static files**
```bash
python manage.py collectstatic --noinput
```

9. **Run the development server**
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to see your CareCove store!

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (for production)
DATABASE_URL=postgres://user:password@localhost/carecove

# LLM API (for chatbot)
ABACUSAI_API_KEY=your-api-key-here

# Email Settings (for production)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True

# Payment Gateway (Pesapal)
PESAPAL_CONSUMER_KEY=your-consumer-key
PESAPAL_CONSUMER_SECRET=your-consumer-secret
PESAPAL_DEMO=True

# WhatsApp Integration
WHATSAPP_NUMBER=+255742604651
```

### Database Configuration

**Development (SQLite - Default)**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**Production (PostgreSQL)**
```python
import dj_database_url
DATABASES = {
    'default': dj_database_url.parse(config('DATABASE_URL'))
}
```

## 📁 Project Structure

```
carecove-django/
├── accounts/              # User authentication & profiles
├── cart/                  # Shopping cart functionality
├── chatbot/              # AI chatbot & WhatsApp integration
├── newsletter/           # Email newsletter management
├── shop/                 # Core e-commerce functionality
├── testimonials/         # Customer testimonials
├── carecove/            # Main project settings
├── templates/           # HTML templates
├── static/              # CSS, JavaScript, Images
├── media/               # User-uploaded files
├── locale/              # Translation files
├── requirements.txt     # Python dependencies
├── manage.py           # Django management script
└── README.md           # This file
```

## 🛠 Key Components

### Apps Overview

1. **shop**: Core e-commerce functionality (products, categories, orders)
2. **cart**: Shopping cart and checkout process
3. **accounts**: User authentication and profile management
4. **chatbot**: AI-powered customer support with WhatsApp integration
5. **testimonials**: Customer reviews and testimonials
6. **newsletter**: Email subscription management

### API Endpoints

**Chatbot API**
- `POST /chatbot/chat/` - Send message to chatbot
- `GET /chatbot/quick-responses/` - Get quick response options
- `GET /chatbot/history/<session_id>/` - Get chat history
- `POST /chatbot/whatsapp-transfer/` - Transfer to WhatsApp

**Shop API**
- `GET /shop/products/` - List all products
- `GET /shop/categories/` - List all categories
- `POST /cart/add/` - Add item to cart
- `GET /cart/` - View cart contents

## 🎨 Customization

### Branding
- **Primary Color**: Golden Yellow (#F4D03F)
- **Background**: Tanzanian beach imagery
- **Logo**: Update in `static/img/` directory
- **Fonts**: Modify in `static/css/style.css`

### Adding Products
1. Access Django admin at `/admin/`
2. Navigate to Shop → Products
3. Add product details, images, and descriptions
4. Set categories and pricing
5. Enable product for display

### Multi-Language Content
1. Update translation files in `locale/` directory
2. Use Django's translation system for new content
3. Run `python manage.py makemessages` to extract strings
4. Run `python manage.py compilemessages` to compile translations

## 🚀 Deployment

### Production Checklist

1. **Environment Configuration**
   - Set `DEBUG=False`
   - Configure `ALLOWED_HOSTS`
   - Set up production database
   - Configure email settings

2. **Security**
   - Generate new `SECRET_KEY`
   - Set up HTTPS
   - Configure secure headers
   - Set up proper file permissions

3. **Performance**
   - Configure caching
   - Optimize database queries
   - Set up CDN for static files
   - Enable compression

4. **Monitoring**
   - Set up error logging
   - Configure monitoring tools
   - Set up backup systems

See `deployment_guide.md` for detailed deployment instructions.

## 📱 WhatsApp Integration

The platform includes seamless WhatsApp integration for customer support:

- **Automatic Handoff**: Chatbot can transfer conversations to WhatsApp
- **Contact Number**: +255742604651
- **Integration Points**: Chat widget, contact forms, order support

To customize the WhatsApp number, update `WHATSAPP_NUMBER` in settings.

## 🤖 AI Chatbot Features

- **Intelligent Responses**: LLM-powered natural language understanding
- **Product Information**: Automated product recommendations and details
- **Order Support**: Help with order status and general inquiries
- **FAQ Handling**: Instant answers to common questions
- **Conversation History**: Complete chat session tracking

## 🧪 Testing

Run the test suite:

```bash
python manage.py test
```

Test specific apps:

```bash
python manage.py test shop
python manage.py test chatbot
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

For support and inquiries:

- **WhatsApp**: +255742604651
- **Email**: support@carecove.co.tz
- **Website**: [www.carecove.co.tz](https://www.carecove.co.tz)

## 🙏 Acknowledgments

- Django community for the excellent framework
- Tanzanian coastal imagery for beautiful backgrounds
- Open source libraries and contributors
- Sea moss farmers and suppliers in Tanzania

---

**CareCove** - Bringing the best of Tanzanian sea moss to the world! 🌊🇹🇿

# Invoice Generation Feature

## Overview
This feature allows you to generate and send invoices to customers via email before they complete payment.

## How to Use

### 1. Generate Invoice
- Go to Admin Panel → Orders
- Click on any order to view details
- Click "Invoice" button to view the invoice in browser
- Or click "Send Invoice" to email it directly to the customer

### 2. Email Configuration
Set these environment variables in your `.env` file:
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@carecove.co.tz
```

### 3. Features
- **PDF Generation**: Invoices are automatically generated as PDF attachments
- **Professional Design**: Clean, branded invoice template
- **Email Templates**: Customizable email templates for invoice notifications
- **Bulk Actions**: Send invoices from both order detail and orders list views

### 4. Invoice Content
Each invoice includes:
- Order details and items
- Customer billing information
- Company information (CareCove)
- Payment instructions
- Due date (7 days from order date)
- Professional formatting

## Testing
For development, emails will be printed to console. To test with real emails:
1. Configure email settings in `.env`
2. Create a test order
3. Use the "Send Invoice" button
4. Check the customer's email

## Dependencies
- `reportlab` for PDF generation (already installed)
- Django email backend configuration

# Customer Invoice Download Feature

## Overview
Customers can now download their invoices immediately after completing the checkout process, even before payment is completed.

## How It Works

### 1. After Checkout
- Customer completes checkout form
- Order is created with "pending" status
- Customer is redirected to order confirmation page
- Invoice download links are immediately available

### 2. Invoice Access Points
- **Payment Success Page**: Direct download links after checkout
- **Order Detail Page**: Customer can view and download invoice anytime
- **Email Confirmation**: Invoice attached to order confirmation email (optional)

### 3. Security Features
- **Authenticated Users**: Only order owner can access invoice
- **Guest Users**: Access via session-based order ID
- **PDF Generation**: Professional PDF with logo and watermark

## URLs
- `cart/order/<order_id>/` - Order detail page
- `cart/order/<order_id>/invoice/` - View invoice in browser
- `cart/order/<order_id>/invoice/?format=pdf` - Download PDF

## Features
- ✅ **Logo Integration**: CareCove logo in top-left corner
- ✅ **Watermark**: "CARECOVE" watermark on PDF
- ✅ **Professional Design**: Clean, branded invoice layout
- ✅ **Multiple Formats**: Web view and PDF download
- ✅ **Security**: Proper access control for customers
- ✅ **Responsive**: Works on mobile and desktop

## Usage Example
After customer completes checkout:
1. Order created with order number (e.g., CC01431224)
2. Customer sees: "Your invoice is ready for download"
3. Customer can click "Download PDF Invoice" immediately
4. Invoice includes all order details, logo, and watermark

## Testing
1. Add items to cart
2. Complete checkout process
3. On payment success page, click "Download PDF Invoice"
4. Verify logo appears and watermark is visible
