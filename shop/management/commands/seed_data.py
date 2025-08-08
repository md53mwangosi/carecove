
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from shop.models import Category, Product, ProductImage, ProductVariant
from testimonials.models import Testimonial
from newsletter.models import Newsletter
import random

class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data seeding...'))

        # Create superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@carecove.co.tz', 'admin123')
            self.stdout.write(self.style.SUCCESS('Created superuser: admin/admin123'))

        # Create sample users
        users = []
        user_data = [
            ('john_doe', 'john@example.com', 'John', 'Doe'),
            ('sarah_smith', 'sarah@example.com', 'Sarah', 'Smith'),
            ('mike_johnson', 'mike@example.com', 'Mike', 'Johnson'),
            ('lisa_brown', 'lisa@example.com', 'Lisa', 'Brown'),
            ('david_wilson', 'david@example.com', 'David', 'Wilson'),
        ]
        
        for username, email, first_name, last_name in user_data:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username, email, 'password123')
                user.first_name = first_name
                user.last_name = last_name
                user.save()
                users.append(user)

        # Create categories
        categories_data = [
            {
                'name': 'Sea Moss Gel',
                'description': 'Ready-to-use Sea Moss gel, perfect for daily consumption',
                'slug': 'sea-moss-gel'
            },
            {
                'name': 'Sea Moss Powder', 
                'description': 'Fine powder form for easy mixing and versatile use',
                'slug': 'sea-moss-powder'
            },
            {
                'name': 'Sea Moss Capsules',
                'description': 'Convenient capsule form for easy supplementation',
                'slug': 'sea-moss-capsules'
            },
            {
                'name': 'Raw Sea Moss',
                'description': 'Pure, dried sea moss for making your own preparations',
                'slug': 'raw-sea-moss'
            }
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categories[cat_data['slug']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Create products
        products_data = [
            # Sea Moss Gel Products
            {
                'name': 'Premium Sea Moss Gel - Original',
                'category': 'sea-moss-gel',
                'product_type': 'gel',
                'sku': 'SM-GEL-0001',
                'description': 'Our flagship Sea Moss gel made from wildcrafted Sea Moss harvested from the pristine waters of Zanzibar. Rich in 92 essential minerals and perfect for daily consumption.',
                'price': 25.00,
                'compare_at_price': 30.00,
                'stock_quantity': 50,
                'weight': 500,
                'ingredients': '100% Wildcrafted Sea Moss (Eucheuma Cottonii), Spring Water',
                'benefits': 'Supports thyroid function, boosts immunity, promotes healthy digestion, enhances skin health, provides essential minerals',
                'usage_instructions': 'Take 1-2 tablespoons daily. Can be consumed directly or mixed into smoothies, teas, or other beverages.',
                'is_featured': True,
            },
            {
                'name': 'Sea Moss Gel with Bladderwrack',
                'category': 'sea-moss-gel',
                'product_type': 'gel',
                'sku': 'SM-GEL-0002',
                'description': 'Enhanced Sea Moss gel combined with Bladderwrack for maximum thyroid support and mineral content.',
                'price': 35.00,
                'stock_quantity': 30,
                'weight': 500,
                'ingredients': '85% Wildcrafted Sea Moss, 15% Bladderwrack, Spring Water',
                'benefits': 'Enhanced thyroid support, improved metabolism, increased energy levels, comprehensive mineral supplementation',
                'usage_instructions': 'Take 1-2 tablespoons daily, preferably in the morning.',
                'is_featured': True,
            },
            {
                'name': 'Sea Moss Gel - Tropical Blend',
                'category': 'sea-moss-gel',
                'product_type': 'gel',
                'sku': 'SM-GEL-0003',
                'description': 'Delicious tropical-flavored Sea Moss gel with natural fruit extracts from Zanzibar.',
                'price': 28.00,
                'stock_quantity': 40,
                'weight': 500,
                'ingredients': 'Wildcrafted Sea Moss, Spring Water, Natural Mango Extract, Natural Coconut Extract',
                'benefits': 'All benefits of Sea Moss with enhanced taste and tropical antioxidants',
                'usage_instructions': 'Take 1-2 tablespoons daily or use in smoothies for tropical flavor.',
            },

            # Sea Moss Powder Products
            {
                'name': 'Pure Sea Moss Powder',
                'category': 'sea-moss-powder',
                'product_type': 'powder',
                'sku': 'SM-POW-0001',
                'description': 'Ultra-fine Sea Moss powder for maximum versatility. Easy to mix into any drink or recipe.',
                'price': 20.00,
                'stock_quantity': 60,
                'weight': 250,
                'ingredients': '100% Wildcrafted Sea Moss Powder',
                'benefits': 'All Sea Moss benefits in convenient powder form, perfect for smoothies and cooking',
                'usage_instructions': 'Mix 1-2 teaspoons into smoothies, juices, soups, or baked goods.',
                'is_featured': True,
            },
            {
                'name': 'Organic Sea Moss Powder - Extra Fine',
                'category': 'sea-moss-powder',
                'product_type': 'powder',
                'sku': 'SM-POW-0002',
                'description': 'Extra-fine milled Sea Moss powder that dissolves completely in liquids.',
                'price': 24.00,
                'stock_quantity': 45,
                'weight': 250,
                'ingredients': '100% Organic Wildcrafted Sea Moss, Ultra-Fine Milled',
                'benefits': 'Superior mixability, faster absorption, all traditional Sea Moss benefits',
                'usage_instructions': 'Mix 1 teaspoon into any liquid. Stir well and enjoy.',
            },

            # Sea Moss Capsules
            {
                'name': 'Sea Moss Capsules - 60 Count',
                'category': 'sea-moss-capsules',
                'product_type': 'capsules',
                'sku': 'SM-CAP-0001',
                'description': 'Convenient Sea Moss capsules for daily supplementation. Each capsule contains 500mg of pure Sea Moss.',
                'price': 18.00,
                'stock_quantity': 80,
                'weight': 100,
                'ingredients': 'Sea Moss Powder (500mg per capsule), Vegetable Cellulose Capsule',
                'benefits': 'Convenient daily supplementation, precise dosing, no taste',
                'usage_instructions': 'Take 2 capsules daily with water, preferably with meals.',
                'is_featured': True,
            },
            {
                'name': 'Sea Moss Capsules - 120 Count',
                'category': 'sea-moss-capsules',
                'product_type': 'capsules',
                'sku': 'SM-CAP-0002',
                'description': 'Economy size Sea Moss capsules for long-term use. 2-month supply.',
                'price': 32.00,
                'compare_at_price': 36.00,
                'stock_quantity': 35,
                'weight': 200,
                'ingredients': 'Sea Moss Powder (500mg per capsule), Vegetable Cellulose Capsule',
                'benefits': 'Cost-effective, long-term supply, convenient daily use',
                'usage_instructions': 'Take 2 capsules daily with water, preferably with meals.',
            },

            # Raw Sea Moss
            {
                'name': 'Wildcrafted Raw Sea Moss - Gold',
                'category': 'raw-sea-moss',
                'product_type': 'raw',
                'sku': 'SM-RAW-0001',
                'description': 'Premium golden variety of raw Sea Moss, sun-dried and ready for preparation.',
                'price': 15.00,
                'stock_quantity': 70,
                'weight': 100,
                'ingredients': '100% Wildcrafted Golden Sea Moss (Eucheuma Cottonii)',
                'benefits': 'Make your own gel, maximum freshness, traditional preparation',
                'usage_instructions': 'Rinse thoroughly, soak for 12-24 hours, then blend with water to make gel.',
            },
            {
                'name': 'Wildcrafted Raw Sea Moss - Purple',
                'category': 'raw-sea-moss', 
                'product_type': 'raw',
                'sku': 'SM-RAW-0002',
                'description': 'Rare purple variety of Sea Moss with enhanced antioxidant properties.',
                'price': 22.00,
                'stock_quantity': 25,
                'weight': 100,
                'ingredients': '100% Wildcrafted Purple Sea Moss (Gracilaria)',
                'benefits': 'Higher antioxidant content, unique purple color, premium variety',
                'usage_instructions': 'Rinse thoroughly, soak for 12-24 hours, then blend with water to make gel.',
                'is_featured': True,
            },
            {
                'name': 'Raw Sea Moss Variety Pack',
                'category': 'raw-sea-moss',
                'product_type': 'raw',
                'sku': 'SM-RAW-0003',
                'description': 'Sample pack containing both golden and purple varieties of raw Sea Moss.',
                'price': 30.00,
                'stock_quantity': 20,
                'weight': 200,
                'ingredients': '50g Golden Sea Moss, 50g Purple Sea Moss',
                'benefits': 'Try both varieties, diverse mineral profile, great value',
                'usage_instructions': 'Prepare each variety separately or combine for unique blends.',
            }
        ]

        products = []
        for prod_data in products_data:
            category = categories[prod_data.pop('category')]
            product, created = Product.objects.get_or_create(
                name=prod_data['name'],
                defaults={
                    'category': category,
                    **prod_data
                }
            )
            products.append(product)
            if created:
                self.stdout.write(f'Created product: {product.name}')

                # Create variants for some products
                if 'gel' in product.product_type:
                    variants_data = [
                        {'name': '250ml', 'price': product.price - 10, 'weight': 250},
                        {'name': '500ml', 'price': product.price, 'weight': 500},
                        {'name': '1L', 'price': product.price + 15, 'weight': 1000},
                    ]
                elif 'powder' in product.product_type:
                    variants_data = [
                        {'name': '125g', 'price': product.price - 8, 'weight': 125},
                        {'name': '250g', 'price': product.price, 'weight': 250},
                        {'name': '500g', 'price': product.price + 12, 'weight': 500},
                    ]
                elif 'capsules' in product.product_type:
                    if '60' in product.name:
                        variants_data = [
                            {'name': '30 Capsules', 'price': product.price - 8, 'weight': 50},
                            {'name': '60 Capsules', 'price': product.price, 'weight': 100},
                        ]
                    else:
                        variants_data = [
                            {'name': '60 Capsules', 'price': 18, 'weight': 100},
                            {'name': '120 Capsules', 'price': product.price, 'weight': 200},
                        ]
                else:
                    variants_data = []

                for variant_data in variants_data:
                    variant_data['product'] = product
                    variant_data['stock_quantity'] = 50
                    ProductVariant.objects.create(**variant_data)

        # Create sample testimonials
        testimonials_data = [
            {
                'name': 'Sarah Mitchell',
                'email': 'sarah.m@example.com',
                'location': 'New York, USA',
                'title': 'Amazing Energy Boost!',
                'content': 'I\'ve been using CareCove Sea Moss gel for 3 months now and the difference in my energy levels is incredible. I feel more vibrant and healthy every day.',
                'rating': 5,
                'status': 'approved',
                'is_featured': True,
            },
            {
                'name': 'James Rodriguez',
                'email': 'james.r@example.com', 
                'location': 'California, USA',
                'title': 'Perfect for My Smoothies',
                'content': 'The Sea Moss powder mixes perfectly in my morning smoothies. Great quality and you can really taste the difference from other brands.',
                'rating': 5,
                'status': 'approved',
                'is_featured': True,
            },
            {
                'name': 'Fatuma Hassan',
                'email': 'fatuma.h@example.com',
                'location': 'Dar es Salaam, Tanzania', 
                'title': 'Authentic Zanzibar Quality',
                'content': 'As someone from Tanzania, I can confirm this is authentic, high-quality Sea Moss. The taste and texture are exactly what they should be.',
                'rating': 5,
                'status': 'approved',
                'is_featured': True,
            },
            {
                'name': 'Maria Santos',
                'email': 'maria.s@example.com',
                'location': 'London, UK',
                'title': 'Great for Skin Health',
                'content': 'I started taking the Sea Moss capsules for convenience and noticed my skin becoming clearer and more radiant within weeks.',
                'rating': 4,
                'status': 'approved',
            },
            {
                'name': 'Ahmed Al-Rashid',
                'email': 'ahmed.a@example.com',
                'location': 'Dubai, UAE',
                'title': 'Excellent Customer Service',
                'content': 'Not only is the product excellent, but the customer service is outstanding. Quick delivery and great communication.',
                'rating': 5,
                'status': 'approved',
            },
            {
                'name': 'Jennifer Parker',
                'email': 'jen.p@example.com',
                'location': 'Toronto, Canada',
                'title': 'Perfect for My Health Journey',
                'content': 'I\'ve tried many Sea Moss products, but CareCove\'s quality is unmatched. The tropical blend gel is my favorite!',
                'rating': 5,
                'status': 'approved',
            }
        ]

        for testimonial_data in testimonials_data:
            # Assign random user if available
            if users:
                testimonial_data['user'] = random.choice(users)
            
            testimonial, created = Testimonial.objects.get_or_create(
                email=testimonial_data['email'],
                defaults=testimonial_data
            )
            if created:
                self.stdout.write(f'Created testimonial: {testimonial.title}')

        # Create sample newsletter subscribers
        newsletter_emails = [
            'subscriber1@example.com',
            'subscriber2@example.com', 
            'subscriber3@example.com',
            'health.enthusiast@example.com',
            'wellness.lover@example.com',
        ]

        for email in newsletter_emails:
            newsletter, created = Newsletter.objects.get_or_create(
                email=email,
                defaults={'is_active': True}
            )
            if created:
                self.stdout.write(f'Created newsletter subscription: {email}')

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
        self.stdout.write(self.style.SUCCESS('Superuser created: admin / admin123'))
        self.stdout.write(self.style.SUCCESS(f'Created {len(products_data)} products'))
        self.stdout.write(self.style.SUCCESS(f'Created {len(testimonials_data)} testimonials'))
        self.stdout.write(self.style.SUCCESS('You can now run the server with: python manage.py runserver'))
