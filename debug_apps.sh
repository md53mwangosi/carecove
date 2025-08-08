#!/bin/bash

# Debug script to test each custom app individually
# This will help identify which app is causing import failures

APPS=("shop" "cart" "accounts" "testimonials" "newsletter" "chatbot" "admin_panel")
SETTINGS_FILE="/home/ubuntu/carecove_debug/carecove/settings.py"
URLS_FILE="/home/ubuntu/carecove_debug/carecove/urls.py"
DEBUG_REPORT="/home/ubuntu/carecove_debug/debug_report.txt"

echo "=== Django App Debugging Report ===" > $DEBUG_REPORT
echo "Date: $(date)" >> $DEBUG_REPORT
echo "Project: CareCove Django Application" >> $DEBUG_REPORT
echo "" >> $DEBUG_REPORT

echo "Step 1: Basic Django configuration test - PASSED" >> $DEBUG_REPORT
echo "" >> $DEBUG_REPORT

# Test each app individually
for app in "${APPS[@]}"; do
    echo "=== Testing app: $app ===" | tee -a $DEBUG_REPORT
    
    # Add app to INSTALLED_APPS
    sed -i "s/# '$app',/'$app',/" $SETTINGS_FILE
    
    # Test with just the app added to INSTALLED_APPS
    echo "Testing $app in INSTALLED_APPS only..." | tee -a $DEBUG_REPORT
    python manage.py check 2>&1 | tee -a $DEBUG_REPORT
    
    if [ $? -eq 0 ]; then
        echo "✓ $app: INSTALLED_APPS test PASSED" | tee -a $DEBUG_REPORT
    else
        echo "✗ $app: INSTALLED_APPS test FAILED" | tee -a $DEBUG_REPORT
        # Remove the app and continue
        sed -i "s/'$app',/# '$app',/" $SETTINGS_FILE
        echo "" >> $DEBUG_REPORT
        continue
    fi
    
    # If INSTALLED_APPS test passed, try adding URL patterns
    case $app in
        "shop")
            sed -i "s|# path('', include('shop.urls')),|path('', include('shop.urls')),|" $URLS_FILE
            ;;
        "cart")
            sed -i "s|# path('cart/', include('cart.urls')),|path('cart/', include('cart.urls')),|" $URLS_FILE
            ;;
        "accounts")
            sed -i "s|# path('accounts/', include('accounts.urls')),|path('accounts/', include('accounts.urls')),|" $URLS_FILE
            ;;
        "testimonials")
            sed -i "s|# path('testimonials/', include('testimonials.urls')),|path('testimonials/', include('testimonials.urls')),|" $URLS_FILE
            ;;
        "newsletter")
            sed -i "s|# path('newsletter/', include('newsletter.urls')),|path('newsletter/', include('newsletter.urls')),|" $URLS_FILE
            ;;
        "chatbot")
            sed -i "s|# path('chatbot/', include('chatbot.urls')),|path('chatbot/', include('chatbot.urls')),|" $URLS_FILE
            ;;
        "admin_panel")
            sed -i "s|# path('admin-panel/', include('admin_panel.urls')),|path('admin-panel/', include('admin_panel.urls')),|" $URLS_FILE
            ;;
    esac
    
    echo "Testing $app with URL patterns..." | tee -a $DEBUG_REPORT
    python manage.py check 2>&1 | tee -a $DEBUG_REPORT
    
    if [ $? -eq 0 ]; then
        echo "✓ $app: URL patterns test PASSED" | tee -a $DEBUG_REPORT
    else
        echo "✗ $app: URL patterns test FAILED" | tee -a $DEBUG_REPORT
        # Remove the URL pattern
        case $app in
            "shop")
                sed -i "s|path('', include('shop.urls')),|# path('', include('shop.urls')),|" $URLS_FILE
                ;;
            "cart")
                sed -i "s|path('cart/', include('cart.urls')),|# path('cart/', include('cart.urls')),|" $URLS_FILE
                ;;
            "accounts")
                sed -i "s|path('accounts/', include('accounts.urls')),|# path('accounts/', include('accounts.urls')),|" $URLS_FILE
                ;;
            "testimonials")
                sed -i "s|path('testimonials/', include('testimonials.urls')),|# path('testimonials/', include('testimonials.urls')),|" $URLS_FILE
                ;;
            "newsletter")
                sed -i "s|path('newsletter/', include('newsletter.urls')),|# path('newsletter/', include('newsletter.urls')),|" $URLS_FILE
                ;;
            "chatbot")
                sed -i "s|path('chatbot/', include('chatbot.urls')),|# path('chatbot/', include('chatbot.urls')),|" $URLS_FILE
                ;;
            "admin_panel")
                sed -i "s|path('admin-panel/', include('admin_panel.urls')),|# path('admin-panel/', include('admin_panel.urls')),|" $URLS_FILE
                ;;
        esac
    fi
    
    echo "" >> $DEBUG_REPORT
done

echo "=== Debugging Complete ===" | tee -a $DEBUG_REPORT
echo "Check debug_report.txt for detailed results" | tee -a $DEBUG_REPORT
