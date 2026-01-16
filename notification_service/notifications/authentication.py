from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import jwt
from django.conf import settings
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

class StatelessJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]
        try:
            # Use settings.SECRET_KEY which must match User Service
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expired')
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid Token: {e}")
            raise AuthenticationFailed('Invalid token')

        # Create a dummy user
        # Explicitly set is_authenticated = True just in case, though standard User object has it.
        # But since we are not saving, it's fine.
        user = User(id=payload.get('user_id'), username=f"user_{payload.get('user_id')}")
        user.token = payload 
        return (user, token)
