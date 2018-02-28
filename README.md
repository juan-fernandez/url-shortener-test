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
