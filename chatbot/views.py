from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Q
import json
import time
import requests
import uuid
from .models import ChatSession, ChatMessage, ChatbotFAQ, QuickResponse
from shop.models import Product

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_or_create_session(request):
    """Get or create chat session for user"""
    session_token = request.session.get('chat_session_token')
    
    if session_token:
        try:
            chat_session = ChatSession.objects.get(
                session_token=session_token,
                is_active=True
            )
            return chat_session
        except ChatSession.DoesNotExist:
            pass
    
    # Create new session
    session_token = str(uuid.uuid4())
    chat_session = ChatSession.objects.create(
        user=request.user if request.user.is_authenticated else None,
        visitor_ip=get_client_ip(request),
        session_token=session_token
    )
    
    request.session['chat_session_token'] = session_token
    return chat_session

def find_faq_response(user_message):
    """Find matching FAQ response based on keywords"""
    user_message_lower = user_message.lower()
    
    # Get all active FAQs ordered by priority
    faqs = ChatbotFAQ.objects.filter(is_active=True).order_by('-priority')
    
    for faq in faqs:
        keywords = [keyword.strip().lower() for keyword in faq.keywords.split(',')]
        if any(keyword in user_message_lower for keyword in keywords):
            return faq.answer
    
    return None

def get_product_recommendations(query):
    """Get product recommendations based on query"""
    products = Product.objects.filter(
        Q(name__icontains=query) | 
        Q(description__icontains=query) | 
        Q(product_type__icontains=query),
        is_active=True
    )[:3]
    
    if products:
        recommendations = []
        for product in products:
            recommendations.append({
                'name': product.name,
                'price': str(product.price),
                'description': product.description[:100] + "..." if len(product.description) > 100 else product.description,
                'url': product.get_absolute_url(),
                'type': product.get_product_type_display()
            })
        return recommendations
    return None

@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    """Main chat API endpoint with LLM integration"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Get or create chat session
        chat_session = get_or_create_session(request)
        
        # Save user message
        user_msg = ChatMessage.objects.create(
            session=chat_session,
            message_type='user',
            content=user_message
        )
        
        start_time = time.time()
        
        # Check for FAQ response first
        faq_response = find_faq_response(user_message)
        if faq_response:
            response_time = int((time.time() - start_time) * 1000)
            bot_msg = ChatMessage.objects.create(
                session=chat_session,
                message_type='bot',
                content=faq_response,
                is_from_ai=False,
                response_time_ms=response_time
            )
            return JsonResponse({
                'message': faq_response,
                'message_id': bot_msg.id,
                'source': 'faq',
                'response_time': response_time
            })
        
        # Get product recommendations
        product_recommendations = get_product_recommendations(user_message)
        
        # Prepare context for LLM
        context = f"""You are CareCove's AI assistant, helping customers with Sea Moss products from Zanzibar, Tanzania.

Company Information:
- CareCove specializes in premium Sea Moss products
- Products are sourced from Zanzibar, Tanzania
- We offer: Sea Moss Gel, Sea Moss Powder, Sea Moss Capsules, and Raw Sea Moss
- WhatsApp contact: {settings.WHATSAPP_NUMBER}
- Our sea moss is natural, organic, and authentic

Customer Query: {user_message}

Guidelines:
1. Be helpful, friendly, and knowledgeable about sea moss benefits
2. Keep responses concise but informative
3. If asked about orders, shipping, or complex issues, suggest contacting WhatsApp
4. Focus on health benefits, usage instructions, and product information
5. Always maintain a professional tone
6. If you don't know something specific, be honest and refer to WhatsApp support

