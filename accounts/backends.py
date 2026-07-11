"""
Custom authentication backend for T&TG Trade Corp.

Allows users to sign in with any of:
  - username  (case-insensitive)
  - email     (case-insensitive)
  - phone     (exact match)

Each field is tried independently so a collision between one user's
username and another user's phone/email can never silently block login.
"""
from django.contrib.auth.backends import ModelBackend
from .models import CustomUser


class FlexAuthBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        identifier = username.strip()
        user = None

        # 1. Username — case-insensitive
        if user is None:
            try:
                user = CustomUser.objects.get(username__iexact=identifier)
            except (CustomUser.DoesNotExist, CustomUser.MultipleObjectsReturned):
                user = None

        # 2. Email — case-insensitive
        if user is None:
            try:
                user = CustomUser.objects.get(email__iexact=identifier)
            except (CustomUser.DoesNotExist, CustomUser.MultipleObjectsReturned):
                user = None

        # 3. Phone — exact
        if user is None and identifier:
            try:
                user = CustomUser.objects.get(phone=identifier)
            except (CustomUser.DoesNotExist, CustomUser.MultipleObjectsReturned):
                user = None

        if user is None:
            # Dummy password check to prevent timing-based user enumeration
            CustomUser().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None
