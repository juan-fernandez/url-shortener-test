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

And your are ready to go! 

## Run the tests
```
python3 manage.py test
```

## Run the server
```
python3 manage.py runserver
```

## API description 
Create a new link: POST /api/v1/ with body
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
      "shortened_url": "<shortened_url_result>",
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
Get list of all links: GET /api/v1/ 

Get info of a shortened_link: GET /api/v1/shortened_url/<shortened_url>
Response:
```
{
  "result": [
    {
      "shortened_url": "<shortened_url>",
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
Modify a shortened_url to act differently depending on the device: 
POST /api/v1/shortened_url/<shortened_url> with body:
```
{
  "target_url_<type_of_device>":"<desired_url>",
  ... (may include up to 3 keys, for tablet, mobile and desktop)
}
```
For example, for changing tablet and mobile:
POST /api/v1/shortened_url/<shortened_url> with body:
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
      "shortened_url": "<shortened_url>",
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

After the setting, you may navigate to 
http://<your_server_root_url>/<shortened_url>

And the server will redirect you to your desired URL, depending on the device you use. 

Each of the redirects will be counted in the variable 'num_redirects', i.e. a visit to http://<your_server_root_url>/<shortened_url> with a desktop computer will result in the following state:
```
{
  "result": [
    {
      ...
      "redirects": {
        ...
        "desktop": {
          "target": "<desired_url_desktop>",
          "num_redirects": 1
        }
      }
    }
  ],
}
```


