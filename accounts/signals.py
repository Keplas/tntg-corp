from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver


@receiver(user_logged_out)
def save_cart_on_logout(sender, request, user, **kwargs):
    """Save session cart to user's DB profile before session is cleared."""
    if user and hasattr(user, 'saved_cart'):
        cart = request.session.get('cart', {})
        if cart:
            try:
                # Merge with existing saved cart
                existing = user.saved_cart or {}
                for pk, qty in cart.items():
                    existing[str(pk)] = existing.get(str(pk), 0) + qty
                user.saved_cart = existing
                user.save(update_fields=['saved_cart'])
            except Exception:
                pass


@receiver(user_logged_in)
def restore_cart_on_login(sender, request, user, **kwargs):
    """Restore saved cart from DB into session on login."""
    if user and hasattr(user, 'saved_cart'):
        try:
            saved = user.saved_cart or {}
            if saved:
                # Merge DB cart into current session cart
                session_cart = request.session.get('cart', {})
                for pk, qty in saved.items():
                    session_cart[str(pk)] = session_cart.get(str(pk), 0) + qty
                request.session['cart'] = session_cart
                # Clear saved cart after restoring
                user.saved_cart = {}
                user.save(update_fields=['saved_cart'])
        except Exception:
            pass
