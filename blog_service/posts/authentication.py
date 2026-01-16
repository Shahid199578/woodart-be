from rest_framework import authentication, exceptions
from django.conf import settings
import jwt
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import UntypedToken

class StatelessJWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        header = request.META.get('HTTP_AUTHORIZATION')
        if not header:
            return None

        try:
            raw_token = header.split()[1]
            # Verify signature using the shared SECRET_KEY
            # simplejwt's UntypedToken validates the signature and expiration
            UntypedToken(raw_token)
            
            # Decode manually to get payload
            decoded_data = jwt.decode(raw_token, settings.SECRET_KEY, algorithms=["HS256"])
            
            # Create a transient user object (not saved to DB)
            user = User(id=decoded_data.get('user_id'), username=decoded_data.get('email', 'admin'))
            # user.is_authenticated is True by default for User instances
            # user.is_authenticated = True # This causes an error because it is a read-only property
            
            # Attach the token payload to the user object for permission checks
            user.token = decoded_data
            
            return (user, None)
        except (jwt.DecodeError, IndexError, jwt.ExpiredSignatureError):
            raise exceptions.AuthenticationFailed('Invalid token')
        except Exception as e:
            # print(f"Auth Error: {e}")
            return None
