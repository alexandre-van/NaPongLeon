import requests
from rest_framework.response import Response
from rest_framework import status
from django.test import Client
import json
from pprint import pformat
from .logger import logger

def auth_required(view_func):
	def wrapper(request, *args, **kwargs):
		cookies = dict(request.COOKIES)
		access_token = cookies.get('access_token')
		refresh_token = cookies.get('refresh_token')
		if not access_token:
			logger.warning("Missing access token in cookies")
			return Response({"error": "Missing access token"}, status=status.HTTP_401_UNAUTHORIZED)
		token = {
			'access_token': access_token,
			'refresh_token': refresh_token
		}
		auth_url = "http://authentication:8000/api/authentication/verify_token/"
		try:
			response = requests.post(auth_url, cookies=token)
			username = response.json().get('user')
			if response and response.status_code == 200:
				return view_func(request, *args, **kwargs)
			else:
				return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
		except requests.exceptions.RequestException as e:
			logger.error(f"Authentication service error: {str(e)}")
			return Response({"error": "Authentication service unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

	return wrapper
