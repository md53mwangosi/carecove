import requests
import json
import logging
from django.conf import settings
import pdfkit
import os

logger = logging.getLogger(__name__)

# Configure pdfkit to use the wkhtmltopdf executable path
# For Vercel/Linux deployment, wkhtmltopdf is not available, so we'll use xhtml2pdf instead
try:
    # Try to find wkhtmltopdf in system PATH first
    import shutil
    wkhtmltopdf_path = shutil.which('wkhtmltopdf')
    if wkhtmltopdf_path:
        pdfkit_config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
    else:
        # Fallback - disable pdfkit for serverless environments like Vercel
        pdfkit_config = None
        logger.warning("wkhtmltopdf not found, PDF generation will use xhtml2pdf instead")
except Exception as e:
    pdfkit_config = None
    logger.warning(f"Could not configure pdfkit: {e}. Using xhtml2pdf instead.")

from xhtml2pdf import pisa
from io import BytesIO

# Replace the generate_invoice_pdf function to use xhtml2pdf

from django.template.loader import render_to_string

def generate_invoice_pdf(order, order_items, output_path):
    # Render the invoice HTML with embedded CSS
    html_content = render_to_string('cart/pre_payment_invoice_print.html', {
        'order': order,
        'order_items': order_items,
    })

    # Generate PDF using xhtml2pdf
    try:
        with open(output_path, 'wb') as output_file:
            pisa_status = pisa.CreatePDF(
                src=html_content,
                dest=output_file,
                encoding='UTF-8'
            )
        if pisa_status.err:
            raise Exception(f"Error generating PDF: {pisa_status.err}")
    except Exception as e:
        logger.error(f"Failed to generate PDF: {e}")
        raise

