from rest_framework.authtoken.models import Token
# from synos.settings import GOOGLE_API_KEY,MAPBOX_API_KEY
from django.conf import settings

def userToken(request):
    if request.user.is_authenticated:
        token, created = Token.objects.get_or_create(user=request.user)
        return {'userToken': token.key , 'googleApiKey': settings.GOOGLE_API_KEY, 'mapboxApiKey': settings.MAPBOX_API_KEY } 
    else:
        return {'googleApiKey': settings.GOOGLE_API_KEY , 'mapboxApiKey': settings.MAPBOX_API_KEY } 