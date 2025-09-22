import httpx
from django.http import JsonResponse
from .logger import logger
from functools import wraps

def auth_required(view_func):
	async def wrapper(request, *args, **kwargs):
		cookies = dict(request.COOKIES)
		access_token = cookies.get('access_token')
		refresh_token = cookies.get('refresh_token')
		if not access_token:
			logger.warning("Missing access token in cookies")
			return JsonResponse({"error": "Missing access token"}, status=401)

		token = {
			'access_token': access_token,
			'refresh_token': refresh_token
		}

		auth_url = "http://authentication:8000/api/authentication/verify_token/"

		try:
			async with httpx.AsyncClient() as client:
				response = await client.post(auth_url, cookies=token)

			if response and response.status_code == 200:
				username = response.json().get('user')
				if not kwargs.get('username'):
					kwargs['username'] = username
				return await view_func(request, *args, **kwargs)
			else:
				return JsonResponse({"error": "Invalid token"}, status=401)
		except httpx.RequestError as e:
			logger.error(f"Authentication service error: {str(e)}")
			return JsonResponse({"error": "Authentication service unavailable"}, status=503)

	return wrapper


def auth_required_ws(func):
	@wraps(func)
	async def wrapper(self, *args, **kwargs):
		cookies = self.scope['headers']
		cookie_header = dict(cookies).get(b'cookie', b'').decode('utf-8')
		cookies_dict = {}
		for cookie in cookie_header.split(';'):
			key_value = cookie.strip().split('=')
			if len(key_value) == 2:
				cookies_dict[key_value[0]] = key_value[1]
		access_token = cookies_dict.get('access_token')
		refresh_token = cookies_dict.get('refresh_token')
		if not access_token:
			kwargs['username'] = None
			return await func(self, *args, **kwargs)
		token = {
			'access_token': access_token,
			'refresh_token': refresh_token
		}
		auth_url = "http://authentication:8000/api/authentication/verify_token/"
		try:
			async with httpx.AsyncClient() as client:
				response = await client.post(auth_url, cookies=token)
			kwargs['username'] = None
			if response and response.status_code == 200:
				username = response.json().get('user')
				kwargs['username'] = username
			return await func(self, *args, **kwargs)
		except httpx.RequestError as e:
			logger.error(f"Authentication service error: {str(e)}")
			return
	return wrapper

def async_csrf_exempt(view_func):
    async def wrapped_view(*args, **kwargs):
        return await view_func(*args, **kwargs)
    wrapped_view.csrf_exempt = True
    return wraps(view_func)(wrapped_view)