class PesapalService:
    """Integrates with Pesapal payment gateway."""

    def __init__(self):
        # Hardcoded credentials for testing
        self.consumer_key = 'ngW+UEcnDhltUc5fxPfrCD987xMh3Lx8'
        self.consumer_secret = "q27RChYs5UkypdcNYKzuUw460Dg="
        self.demo = settings.PESAPAL_DEMO
        
        # Set the base URL based on the environment
        if self.demo:
            self.base_url = 'https://cybqa.pesapal.com/pesapalv3'
        else:
            self.base_url = 'https://pay.pesapal.com/v3'
        
        print(f"Initialized PesapalService with key: {self.consumer_key}")
        print(f"Secret: {self.consumer_secret}")
        print(f"Demo mode: {self.demo}")
        print(f"Base URL: {self.base_url}")

    def get_access_token(self):
        """Get access token from Pesapal API."""
        url = f"{self.base_url}/api/Auth/RequestToken"
        
        # Format exactly as per Pesapal documentation
        data = {
            "consumer_key": self.consumer_key,
            "consumer_secret": self.consumer_secret
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        try:
            print(f"Requesting Pesapal token with URL: {url}")
            print(f"Request data: {json.dumps(data)}")
            print(f"Headers: {headers}")
            
            # Make the request
            response = requests.post(url, json=data, headers=headers)
            print(f"Pesapal token response status: {response.status_code}")
            print(f"Pesapal token response: {response.text}")
            
            # Process the response
            if response.status_code == 200:
                try:
                    result = response.json()
                    
                    # Check if the response has the expected structure
                    if 'token' in result:
                        token = result.get('token')
                        print(f"Successfully obtained Pesapal token: {token[:10]}...")
                        return token
                    else:
                        print(f"Unexpected response structure: {result}")
                        # Check if there's an error message
                        if 'error' in result:
                            error_msg = result.get('error', {}).get('message', 'Unknown error')
                            print(f"Pesapal error message: {error_msg}")
                        print("Could not find token in response")
                        return None
                except Exception as e:
                    print(f"Error parsing JSON response: {e}")
                    return None
            else:
                print(f"Failed to get token. Status code: {response.status_code}")
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_msg = error_data['error'].get('message', 'Unknown error')
                        print(f"Pesapal error message: {error_msg}")
                except Exception as json_error:
                    print(f"Error parsing error response: {json_error}")
                return None
        except Exception as e:
            print(f"Error getting Pesapal token: {e}")
            return None

    def register_ipn_url(self, ipn_url):
        """Register IPN URL with Pesapal."""
        token = self.get_access_token()
        if not token:
            print("Failed to register IPN URL: Could not obtain access token")
            return None
        
        url = f"{self.base_url}/api/URLSetup/RegisterIPN"
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        
        data = {
            'url': ipn_url,
            'ipn_notification_type': 'GET'
        }
        
        try:
            print(f"Registering IPN URL: {ipn_url}")
            response = requests.post(url, json=data, headers=headers)
            print(f"IPN registration response status: {response.status_code}")
            print(f"IPN registration response: {response.text}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    ipn_id = result.get('ipn_id')
                    print(f"Successfully registered IPN URL. IPN ID: {ipn_id}")
                    return ipn_id
                except Exception as e:
                    print(f"Error parsing IPN registration response: {e}")
                    return None
            else:
                print(f"Failed to register IPN URL. Status code: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error registering IPN URL: {e}")
            return None

    def create_order(self, order_data):
        """Create a payment order with Pesapal."""
        token = self.get_access_token()
        if not token:
            print("Failed to create order: Could not obtain access token")
            return None
        
        url = f"{self.base_url}/api/Transactions/SubmitOrderRequest"
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        
        # Prepare the order data according to Pesapal documentation
        pesapal_order = {
            'id': order_data.get('merchant_reference'),
            'currency': order_data.get('currency', 'TZS'),
            'amount': float(order_data.get('amount')),
            'description': order_data.get('description', 'Order payment'),
            'callback_url': order_data.get('callback_url'),
            'notification_id': order_data.get('ipn_id', ''),
            'billing_address': {
                'email_address': order_data.get('email', ''),
                'phone_number': order_data.get('phone_number', ''),
                'country_code': order_data.get('country_code', 'TZ'),
                'first_name': order_data.get('first_name', ''),
                'middle_name': order_data.get('middle_name', ''),
                'last_name': order_data.get('last_name', ''),
                'line_1': order_data.get('address', ''),
                'line_2': '',
                'city': order_data.get('city', ''),
                'state': order_data.get('state', ''),
                'postal_code': order_data.get('postal_code', ''),
                'zip_code': order_data.get('zip_code', '')
            }
        }
        
        try:
            print(f"Creating Pesapal order for reference: {order_data.get('merchant_reference')}")
            print(f"Order data: {json.dumps(pesapal_order)}")
            
            response = requests.post(url, json=pesapal_order, headers=headers)
            print(f"Order creation response status: {response.status_code}")
            print(f"Order creation response: {response.text}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    
                    # Extract the required information from the response
                    order_tracking_id = result.get('order_tracking_id')
                    merchant_reference = result.get('merchant_reference')
                    redirect_url = result.get('redirect_url')
                    
                    if order_tracking_id and redirect_url:
                        print(f"Successfully created Pesapal order. Tracking ID: {order_tracking_id}")
                        return {
                            'order_tracking_id': order_tracking_id,
                            'merchant_reference': merchant_reference,
                            'redirect_url': redirect_url,
                            'pesapal_order_id': result.get('pesapal_order_id', '')
                        }
                    else:
                        print(f"Incomplete order creation response: {result}")
                        return None
                except Exception as e:
                    print(f"Error parsing order creation response: {e}")
                    return None
            else:
                print(f"Failed to create order. Status code: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error creating Pesapal order: {e}")
            return None

    def get_transaction_status(self, order_tracking_id):
        """Get transaction status from Pesapal."""
        token = self.get_access_token()
        if not token:
            print("Failed to get transaction status: Could not obtain access token")
            return None
        
        url = f"{self.base_url}/api/Transactions/GetTransactionStatus?orderTrackingId={order_tracking_id}"
        
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        
        try:
            print(f"Getting transaction status for order tracking ID: {order_tracking_id}")
            response = requests.get(url, headers=headers)
            print(f"Transaction status response status: {response.status_code}")
            print(f"Transaction status response: {response.text}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"Successfully retrieved transaction status: {result}")
                    return result
                except Exception as e:
                    print(f"Error parsing transaction status response: {e}")
                    return None
            else:
                print(f"Failed to get transaction status. Status code: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error getting transaction status: {e}")
            return None

    def verify_payment(self, order_tracking_id):
        """Verify payment status and return a simplified result."""
        transaction_status = self.get_transaction_status(order_tracking_id)

        if not transaction_status:
            print(f"Failed to verify payment for order tracking ID: {order_tracking_id}")
            return {
                'success': False,
                'status': 'error',
                'message': 'Failed to get transaction status'
            }

        # Extract the payment status
        status = transaction_status.get('payment_status_description', '')
        status_code = transaction_status.get('payment_status_code', '')

        # Map Pesapal status codes to simplified statuses
        if status_code == '0':
            simplified_status = 'completed'
            success = True
            message = 'Payment completed successfully'
        elif status_code == '1':
            simplified_status = 'failed'
            success = False
            message = 'Payment failed'
        elif status_code == '2':
            simplified_status = 'reversed'
            success = False
            message = 'Payment was reversed'
        else:
            simplified_status = 'pending'
            success = False
            message = 'Payment is pending or in an unknown state'

        print(f"Payment verification result for order tracking ID {order_tracking_id}: {simplified_status}")

        return {
            'success': success,
            'status': simplified_status,
            'message': message,
            'transaction_details': transaction_status
        }

    def submit_order(self, order_id, currency, amount, description, callback_url, notification_url,
                     billing_email, billing_phone, billing_first_name, billing_last_name, line_items=None):
        """Submit order to Pesapal for payment processing."""
        token = self.get_access_token()
        if not token:
            print("Failed to submit order: Could not obtain access token")
            return None

        url = f"{self.base_url}/api/Transactions/SubmitOrderRequest"

        # Prepare the order data
        order_data = {
            "id": order_id,
            "currency": currency,
            "amount": amount,
            "description": description,
            "callback_url": callback_url,
            "redirect_mode": "",
            "notification_id": notification_url,
            "branch": "CareCove Store",
            "billing_address": {
                "email_address": billing_email,
                "phone_number": billing_phone,
                "country_code": "",
                "first_name": billing_first_name,
                "middle_name": "",
                "last_name": billing_last_name,
                "line_1": "Pesapal Limited",
                "line_2": "",
                "city": "",
                "state": "",
                "postal_code": "",
                "zip_code": ""
            }
        }

        # Add line items if provided
        if line_items:
            order_data["line_items"] = line_items

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        try:
            print(f"Submitting order to Pesapal: {json.dumps(order_data, indent=2)}")
            response = requests.post(url, json=order_data, headers=headers)
            print(f"Submit order response status: {response.status_code}")
            print(f"Submit order response: {response.text}")

            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"Successfully submitted order: {result}")
                    return {
                        'status': '200',
                        'order_tracking_id': result.get('order_tracking_id'),
                        'redirect_url': result.get('redirect_url'),
                        'error': None
                    }
                except Exception as e:
                    print(f"Error parsing submit order response: {e}")
                    return {
                        'status': 'error',
                        'error': str(e)
                    }
            else:
                try:
                    error_data = response.json()
                    error_message = error_data.get('error', {}).get('message', 'Unknown error')
                    print(f"Failed to submit order: {error_message}")
                    return {
                        'status': str(response.status_code),
                        'error': error_message
                    }
                except:
                    return {
                        'status': str(response.status_code),
                        'error': f'HTTP {response.status_code}'
                    }
        except Exception as e:
            print(f"Error submitting order: {e}")
            logger.error(f"Error submitting order: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }