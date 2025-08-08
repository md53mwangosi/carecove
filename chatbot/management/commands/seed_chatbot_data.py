
from django.core.management.base import BaseCommand
from chatbot.models import ChatbotFAQ, QuickResponse

class Command(BaseCommand):
    help = 'Seed chatbot with initial FAQ and quick response data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding chatbot data...')
        
        # Create FAQ entries
        faqs = [
            {
                'question': 'What is Sea Moss and what are its benefits?',
                'keywords': 'sea moss, benefits, health, nutrients, minerals',
                'answer': '''Sea Moss is a nutrient-rich seaweed harvested from the pristine waters of Zanzibar, Tanzania. It contains 92 of the 102 minerals your body needs, including:

• Iodine for thyroid health
• Iron for energy and blood health
• Calcium for strong bones
• Potassium for heart health
• Magnesium for muscle function

Benefits include improved digestion, boosted immunity, enhanced skin health, and increased energy levels.''',
                'category': 'benefits',
                'priority': 10
            },
            {
                'question': 'How do I use Sea Moss Gel?',
                'keywords': 'gel, how to use, usage, instructions, dosage',
                'answer': '''Sea Moss Gel is ready to use! Here's how:

• Take 1-2 tablespoons daily
• Add to smoothies, juices, or water
• Mix into yogurt or oatmeal
• Use as a face mask for skin benefits
• Store in refrigerator for up to 3 weeks

Start with 1 tablespoon daily and gradually increase as your body adjusts.''',
                'category': 'usage',
                'priority': 9
            },
            {
                'question': 'What are the different types of Sea Moss products?',
                'keywords': 'products, types, gel, powder, capsules, raw',
                'answer': '''We offer 4 main types of Sea Moss products:

• **Sea Moss Gel**: Ready-to-use, fresh gel form
• **Sea Moss Powder**: Versatile powder for mixing
• **Sea Moss Capsules**: Convenient daily supplements
• **Raw Sea Moss**: Traditional dried seaweed for DIY preparation

Each form offers the same nutritional benefits - choose based on your preference and lifestyle!''',
                'category': 'products',
                'priority': 8
            },
            {
                'question': 'How long does shipping take?',
                'keywords': 'shipping, delivery, time, when, arrive',
                'answer': '''Shipping times depend on your location:

• Local Zanzibar: 1-2 business days
• Tanzania mainland: 3-5 business days
• East Africa: 5-10 business days
• International: 10-21 business days

All orders are processed within 24 hours. You'll receive tracking information once your order ships.''',
                'category': 'shipping',
                'priority': 7
            },
            {
                'question': 'Is Sea Moss safe for everyone?',
                'keywords': 'safe, side effects, allergies, pregnant, children',
                'answer': '''Sea Moss is generally safe for most people, but consider these points:

• Start with small amounts to assess tolerance
• Consult your doctor if pregnant or breastfeeding
• Those with thyroid conditions should consult healthcare providers
• People with iodine allergies should avoid
• Children can use smaller doses

Always consult with healthcare professionals if you have concerns.''',
                'category': 'general',
                'priority': 6
            },
            {
                'question': 'How do I track my order?',
                'keywords': 'track, order, status, where, package',
                'answer': '''To track your order:

• Check your email for tracking information
• Use the tracking number on our shipping partner's website
• Contact us via WhatsApp for order updates
• Orders are processed within 24 hours

If you can't find your tracking info, please contact our support team on WhatsApp.''',
                'category': 'orders',
                'priority': 5
            }
        ]

        for faq_data in faqs:
            faq, created = ChatbotFAQ.objects.get_or_create(
                question=faq_data['question'],
                defaults=faq_data
            )
            if created:
                self.stdout.write(f'Created FAQ: {faq.question}')
            else:
                self.stdout.write(f'FAQ already exists: {faq.question}')

        # Create Quick Response buttons
        quick_responses = [
            {
                'title': 'Sea Moss Benefits',
                'description': 'Learn about the health benefits of sea moss',
                'action_type': 'faq',
                'icon': 'fas fa-heart',
                'order': 1
            },
            {
                'title': 'How to Use',
                'description': 'Usage instructions for sea moss products',
                'action_type': 'faq',
                'icon': 'fas fa-question-circle',
                'order': 2
            },
            {
                'title': 'Product Types',
                'description': 'Different types of sea moss products available',
                'action_type': 'product_info',
                'icon': 'fas fa-shopping-bag',
                'order': 3
            },
            {
                'title': 'Shipping Info',
                'description': 'Information about shipping and delivery',
                'action_type': 'faq',
                'icon': 'fas fa-shipping-fast',
                'order': 4
            },
            {
                'title': 'Track Order',
                'description': 'Check your order status',
                'action_type': 'order_status',
                'icon': 'fas fa-package',
                'order': 5
            },
            {
                'title': 'Talk to Human',
                'description': 'Connect with our support team on WhatsApp',
                'action_type': 'whatsapp',
                'icon': 'fab fa-whatsapp',
                'order': 6
            }
        ]

        for qr_data in quick_responses:
            qr, created = QuickResponse.objects.get_or_create(
                title=qr_data['title'],
                defaults=qr_data
            )
            if created:
                self.stdout.write(f'Created Quick Response: {qr.title}')
            else:
                self.stdout.write(f'Quick Response already exists: {qr.title}')

        self.stdout.write(self.style.SUCCESS('Successfully seeded chatbot data!'))
