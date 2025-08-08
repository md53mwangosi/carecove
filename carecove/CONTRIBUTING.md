
# Contributing to CareCove

Thank you for your interest in contributing to CareCove! This document provides guidelines and information for contributors.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Contributing Process](#contributing-process)
5. [Coding Standards](#coding-standards)
6. [Testing Guidelines](#testing-guidelines)
7. [Documentation](#documentation)
8. [Reporting Issues](#reporting-issues)
9. [Feature Requests](#feature-requests)
10. [Pull Request Process](#pull-request-process)

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

- **Be Respectful**: Treat all contributors with respect and kindness
- **Be Inclusive**: Welcome newcomers and help them contribute
- **Be Collaborative**: Work together to improve the project
- **Be Professional**: Maintain professional communication
- **Be Patient**: Help others learn and grow

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- Python 3.8 or higher
- Git version control
- Basic understanding of Django framework
- Familiarity with HTML, CSS, and JavaScript
- Understanding of database concepts

### Areas for Contribution

We welcome contributions in the following areas:

**Code Contributions:**
- Bug fixes
- New features
- Performance improvements
- Security enhancements
- Code refactoring

**Documentation:**
- README improvements
- Code documentation
- Deployment guides
- Tutorial creation
- Translation improvements

**Design & UX:**
- UI/UX improvements
- Mobile responsiveness
- Accessibility enhancements
- Theme customizations

**Testing:**
- Unit test creation
- Integration testing
- Performance testing
- Security testing

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YOUR-USERNAME/carecove-django.git
cd carecove-django

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL-OWNER/carecove-django.git
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt  # If available
```

### 3. Configure Environment

```bash
# Copy environment file
cp .env.example .env

# Edit with your development settings
nano .env
```

### 4. Set Up Database

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data
python manage.py seed_data
python manage.py seed_chatbot_data
```

### 5. Run Development Server

```bash
python manage.py runserver
```

## Contributing Process

### 1. Create an Issue

Before starting work:
- Check existing issues to avoid duplication
- Create a new issue describing the problem or feature
- Wait for discussion and approval for significant changes

### 2. Create a Branch

```bash
# Update your local main branch
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-number
```

### 3. Make Changes

- Write clean, readable code
- Follow coding standards (see below)
- Add tests for new functionality
- Update documentation as needed

### 4. Test Your Changes

```bash
# Run tests
python manage.py test

# Check code style (if configured)
flake8 .
black .

# Test manually
python manage.py runserver
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: add new feature description"
# or
git commit -m "fix: resolve issue with specific problem"
```

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Coding Standards

### Python Code Style

Follow PEP 8 guidelines:

```python
# Good: Clear, descriptive names
def calculate_order_total(cart_items):
    """Calculate the total price of items in cart."""
    total = 0
    for item in cart_items:
        total += item.price * item.quantity
    return total

# Good: Proper imports
from django.db import models
from django.contrib.auth.models import User

# Good: Class naming
class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural = 'Product Categories'
```

### Django Best Practices

**Models:**
```python
class Product(models.Model):
    # Use descriptive field names
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Add Meta class for options
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Products'
    
    # Add string representation
    def __str__(self):
        return self.name
    
    # Add custom methods after special methods
    def get_absolute_url(self):
        return reverse('product_detail', args=[self.pk])
```

**Views:**
```python
# Use class-based views when appropriate
class ProductListView(ListView):
    model = Product
    template_name = 'shop/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

# Use function-based views for simple logic
def add_to_cart(request, product_id):
    """Add product to shopping cart."""
    if request.method == 'POST':
        # Handle POST logic
        pass
    return redirect('cart_detail')
```

**Templates:**
```html
<!-- Use semantic HTML -->
<article class="product-card">
    <header>
        <h3>{{ product.name }}</h3>
    </header>
    <div class="product-content">
        <p>{{ product.description|truncatewords:20 }}</p>
    </div>
    <footer>
        <span class="price">${{ product.price }}</span>
    </footer>
</article>
```

### CSS Guidelines

```css
/* Use BEM methodology for CSS classes */
.product-card {
    border: 1px solid #ddd;
    padding: 1rem;
}

.product-card__title {
    font-size: 1.2rem;
    font-weight: bold;
}

.product-card__title--featured {
    color: #f4d03f;
}

/* Use CSS custom properties for theming */
:root {
    --primary-color: #f4d03f;
    --secondary-color: #2c3e50;
    --border-radius: 4px;
}
```

### JavaScript Guidelines

```javascript
// Use modern ES6+ syntax
const cart = {
    items: [],
    
    addItem(product) {
        const existingItem = this.items.find(item => item.id === product.id);
        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            this.items.push({ ...product, quantity: 1 });
        }
        this.updateDisplay();
    },
    
    async updateDisplay() {
        try {
            const response = await fetch('/api/cart/update/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(this.items)
            });
            
            if (!response.ok) {
                throw new Error('Failed to update cart');
            }
            
            // Update UI
        } catch (error) {
            console.error('Cart update error:', error);
        }
    }
};
```

## Testing Guidelines

### Writing Tests

```python
from django.test import TestCase, Client
from django.contrib.auth.models import User
from shop.models import Product, Category

class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        
    def test_product_creation(self):
        """Test that a product can be created successfully."""
        product = Product.objects.create(
            name='Test Product',
            description='Test description',
            price=29.99,
            category=self.category
        )
        
        self.assertEqual(product.name, 'Test Product')
        self.assertEqual(str(product), 'Test Product')
        
    def test_product_absolute_url(self):
        """Test product absolute URL generation."""
        product = Product.objects.create(
            name='Test Product',
            price=29.99,
            category=self.category
        )
        
        expected_url = f'/products/{product.pk}/'
        self.assertEqual(product.get_absolute_url(), expected_url)

class ProductViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
    def test_product_list_view(self):
        """Test product list view returns correct response."""
        response = self.client.get('/products/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Products')
        
    def test_add_to_cart_authenticated(self):
        """Test adding product to cart when authenticated."""
        self.client.login(username='testuser', password='testpass123')
        
        product = Product.objects.create(
            name='Test Product',
            price=29.99,
            category=self.category
        )
        
        response = self.client.post(f'/cart/add/{product.pk}/')
        
        self.assertEqual(response.status_code, 302)  # Redirect after add
```

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test shop

# Run specific test class
python manage.py test shop.tests.ProductModelTest

# Run with coverage (if installed)
coverage run --source='.' manage.py test
coverage report
coverage html
```

## Documentation

### Code Documentation

```python
def process_payment(order, payment_method):
    """
    Process payment for an order using specified payment method.
    
    Args:
        order (Order): The order instance to process payment for
        payment_method (str): Payment method ('pesapal', 'mpesa', etc.)
        
    Returns:
        dict: Payment result with status and transaction details
        
    Raises:
        PaymentError: If payment processing fails
        ValueError: If payment method is not supported
        
    Example:
        >>> order = Order.objects.get(pk=1)
        >>> result = process_payment(order, 'pesapal')
        >>> print(result['status'])
        'success'
    """
    if payment_method not in SUPPORTED_PAYMENT_METHODS:
        raise ValueError(f"Unsupported payment method: {payment_method}")
    
    # Implementation here
    pass
```

### API Documentation

Document API endpoints clearly:

```python
# views.py
class ProductAPIView(APIView):
    """
    API endpoint for product operations.
    
    GET /api/products/ - List all products
    POST /api/products/ - Create new product (admin only)
    GET /api/products/{id}/ - Get specific product
    PUT /api/products/{id}/ - Update product (admin only)
    DELETE /api/products/{id}/ - Delete product (admin only)
    """
    
    def get(self, request, pk=None):
        """
        Retrieve product(s).
        
        Query Parameters:
            category (str): Filter by category slug
            search (str): Search in product name and description
            page (int): Page number for pagination
            
        Returns:
            200: List of products or single product
            404: Product not found (for single product requests)
        """
        pass
```

## Reporting Issues

### Bug Reports

When reporting bugs, please include:

1. **Environment Information:**
   - Operating system
   - Python version
   - Django version
   - Browser (if web-related)

2. **Steps to Reproduce:**
   ```
   1. Go to product page
   2. Click 'Add to Cart'
   3. Navigate to cart
   4. See error message
   ```

3. **Expected vs Actual Behavior:**
   - Expected: Product should be added to cart
   - Actual: Error message appears

4. **Screenshots/Logs:** Include relevant screenshots or error logs

5. **Additional Context:** Any other relevant information

### Security Issues

For security vulnerabilities:
- Do NOT create public issues
- Email security@carecove.co.tz directly
- Include detailed information about the vulnerability
- Allow time for investigation before public disclosure

## Feature Requests

When requesting features:

1. **Use Case:** Describe the problem this feature would solve
2. **Proposed Solution:** Your idea for implementing the feature
3. **Alternatives:** Other solutions you've considered
4. **Additional Context:** Screenshots, mockups, or examples

Example:
```
**Feature Request: Product Comparison**

**Use Case:**
Customers want to compare multiple sea moss products side-by-side to make informed purchasing decisions.

**Proposed Solution:**
Add a comparison feature that allows users to:
- Select multiple products for comparison
- View side-by-side comparison table
- Compare prices, features, and specifications

**Alternatives:**
- Product recommendation system
- Enhanced filtering options

**Additional Context:**
Similar to Amazon's product comparison feature. Could be particularly useful for different sea moss variants (gel, powder, capsules).
```

## Pull Request Process

### Before Submitting

1. **Sync with Main:**
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-feature-branch
   git rebase main
   ```

2. **Review Your Changes:**
   - Check for console errors
   - Test on different screen sizes
   - Verify accessibility
   - Run all tests

3. **Update Documentation:**
   - Update README if needed
   - Add docstrings to new functions
   - Update API documentation

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

## Screenshots (if applicable)
Add screenshots to help explain your changes

## Checklist
- [ ] My code follows the project's coding standards
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] Any dependent changes have been merged and published
```

### Review Process

1. **Automated Checks:** Ensure all CI checks pass
2. **Code Review:** At least one maintainer will review your code
3. **Testing:** Changes will be tested in staging environment
4. **Approval:** Once approved, changes will be merged

### After Merge

1. **Clean Up:**
   ```bash
   git checkout main
   git pull upstream main
   git branch -d your-feature-branch
   ```

2. **Update Fork:**
   ```bash
   git push origin main
   ```

## Development Workflow

### Git Flow

We use a simplified Git flow:

- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/**: New features
- **bugfix/**: Bug fixes
- **hotfix/**: Critical production fixes

### Commit Messages

Use conventional commit format:

```
type(scope): description

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build process or auxiliary tool changes

Examples:
```
feat(cart): add quantity update functionality

fix(auth): resolve login redirect issue

docs(readme): update installation instructions

style(css): improve mobile responsiveness

refactor(models): optimize database queries

test(shop): add product model tests

chore(deps): update Django to 5.2.4
```

## Getting Help

### Communication Channels

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Email**: development@carecove.co.tz for direct contact

### Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Python Style Guide (PEP 8)](https://pep8.org/)
- [Git Documentation](https://git-scm.com/doc)

### Mentorship

New contributors can request mentorship:
- Comment on issues you'd like to work on
- Ask questions in GitHub discussions
- Request code review guidance

## Recognition

Contributors will be recognized:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Special recognition for significant contributions

## License

By contributing to CareCove, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

Thank you for contributing to CareCove! Your efforts help make premium sea moss products more accessible to customers in Tanzania and beyond. 🌊🇹🇿
