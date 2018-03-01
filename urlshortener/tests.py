from django.test import TestCase, Client
from django.urls import reverse
from api.models import ShortUrl
from api.utils import toBase10,toBase62
import json
from unittest.mock import patch
from django.utils import timezone
import datetime

class CreateAndFetchTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        ShortUrl.objects.create(
            pk=15,
            target_url_desktop='http://google.com',
            desktop_redirects=0,
            target_url_tablet='http://facebook.com',
            tablet_redirects=0,
            target_url_mobile='http://twitter.com',
            mobile_redirects=0,
            created_at=timezone.now()
        )
        ShortUrl.objects.create(
            pk=16,
            target_url_desktop='http://instagram.com',
            desktop_redirects=0,
            target_url_tablet='http://youtube.com',
            tablet_redirects=0,
            target_url_mobile='http://twitch.com',
            mobile_redirects=0,
            created_at=timezone.now()
        )
    def setUp(self):
        self.client = Client()

    def test_get_all_links_correct(self):
        response = self.client.get(reverse('api:all'))
        # Status and headers
        self.assertEqual(response.status_code,200)
        self.assertTrue(response.has_header('Content-Type'))
        self.assertEqual(response.__getitem__('Content-Type'),'application/json')
        # Content
        json_response = response.json()
        self.assertEqual(len(json_response),1)
        self.assertTrue('result' in json_response)
        result = json_response['result']
        self.assertEqual(len(result),2)
        # Content - First
        first = result[0]
        self.assertTrue('shortened_url' in first)

        self.assertEqual(toBase10(first['shortened_url'].split('/')[-1]),15) # pk
        self.assertTrue('redirects' in first)
        redirects_first = first['redirects']
        self.assertTrue('mobile' in redirects_first and 'desktop' in redirects_first and 'tablet' in redirects_first)
        # Content - First - Mobile
        redirects_first_mobile = redirects_first['mobile']
        self.assertTrue('target' in redirects_first_mobile and 'num_redirects' in redirects_first_mobile)
        self.assertEqual(redirects_first_mobile['target'],'http://twitter.com')
        self.assertEqual(redirects_first_mobile['num_redirects'],0)
        # Content - First - Tablet
        redirects_first_tablet = redirects_first['tablet']
        self.assertTrue('target' in redirects_first_tablet and 'num_redirects' in redirects_first_tablet)
        self.assertEqual(redirects_first_tablet['target'],'http://facebook.com')
        self.assertEqual(redirects_first_tablet['num_redirects'],0)
        # Content - First - Desktop
        redirects_first_desktop = redirects_first['desktop']
        self.assertTrue('target' in redirects_first_desktop and 'num_redirects' in redirects_first_desktop)
        self.assertEqual(redirects_first_desktop['target'],'http://google.com')
        self.assertEqual(redirects_first_desktop['num_redirects'],0)

        # Content - Second
        first = result[1]
        self.assertTrue('shortened_url' in first)
        self.assertEqual(toBase10(first['shortened_url'].split('/')[-1]),16) # pk
        self.assertTrue('redirects' in first)
        redirects_first = first['redirects']
        self.assertTrue('mobile' in redirects_first and 'desktop' in redirects_first and 'tablet' in redirects_first)
        # Content - Second - Mobile
        redirects_first_mobile = redirects_first['mobile']
        self.assertTrue('target' in redirects_first_mobile and 'num_redirects' in redirects_first_mobile)
        self.assertEqual(redirects_first_mobile['target'],'http://twitch.com')
        self.assertEqual(redirects_first_mobile['num_redirects'],0)
        # Content - Second - Tablet
        redirects_first_tablet = redirects_first['tablet']
        self.assertTrue('target' in redirects_first_tablet and 'num_redirects' in redirects_first_tablet)
        self.assertEqual(redirects_first_tablet['target'],'http://youtube.com')
        self.assertEqual(redirects_first_tablet['num_redirects'],0)
        # Content - Second - Desktop
        redirects_first_desktop = redirects_first['desktop']
        self.assertTrue('target' in redirects_first_desktop and 'num_redirects' in redirects_first_desktop)
        self.assertEqual(redirects_first_desktop['target'],'http://instagram.com')
        self.assertEqual(redirects_first_desktop['num_redirects'],0)

    def test_create_new_link_wrong(self):

        # Wrong content type
        response = self.client.post(reverse('api:all'),{
        })
        self.assertEqual(response.status_code,400)
        content = response.json()
        self.assertTrue('status' in content)
        self.assertEqual(content['status'],'Content type must be application/json')

        # Wrong JSON
        response = self.client.post(reverse('api:all'),{
            'wrong'
        },content_type='application/json')
        self.assertEqual(response.status_code,400)
        content = response.json()
        self.assertTrue('status' in content)
        self.assertEqual(content['status'],'Error found in JSON')

        # Wrong JSON 2
        response = self.client.post(reverse('api:all'),{
            "wrong":"wrong"
        },content_type='application/json')
        self.assertEqual(response.status_code,400)
        content = response.json()
        self.assertTrue('status' in content)
        self.assertEqual(content['status'],'Error found in JSON')

        # Wrong structure
        response = self.client.post(reverse('api:all'),json.dumps({
            "wrong":"wrong"
        }),content_type='application/json')
        self.assertEqual(response.status_code,400)
        content = response.json()
        self.assertTrue('status' in content)
        self.assertEqual(content['status'],'Invalid request')

        # Wrong website
        response = self.client.post(reverse('api:all'),json.dumps({
            "target_url":"asdfasdf"
        }),content_type='application/json')
        self.assertEqual(response.status_code,400)
        content = response.json()
        self.assertTrue('status' in content)
        self.assertEqual(content['status'],'Invalid URL')


    def test_correct_creation(self):
        # Correct website
        # mock time now()
        with patch.object(timezone, 'now', return_value=datetime.datetime(2011, 1, 1,tzinfo=timezone.utc)) as mock_now:
            response = self.client.post(reverse('api:all'),json.dumps({
                "target_url":"jooraccess.com"
            }),content_type='application/json')
        self.assertEqual(response.status_code,200)
        # Check if new object exists (added http)
        self.assertTrue(ShortUrl.objects.filter(target_url_desktop='http://jooraccess.com').exists())
        # Check properties
        shortUrl = ShortUrl.objects.get(target_url_desktop='http://jooraccess.com')
        self.assertEqual(shortUrl.target_url_mobile,'http://jooraccess.com')
        self.assertEqual(shortUrl.target_url_tablet,'http://jooraccess.com')
        self.assertEqual(shortUrl.created_at, datetime.datetime(2011, 1, 1,tzinfo=timezone.utc))
        pk = shortUrl.pk
        # Check response
        shortened_url_id = toBase62(pk)
        content = response.json()
        self.assertTrue('result' in content)
        result = content['result']
        self.assertEqual(len(result),1)
        result = result[0]
        self.assertTrue('shortened_url' in result and 'redirects' in result and 'created_at' in result)
        self.assertEqual(result['shortened_url'].split('/')[-1], shortened_url_id)
        self.assertEqual(datetime.datetime.strptime(result['created_at'], "%Y-%m-%dT%H:%M:%SZ"),
                        datetime.datetime(2011,1,1))
        redirects = result['redirects']
        self.assertTrue('mobile' in redirects and 'tablet' in redirects and 'desktop' in redirects)
        # mobile
        mobile = redirects['mobile']
        self.assertTrue('num_redirects' in mobile and 'target' in mobile)
        self.assertEqual(mobile['num_redirects'],0)
        self.assertEqual(mobile['target'],'http://jooraccess.com')
        # tablet
        tablet = redirects['tablet']
        self.assertTrue('num_redirects' in tablet and 'target' in tablet)
        self.assertEqual(tablet['num_redirects'],0)
        self.assertEqual(tablet['target'],'http://jooraccess.com')
        # desktop
        desktop = redirects['desktop']
        self.assertTrue('num_redirects' in desktop and 'target' in desktop)
        self.assertEqual(desktop['num_redirects'],0)
        self.assertEqual(desktop['target'],'http://jooraccess.com')

        # correct website (but twice - only last one taken into account)
        with patch.object(timezone, 'now', return_value=datetime.datetime(2011, 1, 1,tzinfo=timezone.utc)) as mock_now:
            response = self.client.post(reverse('api:all'),json.dumps({
                "target_url":"google.com",
                "target_url":"jooraccess.com"
            }),content_type='application/json')
        self.assertEqual(response.status_code,200)
        # Check if new object exists (added http)
        self.assertTrue(ShortUrl.objects.filter(target_url_desktop='http://jooraccess.com').exists())
        # Check properties
        shortUrl = ShortUrl.objects.get(target_url_desktop='http://jooraccess.com')
        self.assertEqual(shortUrl.target_url_mobile,'http://jooraccess.com')
        self.assertEqual(shortUrl.target_url_tablet,'http://jooraccess.com')
        self.assertEqual(shortUrl.created_at, datetime.datetime(2011, 1, 1,tzinfo=timezone.utc))
        pk = shortUrl.pk
        # Check response
        shortened_url_id = toBase62(pk)
        content = response.json()
        self.assertTrue('result' in content)
        result = content['result']
        self.assertEqual(len(result),1)
        result = result[0]
        self.assertTrue('shortened_url' in result and 'redirects' in result and 'created_at' in result)
        self.assertEqual(result['shortened_url'].split('/')[-1], shortened_url_id)
        self.assertEqual(datetime.datetime.strptime(result['created_at'], "%Y-%m-%dT%H:%M:%SZ"),
                        datetime.datetime(2011,1,1))
        redirects = result['redirects']
        self.assertTrue('mobile' in redirects and 'tablet' in redirects and 'desktop' in redirects)
        # mobile
        mobile = redirects['mobile']
        self.assertTrue('num_redirects' in mobile and 'target' in mobile)
        self.assertEqual(mobile['num_redirects'],0)
        self.assertEqual(mobile['target'],'http://jooraccess.com')
        # tablet
        tablet = redirects['tablet']
        self.assertTrue('num_redirects' in tablet and 'target' in tablet)
        self.assertEqual(tablet['num_redirects'],0)
        self.assertEqual(tablet['target'],'http://jooraccess.com')
        # desktop
        desktop = redirects['desktop']
        self.assertTrue('num_redirects' in desktop and 'target' in desktop)
        self.assertEqual(desktop['num_redirects'],0)
        self.assertEqual(desktop['target'],'http://jooraccess.com')

    def test_repeated_creation(self):
        # The same request should lead to the same shortened_url_id
        response = self.client.post(reverse('api:all'),json.dumps({
            "target_url":"jooraccess.com"
        }),content_type='application/json')
        self.assertEqual(response.status_code,200)
        shortUrl = ShortUrl.objects.get(target_url_desktop='http://jooraccess.com')
        shortened_url_id = toBase62(shortUrl.pk)
        content = response.json()
        self.assertEqual(shortened_url_id,content['result'][0]['shortened_url'].split('/')[-1])
        response_second = self.client.post(reverse('api:all'),json.dumps({
            "target_url":"jooraccess.com"
        }),content_type='application/json')
        self.assertEqual(response.status_code,200)
        content_second = response_second.json()
        self.assertEqual(shortened_url_id,content_second['result'][0]['shortened_url'].split('/')[-1])
        # with http added, the same
        response_third = self.client.post(reverse('api:all'),json.dumps({
            "target_url":"http://jooraccess.com"
        }),content_type='application/json')
        self.assertEqual(response.status_code,200)
        # Check properties
        content_third = response_third.json()
        self.assertEqual(shortened_url_id,content_third['result'][0]['shortened_url'].split('/')[-1])
        # with https added, it should be different
        response_fourth = self.client.post(reverse('api:all'),json.dumps({
            "target_url":"https://jooraccess.com"
        }),content_type='application/json')
        self.assertEqual(response.status_code,200)
        # Check properties
        content_fourth = response_fourth.json()
        self.assertNotEqual(shortened_url_id,content_fourth['result'][0]['shortened_url'].split('/')[-1])

    def test_wrong_http_methods(self):
        response = self.client.put(reverse('api:all'),json.dumps({
            "target_url":"jooraccess.com"
        }),content_type='application/json')
        self.assertEqual(response.status_code,405)
        response = self.client.delete(reverse('api:all'),json.dumps({
            "target_url":"jooraccess.com"
        }),content_type='application/json')
        self.assertEqual(response.status_code,405)

class ConfigureTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        ShortUrl.objects.create(
            pk=15,
            target_url_desktop='http://google.com',
            desktop_redirects=0,
            target_url_tablet='http://facebook.com',
            tablet_redirects=0,
            target_url_mobile='http://twitter.com',
            mobile_redirects=0,
            created_at=timezone.now()
        )
        ShortUrl.objects.create(
            pk=16,
            target_url_desktop='http://instagram.com',
            desktop_redirects=0,
            target_url_tablet='http://youtube.com',
            tablet_redirects=0,
            target_url_mobile='http://twitch.com',
            mobile_redirects=0,
            created_at=timezone.now()
        )
    def setUp(self):
        self.client = Client()

    def test_configure_redirects_correct(self):
        # change desktop
        response = self.client.post(reverse('api:configure_view',kwargs={'shortened_url_id':toBase62(15)}),json.dumps({
            "target_url_desktop":"jooraccess.com"
        }),content_type='application/json')
        self.assertEqual(response.status_code,200)
        # Check if new object exists (added http)
        self.assertTrue(ShortUrl.objects.filter(target_url_desktop='http://jooraccess.com').exists())
        # Check properties
        shortUrl = ShortUrl.objects.get(target_url_desktop='http://jooraccess.com')
        self.assertEqual(shortUrl.target_url_mobile,'http://twitter.com')
        self.assertEqual(shortUrl.target_url_tablet,'http://facebook.com')
        pk = shortUrl.pk
        # Check response
        shortened_url_id = toBase62(pk)
        content = response.json()
        self.assertTrue('result' in content)
        result = content['result']
        self.assertEqual(len(result),1)
        result = result[0]
        self.assertTrue('shortened_url' in result and 'redirects' in result and 'created_at' in result)
        self.assertEqual(result['shortened_url'].split('/')[-1], shortened_url_id)
        redirects = result['redirects']
        self.assertTrue('mobile' in redirects and 'tablet' in redirects and 'desktop' in redirects)
        # mobile
        mobile = redirects['mobile']
        self.assertTrue('num_redirects' in mobile and 'target' in mobile)
        self.assertEqual(mobile['num_redirects'],0)
        self.assertEqual(mobile['target'],'http://twitter.com')
        # tablet
        tablet = redirects['tablet']
        self.assertTrue('num_redirects' in tablet and 'target' in tablet)
        self.assertEqual(tablet['num_redirects'],0)
        self.assertEqual(tablet['target'],'http://facebook.com')
        # desktop
        desktop = redirects['desktop']
        self.assertTrue('num_redirects' in desktop and 'target' in desktop)
        self.assertEqual(desktop['num_redirects'],0)
        self.assertEqual(desktop['target'],'http://jooraccess.com')

        # repeated element, should only get the last
        response = self.client.post(reverse('api:configure_view',kwargs={'shortened_url_id':toBase62(15)}),json.dumps({
            "target_url_desktop":"twitter.com",
            "target_url_desktop":"google.com"
        }),content_type='application/json')
        self.assertEqual(response.status_code,200)
        self.assertTrue(ShortUrl.objects.filter(target_url_desktop='http://google.com').exists())
        # Check properties
        shortUrl = ShortUrl.objects.get(target_url_desktop='http://google.com')
        pk = shortUrl.pk
        # Check response
        shortened_url_id = toBase62(pk)
        content = response.json()
        self.assertTrue('result' in content)
        result = content['result']
        self.assertEqual(len(result),1)
        result = result[0]
        self.assertTrue('shortened_url' in result and 'redirects' in result and 'created_at' in result)
        self.assertEqual(result['shortened_url'].split('/')[-1], shortened_url_id)
        redirects = result['redirects']
        self.assertTrue('mobile' in redirects and 'tablet' in redirects and 'desktop' in redirects)
        # mobile
        desktop = redirects['desktop']
        self.assertTrue('num_redirects' in desktop and 'target' in desktop)
        self.assertEqual(desktop['num_redirects'],0)
        self.assertEqual(desktop['target'],'http://google.com')

        # change mobile
        response = self.client.post(reverse('api:configure_view',kwargs={'shortened_url_id':toBase62(15)}),json.dumps({
            "target_url_mobile":"jooraccess.com"
        }),content_type='application/json')
        content = response.json()
        result = content['result']
        result = result[0]
        redirects = result['redirects']
        # mobile
        mobile = redirects['mobile']
        self.assertTrue('num_redirects' in mobile and 'target' in mobile)
        self.assertEqual(mobile['num_redirects'],0)
        self.assertEqual(mobile['target'],'http://jooraccess.com')
        # tablet
        tablet = redirects['tablet']
        self.assertTrue('num_redirects' in tablet and 'target' in tablet)
        self.assertEqual(tablet['num_redirects'],0)
        self.assertEqual(tablet['target'],'http://facebook.com')
        # desktop
        desktop = redirects['desktop']
        self.assertTrue('num_redirects' in desktop and 'target' in desktop)
        self.assertEqual(desktop['num_redirects'],0)
        self.assertEqual(desktop['target'],'http://google.com')

        # change tablet
        response = self.client.post(reverse('api:configure_view',kwargs={'shortened_url_id':toBase62(15)}),json.dumps({
            "target_url_tablet":"jooraccess.com"
        }),content_type='application/json')
        content = response.json()
        result = content['result']
        result = result[0]
        redirects = result['redirects']
        # mobile
        mobile = redirects['mobile']
        self.assertTrue('num_redirects' in mobile and 'target' in mobile)
        self.assertEqual(mobile['num_redirects'],0)
        self.assertEqual(mobile['target'],'http://jooraccess.com')
        # tablet
        tablet = redirects['tablet']
        self.assertTrue('num_redirects' in tablet and 'target' in tablet)
        self.assertEqual(tablet['num_redirects'],0)
        self.assertEqual(tablet['target'],'http://jooraccess.com')
        # desktop
        desktop = redirects['desktop']
        self.assertTrue('num_redirects' in desktop and 'target' in desktop)
        self.assertEqual(desktop['num_redirects'],0)
        self.assertEqual(desktop['target'],'http://google.com')

        # change 2 at the same time
        response = self.client.post(reverse('api:configure_view',kwargs={'shortened_url_id':toBase62(15)}),json.dumps({
            "target_url_tablet":"google.com",
            "target_url_desktop":"google.com"
        }),content_type='application/json')
        content = response.json()
        result = content['result']
        result = result[0]
        redirects = result['redirects']
        # mobile
        mobile = redirects['mobile']
        self.assertTrue('num_redirects' in mobile and 'target' in mobile)
        self.assertEqual(mobile['num_redirects'],0)
        self.assertEqual(mobile['target'],'http://jooraccess.com')
        # tablet
        tablet = redirects['tablet']
        self.assertTrue('num_redirects' in tablet and 'target' in tablet)
        self.assertEqual(tablet['num_redirects'],0)
        self.assertEqual(tablet['target'],'http://google.com')
        # desktop
        desktop = redirects['desktop']
        self.assertTrue('num_redirects' in desktop and 'target' in desktop)
        self.assertEqual(desktop['num_redirects'],0)
        self.assertEqual(desktop['target'],'http://google.com')

        # change 3 at the same time
        response = self.client.post(reverse('api:configure_view',kwargs={'shortened_url_id':toBase62(15)}),json.dumps({
            "target_url_tablet":"twitter.com",
            "target_url_desktop":"instagram.com",
            "target_url_mobile":"facebook.com"
        }),content_type='application/json')
        content = response.json()
        result = content['result']
        result = result[0]
        redirects = result['redirects']
        # mobile
        mobile = redirects['mobile']
        self.assertTrue('num_redirects' in mobile and 'target' in mobile)
        self.assertEqual(mobile['num_redirects'],0)
        self.assertEqual(mobile['target'],'http://facebook.com')
        # tablet
        tablet = redirects['tablet']
        self.assertTrue('num_redirects' in tablet and 'target' in tablet)
        self.assertEqual(tablet['num_redirects'],0)
        self.assertEqual(tablet['target'],'http://twitter.com')
        # desktop
        desktop = redirects['desktop']
        self.assertTrue('num_redirects' in desktop and 'target' in desktop)
        self.assertEqual(desktop['num_redirects'],0)
        self.assertEqual(desktop['target'],'http://instagram.com')

    def test_configure_redirects_wrong(self):
        # Wrong content type
        response = self.client.post(reverse('api:configure_view',kwargs={'shortened_url_id':toBase62(15)}),{
        })
        self.assertEqual(response.status_code,400)
        content = response.json()
        self.assertTrue('status' in content)
        self.assertEqual(content['status'],'Content type must be application/json')

        # Wrong JSON
        response = self.client.post(reverse('api:configure_view',kwargs={'shortened_url_id':toBase62(15)}),{
            'wrong'
        },content_type='application/json')
        self.assertEqual(response.status_code,400)
        content = response.json()
        self.assertTrue('status' in content)
        self.assertEqual(content['status'],'Error found in JSON')

        # Wrong JSON 2
        response = self.client.post(reverse('api:configure_view',kwargs={'shortened_url_id':toBase62(15)}),{
            "wrong":"wrong"
        },content_type='application/json')
        self.assertEqual(response.status_code,400)
        content = response.json()
        self.assertTrue('status' in content)
        self.assertEqual(content['status'],'Error found in JSON')

        # Wrong structure
        response = self.client.post(reverse('api:configure_view',kwargs={'shortened_url_id':toBase62(15)}),json.dumps({
            "wrong":"wrong"
        }),content_type='application/json')
        self.assertEqual(response.status_code,400)
        content = response.json()
        self.assertTrue('status' in content)
        self.assertEqual(content['status'],'Invalid request')

        # Wrong URL
        response = self.client.post(reverse('api:configure_view',kwargs={'shortened_url_id':toBase62(15)}),json.dumps({
            "target_url_desktop":"asdfasdf"
        }),content_type='application/json')
        self.assertEqual(response.status_code,400)
        content = response.json()
        self.assertTrue('status' in content)
        self.assertEqual(content['status'],'Invalid URL asdfasdf')

        # One right URL one wrong URL
        response = self.client.post(reverse('api:configure_view',kwargs={'shortened_url_id':toBase62(15)}),json.dumps({
            "target_url_mobile":"google.com",
            "target_url_desktop":"asdfasdf",
        }),content_type='application/json')
        self.assertEqual(response.status_code,400)
        content = response.json()
        self.assertTrue('status' in content)
        self.assertEqual(content['status'],'Invalid URL asdfasdf')



        # Not found shortened_url
        response = self.client.post(reverse('api:configure_view',kwargs={'shortened_url_id':toBase62(25)}),json.dumps({
            "target_url_desktop":"asdfasdf"
        }),content_type='application/json')
        self.assertEqual(response.status_code,404)
        content = response.json()
        self.assertTrue('status' in content)
        self.assertEqual(content['status'],'Not found')

        # Invalid shortened_url
        response = self.client.post('/shortened_url/ljkañsdf@',json.dumps({
            "target_url_desktop":"asdfasdf"
        }),content_type='application/json')
        self.assertEqual(response.status_code,404)
        self.assertEqual(response.content,b'<h1>Not Found</h1><p>The requested URL /shortened_url/ljka\xc3\xb1sdf@ was not found on this server.</p>')

        # Not found shortened_url
        response = self.client.post('/shortened_url/',json.dumps({
            "target_url_desktop":"asdfasdf"
        }),content_type='application/json')
        self.assertEqual(response.status_code,404)
        self.assertEqual(response.content,b'<h1>Not Found</h1><p>The requested URL /shortened_url/ was not found on this server.</p>')

    def test_get_shortened_url_info(self):
        response = self.client.get(reverse('api:configure_view',kwargs={'shortened_url_id':toBase62(15)}))
        self.assertEqual(response.status_code,200)
        # check correct info
        content = response.json()
        self.assertTrue('result' in content)
        result = content['result']
        self.assertEqual(len(result),1)
        result = result[0]
        self.assertTrue('shortened_url' in result and 'redirects' in result and 'created_at' in result)
        self.assertEqual(result['shortened_url'].split('/')[-1], toBase62(15))
        redirects = result['redirects']
        self.assertTrue('mobile' in redirects and 'tablet' in redirects and 'desktop' in redirects)
        # mobile
        mobile = redirects['mobile']
        self.assertTrue('num_redirects' in mobile and 'target' in mobile)
        self.assertEqual(mobile['num_redirects'],0)
        self.assertEqual(mobile['target'],'http://twitter.com')
        # tablet
        tablet = redirects['tablet']
        self.assertTrue('num_redirects' in tablet and 'target' in tablet)
        self.assertEqual(tablet['num_redirects'],0)
        self.assertEqual(tablet['target'],'http://facebook.com')
        # desktop
        desktop = redirects['desktop']
        self.assertTrue('num_redirects' in desktop and 'target' in desktop)
        self.assertEqual(desktop['num_redirects'],0)
        self.assertEqual(desktop['target'],'http://google.com')

        response = self.client.get(reverse('api:configure_view',kwargs={'shortened_url_id':toBase62(25)}))
        self.assertEqual(response.status_code,404)
        response = self.client.get('/shortened_url/lkjar@')
        self.assertEqual(response.status_code,404)


class RedirectTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        ShortUrl.objects.create(
            pk=15,
            target_url_desktop='http://google.com',
            desktop_redirects=0,
            target_url_tablet='http://facebook.com',
            tablet_redirects=0,
            target_url_mobile='http://twitter.com',
            mobile_redirects=0,
            created_at=timezone.now()
        )


    def test_redirect(self):
        # check before redirects
        # check num redirects
        shortUrl = ShortUrl.objects.get(pk=15)
        self.assertEqual(shortUrl.desktop_redirects,0)
        self.assertEqual(shortUrl.mobile_redirects,0)
        self.assertEqual(shortUrl.tablet_redirects,0)
        # check if API is refreshed as well
        response = self.client.get(reverse('api:all'))
        # Content
        json_response = response.json()
        self.assertEqual(len(json_response),1)
        self.assertTrue('result' in json_response)
        result = json_response['result']
        self.assertEqual(len(result),1)
        # Content - First
        first = result[0]
        self.assertTrue('shortened_url' in first)
        self.assertEqual(toBase10(first['shortened_url'].split('/')[-1]),15) # pk
        self.assertTrue('redirects' in first)
        redirects_first = first['redirects']
        self.assertTrue('mobile' in redirects_first and 'desktop' in redirects_first and 'tablet' in redirects_first)
        # Content - First - Mobile
        redirects_first_mobile = redirects_first['mobile']
        self.assertTrue('target' in redirects_first_mobile and 'num_redirects' in redirects_first_mobile)
        self.assertEqual(redirects_first_mobile['target'],'http://twitter.com')
        self.assertEqual(redirects_first_mobile['num_redirects'],0)
        # Content - First - Tablet
        redirects_first_tablet = redirects_first['tablet']
        self.assertTrue('target' in redirects_first_tablet and 'num_redirects' in redirects_first_tablet)
        self.assertEqual(redirects_first_tablet['target'],'http://facebook.com')
        self.assertEqual(redirects_first_tablet['num_redirects'],0)
        # Content - First - Desktop
        redirects_first_desktop = redirects_first['desktop']
        self.assertTrue('target' in redirects_first_desktop and 'num_redirects' in redirects_first_desktop)
        self.assertEqual(redirects_first_desktop['target'],'http://google.com')
        self.assertEqual(redirects_first_desktop['num_redirects'],0)

        # ubuntu firefox user (from user_agents library)
        self.client = Client('Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:15.0) Gecko/20100101 Firefox/15.0.1')
        response = self.client.get('/%s'%(toBase62(15)),follow=True)
        last_url, status_code = response.redirect_chain[-1]
        self.assertEqual(last_url,'http://google.com')
        # iphone user agent (from user_agents library)
        self.client = Client(HTTP_USER_AGENT='Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3')
        response = self.client.get('/%s'%(toBase62(15)),follow=True)
        last_url, status_code = response.redirect_chain[-1]
        self.assertEqual(last_url,'http://twitter.com')
        # ipad user agent (from user_agents library)
        self.client = Client(HTTP_USER_AGENT='Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10')
        response = self.client.get('/%s'%(toBase62(15)),follow=True)
        last_url, status_code = response.redirect_chain[-1]
        self.assertEqual(last_url,'http://facebook.com')
        # unknown user goes to desktop redirect
        self.client = Client()
        response = self.client.get('/%s'%(toBase62(15)),follow=True)
        last_url, status_code = response.redirect_chain[-1]
        self.assertEqual(last_url,'http://google.com')

        # check num redirects
        shortUrl = ShortUrl.objects.get(pk=15)
        self.assertEqual(shortUrl.desktop_redirects,2)
        self.assertEqual(shortUrl.mobile_redirects,1)
        self.assertEqual(shortUrl.tablet_redirects,1)
        # check if API is refreshed as well
        response = self.client.get(reverse('api:all'))
        # Status and headers
        self.assertEqual(response.status_code,200)
        self.assertTrue(response.has_header('Content-Type'))
        self.assertEqual(response.__getitem__('Content-Type'),'application/json')
        # Content
        json_response = response.json()
        self.assertEqual(len(json_response),1)
        self.assertTrue('result' in json_response)
        result = json_response['result']
        self.assertEqual(len(result),1)
        # Content - First
        first = result[0]
        self.assertTrue('shortened_url' in first)
        self.assertEqual(toBase10(first['shortened_url'].split('/')[-1]),15) # pk
        self.assertTrue('redirects' in first)
        redirects_first = first['redirects']
        self.assertTrue('mobile' in redirects_first and 'desktop' in redirects_first and 'tablet' in redirects_first)
        # Content - First - Mobile
        redirects_first_mobile = redirects_first['mobile']
        self.assertTrue('target' in redirects_first_mobile and 'num_redirects' in redirects_first_mobile)
        self.assertEqual(redirects_first_mobile['target'],'http://twitter.com')
        self.assertEqual(redirects_first_mobile['num_redirects'],1)
        # Content - First - Tablet
        redirects_first_tablet = redirects_first['tablet']
        self.assertTrue('target' in redirects_first_tablet and 'num_redirects' in redirects_first_tablet)
        self.assertEqual(redirects_first_tablet['target'],'http://facebook.com')
        self.assertEqual(redirects_first_tablet['num_redirects'],1)
        # Content - First - Desktop
        redirects_first_desktop = redirects_first['desktop']
        self.assertTrue('target' in redirects_first_desktop and 'num_redirects' in redirects_first_desktop)
        self.assertEqual(redirects_first_desktop['target'],'http://google.com')
        self.assertEqual(redirects_first_desktop['num_redirects'],2)

    def test_redirect_wrong(self):
        # does not exist
        self.client = Client()
        response = self.client.get('/%s'%(toBase62(25)),follow=True)
        self.assertEqual(response.status_code,404)
        # invalid
        self.client = Client()
        response = self.client.get('/sdf@',follow=True)
        self.assertEqual(response.status_code,404)
        # continuing
        self.client = Client()
        response = self.client.get('/%s/more'%(toBase62(25)),follow=True)
        self.assertEqual(response.status_code,404)
        # wrong method
        response = self.client.post('/%s'%(toBase62(15)),follow=True)
        self.assertEqual(response.status_code,400)
