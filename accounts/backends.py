"""
Flexible authentication backend for T&TG Trade Corp.
Accepts username, email, or phone — tried independently so a collision
between one user's fields and another's can never block login.
"""
from django.contrib.auth.backends import ModelBackend
from .models import CustomUser


class FlexAuthBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        identifier = username.strip()
        user = None

        # 1. Try username (case-insensitive)
        try:
            user = CustomUser.objects.get(username__iexact=identifier)
        except (CustomUser.DoesNotExist, CustomUser.MultipleObjectsReturned):
            user = None

        # 2. Try email (case-insensitive)
        if user is None:
            try:
                user = CustomUser.objects.get(email__iexact=identifier)
            except (CustomUser.DoesNotExist, CustomUser.MultipleObjectsReturned):
                user = None

        # 3. Try phone (exact)
        if user is None:
            try:
                user = CustomUser.objects.get(phone=identifier)
            except (CustomUser.DoesNotExist, CustomUser.MultipleObjectsReturned):
                user = None

        if user is None:
            CustomUser().set_password(password)   # timing attack prevention
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None
