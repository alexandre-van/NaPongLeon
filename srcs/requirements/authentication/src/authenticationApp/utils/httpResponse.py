import json
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.core.serializers.json import DjangoJSONEncoder

import logging
logger = logging.getLogger(__name__)

def HttpResponseJD(message, status, additionnal_data=None):
    key = 'message' if status in [200, 201] else 'error'
    response_data = {key: message}

    if additionnal_data:
        response_data.update(additionnal_data)

    response = HttpResponse(
        json.dumps(response_data, cls=DjangoJSONEncoder),
        status=status,
        content_type='application/json'
    )
    logger.debug(f"HttpResponseJD = {response}")
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
