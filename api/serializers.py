import json
from django.core.exceptions import ValidationError
from .utils import toBase62
from urllib.parse import urlparse
from django.core.validators import URLValidator

def serialize_urls(urls):
    return [{
            'created_at':obj.created_at,
            'shortened_url': toBase62(obj.pk),
            'redirects': {
                'mobile': {
                    'target': obj.target_url_mobile,
                    'num_redirects': obj.mobile_redirects
                },
                'tablet': {
                    'target': obj.target_url_tablet,
                    'num_redirects': obj.tablet_redirects
                },
                'desktop': {
                    'target': obj.target_url_desktop,
                    'num_redirects': obj.desktop_redirects
                }
            }} for obj in urls]

def validate_website_url(website):
    msg = "Cannot validate this website: %s" % website
    validate = URLValidator(message=msg)
    try:
        validate(website)
    except ValidationError:
        o = urlparse(website)
        if o.path:
            path = o.path
            while path.endswith('/'):
                path = path[:-1]
            path = "http://"+path # http assumed (google does the same)
            validate(path)
            return path
        else:
            raise ValidationError(message=msg)
    return website


# return status
def validate_url_request(request):
    validation = {}
    validation['code'] = 200

    if request.content_type != 'application/json':
        validation['status'] = 'Content type must be application/json'
        validation['code'] = 400
        return validation
    try:
        parsedData = json.loads(request.body.decode('utf-8'))
    except ValueError:
        validation['status'] = 'Error found in JSON'
        validation['code'] = 400
        return validation
    if len(parsedData.keys()) > 1 or not 'target_url' in parsedData:
        validation['status'] = 'Invalid request'
        validation['code'] = 400
        return validation
    try:
        website = validate_website_url(parsedData['target_url'])
    except ValidationError:
        validation['status'] = 'Invalid URL'
        validation['code'] = 400
        return validation

    validation['data'] = {'target_url':website}
    return validation


# return status
def validate_configure_request(request):
    validation = {}
    validation['code'] = 200

    if request.content_type != 'application/json':
        validation['status'] = 'Content type must be application/json'
        validation['code'] = 400
        return validation
    try:
        parsedData = json.loads(request.body.decode('utf-8'))
    except ValueError:
        validation['status'] = 'Error found in JSON'
        validation['code'] = 400
        return validation

    if not ('target_url_desktop' in parsedData
        or 'target_url_mobile' in parsedData
        or 'target_url_tablet' in parsedData):
        validation['status'] = 'Invalid request'
        validation['code'] = 400
        return validation

    for key in parsedData:
        try:
            website = validate_website_url(parsedData[key])
            parsedData[key] = website
        except ValidationError:
            validation['status'] = 'Invalid URL %s'%parsedData[key]
            validation['code'] = 400
            return validation

    validation['data'] =parsedData
    return validation
