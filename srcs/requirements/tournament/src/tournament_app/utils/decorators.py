import json
from functools import wraps
from .logger import logger
import httpx

def auth_required(func):
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
			kwargs['nickname'] = None
			if response and response.status_code == 200:
				username = response.json().get('user')
				nickname = response.json().get('nickname')
				kwargs['username'] = username
				kwargs['nickname'] = nickname
			return await func(self, *args, **kwargs)
		except httpx.RequestError as e:
			logger.error(f"Authentication service error: {str(e)}")
			return
	return wrapper
