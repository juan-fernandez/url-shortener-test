Simple URL shortener developed with Django 2.0 and Python 3

## Requirements
- Python3


## Setup instructions
Clone the repository:
```
git clone git@github.com:juan-fernandez/url-shortener-test.git
```
Create your virtual environment: 
```
python3 -m venv <path_to_your_venv>
```
Activate your virtual environment:
```
source <path_to_your_venv>/bin/activate
```
Install the requirements: 
```
pip install -r url-shortener-test/requirements.txt
```
Migrate your database:
```
python3 manage.py migrate
```

And you are ready to go! 

## Run the tests
```
python3 manage.py test
```

## Run the server
```
python3 manage.py runserver <your_server_root_url>
```
Make sure your SITE_DOMAIN setting in urlshortener/settings.py is correctly set. This will be used for your responses. 

```
...
SITE_DOMAIN = '<your_server_root_url>'
...
```


## API description 
This API is designed to process a given URL and return a shortened version. The server will handle requests to the shortened version of the URLs and redirect to the desired URL.  

### Example

https://www.youtube.com/watch?v=FlsCjmMhFmw > <your_server_root_url>/<shortened_url_id>

The shortened_url_id is a unique identifier of this link.

The API allows the user to:
1. Submit any URL and get a shortened URL back
2. Get a list of all exiting shortened URLs, with time since creation and number of redirects per device type
3. Get information of a given shortened URL
4. Configure a shortened URL to redirect to different targets based on the device type (mobile, tablet and desktop)
5. Be redirected to the desired URL when navigating to a shortened URL


### 1. Submit a new URL 
HTTP POST /api/v1/ with body
```
{
  "target_url":"<desired_url>"
}
```
Response:
```
{
  "result": [
    {
      "shortened_url": "<your_server_root_url>/<shortened_url_id>",
      "created_at": "<creation_date_time>",
      "redirects": {
        "desktop": {
          "target": "<desired_url>",
          "num_redirects": 0
        },
        "tablet": {
          "target": "<desired_url>",
          "num_redirects": 0
        },
        "mobile": {
          "target": "<desired_url>",
          "num_redirects": 0
        }
      }
    }
  ],
}
```
### 2. Get a list of all shortened URLs
HTTP GET /api/v1/ 

### 3. Get info of an specific shortened URL
HTTP GET /api/v1/shortened_url/{shortened_url_id}

Response:
```
{
  "result": [
    {
      "shortened_url": "<your_server_root_url>/<shortened_url_id>",
      "created_at": "<creation_date_time>",
      "redirects": {
        "desktop": {
          "target": "<desired_url>",
          "num_redirects": 0
        },
        "tablet": {
          "target": "<desired_url>",
          "num_redirects": 0
        },
        "mobile": {
          "target": "<desired_url>",
          "num_redirects": 0
        }
      }
    }
  ],
}
```
### 4. Modify a shortened URL
Modify a shortened_url to act differently depending on the device.

HTTP POST /api/v1/shortened_url/{shortened_url_id} with body:
```
{
  "target_url_<type_of_device>":"<desired_url>",
  ... (may include up to 3 keys, for tablet, mobile and desktop)
}
```
For example, for changing tablet and mobile:

HTTP POST /api/v1/shortened_url/{shortened_url_id} with body:
```
{
  "target_url_tablet":"<desired_url_tablet>",
  "target_url_mobile":"<desired_url_mobile>"
}
```
The response is: 
```
{
  "result": [
    {
      "shortened_url": "<your_server_root_url>/<shortened_url_id>",
      "created_at": "<creation_date_time>",
      "redirects": {
        "desktop": {
          "target": "<desired_url>",
          "num_redirects": 0
        },
        "tablet": {
          "target": "<desired_url_tablet>",
          "num_redirects": 0
        },
        "mobile": {
          "target": "<desired_url_mobile>",
          "num_redirects": 0
        }
      }
    }
  ],
}
```
### 5. Redirection to the desired URL
After the creation of a shortened URL, you may navigate to 
<your_server_root_url>/<shortened_url>

The server will redirect you to the configured URL for your specific device and update the number of redirects num_redirects variable.



