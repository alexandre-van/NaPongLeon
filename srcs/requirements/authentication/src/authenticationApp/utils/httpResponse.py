import json
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseNotFound
from django.core.serializers.json import DjangoJSONEncoder

import logging
from django.utils import timezone
logger = logging.getLogger(__name__)

def HttpResponseJD(message, status, additionnal_data=None):
    key = 'message' if status in [200, 201] else 'error'
    response_data = {key: message}
    current_time = timezone.now()

    if additionnal_data is not None:
        if isinstance(additionnal_data, dict):
            response_data.update(additionnal_data)
        else:
            response_data['data'] = additionnal_data

    response = HttpResponse(
        json.dumps(response_data, cls=DjangoJSONEncoder),
        status=status,
        content_type='application/json'
    )
    return response


def HttpResponseRedirectJD(message, status, redirect_url, additionnal_data=None):
    response_data = { 'message': message, 'status': status}
    if additionnal_data:
        response_data.update(additionnal_data)

    response = HttpResponseRedirect(redirect_url)
    response.set_cookie(
        'redirect_data',
        json.dumps(response_data, cls=DjangoJSONEncoder),
        max_age=30,
        httponly=True,
        samesite='Strict'
    )
    (f"HttpResponseRedirectJD = {response}")
    return response

def HttpResponseBadRequestJD(errorMessage):
    return HttpResponseBadRequest(
        json.dumps({'error': errorMessage}),
        content_type='application/json'
    )

def HttpResponseNotFoundJD(errorMessage):
    return HttpResponseNotFound(
        json.dumps({'error': errorMessage}),
        content_type='application/json'
    )

def HttpResponseJDexception(e):
    return HttpResponse(
        json.dumps({'error': str(e)}, cls=DjangoJSONEncoder),
        status=500,
        content_type='application/json'
    )
