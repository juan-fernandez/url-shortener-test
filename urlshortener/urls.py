from django.conf.urls import include
from django.urls import path,register_converter
from api.views import ShortUrlRedirect
from api.utils import ShortenedUrlMatcher



register_converter(ShortenedUrlMatcher, 'shorturl')

urlpatterns = [
    path('<shorturl:shortened_url>/',ShortUrlRedirect.as_view(),name='shortened_url'),
    path('api/v1/',include('api.urls')),
]
