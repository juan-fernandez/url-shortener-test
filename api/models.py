from django.db import models
from .utils import toBase62
from django.db import transaction

class ShortUrl(models.Model):
    created_at = models.DateTimeField('created_at', null=False, blank=False)
    target_url_desktop = models.URLField(max_length=200,null=True)
    desktop_redirects = models.IntegerField(default=0)
    target_url_tablet = models.URLField(max_length=200,null=True)
    tablet_redirects = models.IntegerField(default=0)
    target_url_mobile = models.URLField(max_length=200,null=True)
    mobile_redirects = models.IntegerField(default=0)
