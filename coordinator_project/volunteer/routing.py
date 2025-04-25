from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/volunteers/(?P<volunteer_id>[0-9a-f-]+)/$', consumers.VolunteerConsumer.as_asgi()),
]
