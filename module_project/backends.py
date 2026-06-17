from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class PhoneNumberBackend(ModelBackend):
    """Аутентификация по телефону, email или username"""
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        
        # Ищем по телефону (в профиле), email или username
        try:
            user = User.objects.get(
                Q(profile__phone_number=username) | 
                Q(email=username) | 
                Q(username=username)
            )
        except User.DoesNotExist:
            return None
        
        if user.check_password(password):
            return user
        
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None