Please provide a helpful response to the customer's query."""

        # Add product recommendations to context if found
        if product_recommendations:
            context += f"\n\nRelevant Products Found:\n"
            for product in product_recommendations:
                context += f"- {product['name']} (${product['price']}) - {product['description']}\n"

        try:
            # Call LLM API
            response = requests.post(
                'https://apps.abacus.ai/v1/chat/completions',
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {settings.ABACUSAI_API_KEY}'
                },
                json={
                    'model': 'gpt-4.1-mini',
                    'messages': [
                        {'role': 'user', 'content': context}
                    ],
                    'max_tokens': 500,
                    'temperature': 0.7
                },
                timeout=30
            )
            
            if response.status_code == 200:
                ai_response = response.json()
                bot_response = ai_response['choices'][0]['message']['content'].strip()
                
                response_time = int((time.time() - start_time) * 1000)
                
                # Save bot response
                bot_msg = ChatMessage.objects.create(
                    session=chat_session,
                    message_type='bot',
                    content=bot_response,
                    is_from_ai=True,
                    response_time_ms=response_time
                )
                
                response_data = {
                    'message': bot_response,
                    'message_id': bot_msg.id,
                    'source': 'ai',
                    'response_time': response_time
                }
                
                # Add product recommendations if found
                if product_recommendations:
                    response_data['product_recommendations'] = product_recommendations
                
                return JsonResponse(response_data)
            else:
                raise Exception(f"LLM API error: {response.status_code}")
                
        except Exception as e:
            # Fallback response if LLM fails
            fallback_response = """Thank you for your message! I'm here to help you with CareCove's premium Sea Moss products from Zanzibar. 

For immediate assistance with orders, shipping, or detailed product information, please contact our team on WhatsApp at +255742604651.

Our Sea Moss products include:
- Sea Moss Gel (ready to use)
- Sea Moss Powder (versatile)
- Sea Moss Capsules (convenient)
- Raw Sea Moss (traditional)

How can I help you today?"""

            response_time = int((time.time() - start_time) * 1000)
            
            bot_msg = ChatMessage.objects.create(
                session=chat_session,
                message_type='bot',
                content=fallback_response,
                is_from_ai=False,
                response_time_ms=response_time
            )
            
            return JsonResponse({
                'message': fallback_response,
                'message_id': bot_msg.id,
                'source': 'fallback',
                'response_time': response_time,
                'error': str(e)
            })
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def get_quick_responses(request):
    """Get quick response buttons"""
    quick_responses = QuickResponse.objects.filter(is_active=True).order_by('order')
    responses_data = []
    
    for qr in quick_responses:
        responses_data.append({
            'id': qr.id,
            'title': qr.title,
            'description': qr.description,
            'action_type': qr.action_type,
            'action_data': qr.action_data,
            'icon': qr.icon
        })
    
    return JsonResponse({'quick_responses': responses_data})

@require_http_methods(["GET"])
def get_chat_history(request):
    """Get chat history for current session"""
    chat_session = get_or_create_session(request)
    messages = chat_session.messages.all()
    
    messages_data = []
    for msg in messages:
        messages_data.append({
            'id': msg.id,
            'type': msg.message_type,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat(),
            'is_from_ai': msg.is_from_ai
        })
    
    return JsonResponse({
        'messages': messages_data,
        'session_id': str(chat_session.session_id)
    })

@csrf_exempt
@require_http_methods(["POST"])
def transfer_to_whatsapp(request):
    """Transfer chat to WhatsApp"""
    try:
        chat_session = get_or_create_session(request)
        
        if not chat_session.transferred_to_whatsapp:
            chat_session.transferred_to_whatsapp = True
            chat_session.whatsapp_transfer_time = timezone.now()
            chat_session.save()
            
            # Create transfer message
            ChatMessage.objects.create(
                session=chat_session,
                message_type='whatsapp_transfer',
                content='Chat transferred to WhatsApp for personal assistance.'
            )
        
        whatsapp_url = f"https://wa.me/{settings.WHATSAPP_NUMBER.replace('+', '')}?text=Hello! I was chatting on your website and would like to continue our conversation here."
        
        return JsonResponse({
            'whatsapp_url': whatsapp_url,
            'message': 'Redirecting to WhatsApp for personal assistance...'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def end_chat_session(request):
    """End current chat session"""
    try:
        chat_session = get_or_create_session(request)
        chat_session.end_session()
        
        # Clear session
        if 'chat_session_token' in request.session:
            del request.session['chat_session_token']
        
        return JsonResponse({'message': 'Chat session ended successfully'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
