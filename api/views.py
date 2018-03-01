from .models import ShortUrl
from django.views import View
from django.http import JsonResponse, Http404
from .serializers import serialize_urls, validate_url_request, validate_configure_request
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from .utils import toBase10
from django.utils import timezone

# creates a target url to all devices
class ShortUrlsView(View):

    def get(self,request):
        data = serialize_urls(ShortUrl.objects.all())
        return JsonResponse({'result':data})

    def post(self,request):
        validation = validate_url_request(request)
        if validation['code'] is not 200:
            return JsonResponse({
                'status': validation['status'],
            },status=validation['code'])
        target_url = validation['data']['target_url']

        try:
            link = ShortUrl.objects.get(target_url_desktop=target_url,
                                        target_url_tablet=target_url,
                                        target_url_mobile=target_url)
        except ObjectDoesNotExist:
            # it may happen that the same URL conf has different PK in the database
            link = ShortUrl.objects.create(target_url_desktop=target_url,
                                            target_url_tablet=target_url,
                                            target_url_mobile=target_url,
                                            created_at=timezone.now())



        data = serialize_urls([link])
        return JsonResponse({'result':data},status=200)

class ShortUrlRedirect(View):

    def get(self,request,shortened_url):
        try:
            link = ShortUrl.objects.get(pk=toBase10(shortened_url))
        except ObjectDoesNotExist:
            raise Http404()
        # get user device and increase count
        if request.user_agent.is_mobile:
            link.mobile_redirects = link.mobile_redirects + 1
            link.save()
            return redirect(link.target_url_mobile,permanent=True)
        elif request.user_agent.is_tablet:
            link.tablet_redirects = link.tablet_redirects + 1
            link.save()
            return redirect(link.target_url_tablet,permanent=True)
        else:
            link.desktop_redirects = link.desktop_redirects + 1
            link.save()
            return redirect(link.target_url_desktop,permanent=True)


class ConfigureUrlView(View):
    def get(self,request,shortened_url):
        try:
            link = ShortUrl.objects.get(pk=toBase10(shortened_url))
        except ObjectDoesNotExist:
            return JsonResponse({
                'status': 'Not found',
            },status=404)
        data = serialize_urls([link])
        return JsonResponse({'result':data},status=200)
    def post(self,request,shortened_url):
        try:
            link = ShortUrl.objects.get(pk=toBase10(shortened_url))
        except ObjectDoesNotExist:
            return JsonResponse({
                'status': 'Not found',
                },status=404)
        validation = validate_configure_request(request)
        if validation['code'] is not 200:
            return JsonResponse({
                'status': validation['status'],
            },status=validation['code'])
        for key in validation['data']:
            setattr(link,key,validation['data'][key])
            link.save()
        data = serialize_urls([link])
        return JsonResponse({'result':data},status=validation['code'])
