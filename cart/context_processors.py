
from .models import Cart

def cart(request):
    """Add cart information to all templates."""
    cart_total_items = 0
    cart_total_price = 0
    cart_obj = None
    
    try:
        if request.user.is_authenticated:
            cart_obj = Cart.objects.get(user=request.user)
        else:
            if request.session.session_key:
                cart_obj = Cart.objects.get(session_key=request.session.session_key)
        
        if cart_obj:
            cart_total_items = cart_obj.total_items
            cart_total_price = cart_obj.total_price
    except Cart.DoesNotExist:
        pass
    
    return {
        'cart_total_items': cart_total_items,
        'cart_total_price': cart_total_price,
        'cart': cart_obj,
    }
