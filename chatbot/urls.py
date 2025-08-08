from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('api/chat/', views.chat_api, name='chat_api'),
    path('api/quick-responses/', views.get_quick_responses, name='quick_responses'),
    path('api/chat-history/', views.get_chat_history, name='chat_history'),
    path('api/transfer-whatsapp/', views.transfer_to_whatsapp, name='transfer_whatsapp'),
    path('api/end-session/', views.end_chat_session, name='end_session'),

    # Added for backward compatibility to fix 404 error
    path('quick-responses/', views.get_quick_responses, name='quick_responses_no_api'),
]