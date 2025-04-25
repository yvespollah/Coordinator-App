import jwt
from django.conf import settings
import datetime

def generate_jwt(volunteer_id):
    payload = {
        'volunteer_id': str(volunteer_id),
        'exp': datetime.datetime.now() + datetime.timedelta(days=1),
        'iat': datetime.datetime.now()
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token
