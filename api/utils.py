from math import floor
import string

def toBase62(num, b = 62):
    if b <= 0 or b > 62:
        return 0
    base = string.digits + string.ascii_letters
    r = num % b
    res = base[r];
    q = floor(num / b)
    while q:
        r = q % b
        q = floor(q / b)
        res = base[int(r)] + res
    return res

def toBase10(num, b = 62):
    base = string.digits + string.ascii_letters
    limit = len(num)
    res = 0
    for i in range(limit):
        res = b * res + base.find(num[i])
    return res

class ShortenedUrlMatcher:
    regex = '[a-zA-Z0-9]+'

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return '%s' % value
