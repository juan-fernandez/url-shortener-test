from django.urls import path,register_converter
from .views import ShortUrlsView,ConfigureUrlView
from django.views.decorators.csrf import csrf_exempt
from .utils import ShortenedUrlMatcher


register_converter(ShortenedUrlMatcher, 'shorturl')

app_name='api'
urlpatterns = [
    path(r'shortened_url/<shorturl:shortened_url_id>',csrf_exempt(ConfigureUrlView.as_view()),name='configure_view'),
    path(r'', csrf_exempt(ShortUrlsView.as_view()),name='all'),
]
