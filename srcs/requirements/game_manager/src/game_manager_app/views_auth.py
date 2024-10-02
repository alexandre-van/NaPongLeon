import requests
from rest_framework.response import Response
from rest_framework import status
from django.test import Client
import json
import logging
from pprint import pformat

logger = logging.getLogger(__name__)

def auth_required(view_func):
	def wrapper(request, *args, **kwargs):
		logger.debug(f"Request method: {request.method}")
		logger.debug(f"Request path: {request.path}")
		logger.debug(f"Request GET params: {pformat(request.GET)}")
		logger.debug(f"Request POST data: {pformat(request.POST)}")
		logger.debug(f"Request headers: {pformat(dict(request.headers))}")

		cookies = dict(request.COOKIES)
		access_token = cookies.get('access_token')
		refresh_token = cookies.get('refresh_token')

		if not access_token:
			logger.warning("Missing access token in cookies")
			return Response({"error": "Missing access token"}, status=status.HTTP_401_UNAUTHORIZED)

		logger.debug(f"Extracted access token: {access_token[:20]}...")
		logger.debug(f"Extracted refresh token: {refresh_token[:20] if refresh_token else 'None'}...")

		token = {
			'access_token': access_token,
			'refresh_token': refresh_token
		}

		auth_url = "http://authentication:8000/api/authentication/verify_token/"
		logger.debug(f"token: {token}")

		try:
			logger.debug('avant post')
			response = requests.post(auth_url, cookies=token)
			logger.debug(f"status={response.status_code}")
			logger.debug(f"response={response}")
			username = response.json().get('user')
			logger.debug(f"username={username}")
			if response.status_code == 200:
				return view_func(request, *args, **kwargs)
			else:
				return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
		except requests.exceptions.RequestException as e:
			logger.error(f"Authentication service error: {str(e)}")
			return Response({"error": "Authentication service unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

	return wrapper
