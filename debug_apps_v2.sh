#!/bin/bash

# Improved debug script to test each custom app individually
# This will help identify which app is causing import failures

APPS=("shop" "cart" "accounts" "testimonials" "newsletter" "chatbot" "admin_panel")
SETTINGS_FILE="/home/ubuntu/carecove_debug/carecove/settings.py"
URLS_FILE="/home/ubuntu/carecove_debug/carecove/urls.py"
DEBUG_REPORT="/home/ubuntu/carecove_debug/debug_report_v2.txt"

echo "=== Django App Debugging Report V2 ===" > $DEBUG_REPORT
echo "Date: $(date)" >> $DEBUG_REPORT
echo "Project: CareCove Django Application" >> $DEBUG_REPORT
echo "" >> $DEBUG_REPORT

echo "Step 1: Basic Django configuration test - PASSED" >> $DEBUG_REPORT
echo "" >> $DEBUG_REPORT

# Function to reset to minimal configuration
reset_to_minimal() {
    # Reset INSTALLED_APPS to minimal
    sed -i 's/^    '\''shop'\'',/    # '\''shop'\'',/' $SETTINGS_FILE
    sed -i 's/^    '\''cart'\'',/    # '\''cart'\'',/' $SETTINGS_FILE
    sed -i 's/^    '\''accounts'\'',/    # '\''accounts'\'',/' $SETTINGS_FILE
    sed -i 's/^    '\''testimonials'\'',/    # '\''testimonials'\'',/' $SETTINGS_FILE
    sed -i 's/^    '\''newsletter'\'',/    # '\''newsletter'\'',/' $SETTINGS_FILE
    sed -i 's/^    '\''chatbot'\'',/    # '\''chatbot'\'',/' $SETTINGS_FILE
    sed -i 's/^    '\''admin_panel'\'',/    # '\''admin_panel'\'',/' $SETTINGS_FILE
    
    # Reset URLs to minimal
    sed -i 's|^    path('\''admin-panel/|    # path('\''admin-panel/|' $URLS_FILE
    sed -i 's|^    path('\'\'\'|    # path('\'\'\'|' $URLS_FILE
    sed -i 's|^    path('\''cart/|    # path('\''cart/|' $URLS_FILE
    sed -i 's|^    path('\''accounts/|    # path('\''accounts/|' $URLS_FILE
    sed -i 's|^    path('\''testimonials/|    # path('\''testimonials/|' $URLS_FILE
    sed -i 's|^    path('\''newsletter/|    # path('\''newsletter/|' $URLS_FILE
    sed -i 's|^    path('\''chatbot/|    # path('\''chatbot/|' $URLS_FILE
}

# Test each app individually
for app in "${APPS[@]}"; do
    echo "=== Testing app: $app ===" | tee -a $DEBUG_REPORT
    
    # Reset to minimal configuration first
    reset_to_minimal
    
    # Add only this app to INSTALLED_APPS
    sed -i "s/# '$app',/'$app',/" $SETTINGS_FILE
    
    # Test with just the app added to INSTALLED_APPS
    echo "Testing $app in INSTALLED_APPS only..." | tee -a $DEBUG_REPORT
    python manage.py check 2>&1 | tee -a $DEBUG_REPORT
    
    if [ $? -eq 0 ]; then
        echo "✓ $app: INSTALLED_APPS test PASSED" | tee -a $DEBUG_REPORT
        
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
        fi
        
    else
        echo "✗ $app: INSTALLED_APPS test FAILED" | tee -a $DEBUG_REPORT
    fi
    
    echo "" >> $DEBUG_REPORT
done

# Reset to minimal configuration at the end
reset_to_minimal

echo "=== Debugging Complete ===" | tee -a $DEBUG_REPORT
echo "Check debug_report_v2.txt for detailed results" | tee -a $DEBUG_REPORT
