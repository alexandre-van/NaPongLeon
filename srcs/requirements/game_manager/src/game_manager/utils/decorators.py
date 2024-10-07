import httpx
from django.http import JsonResponse
from .logger import logger

def auth_required(view_func):
	async def wrapper(request, *args, **kwargs):
		logger.debug("Auth1")
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
				logger.debug("Auth2")
				response = await client.post(auth_url, cookies=token)
				logger.debug("Auth3")

			if response and response.status_code == 200:
				username = response.json().get('user')
				kwargs['username'] = username
				return await view_func(request, *args, **kwargs)
			else:
				return JsonResponse({"error": "Invalid token"}, status=401)
		except httpx.RequestError as e:
			logger.error(f"Authentication service error: {str(e)}")
			return JsonResponse({"error": "Authentication service unavailable"}, status=503)

	return wrapper
