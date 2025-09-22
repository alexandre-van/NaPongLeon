
def parse_cookies(cookie_string):
    if not cookie_string:
        return {}
    return {
        k.strip(): v.strip() 
        for k, v in (pair.split('=', 1) for pair in cookie_string.split(';')) 
        if k and v
    }

def normalize_headers(headers):
    return {
        f"HTTP_{key.decode('ascii').upper().replace('-', '_')}": value.decode('ascii')
        for key, value in headers
    }