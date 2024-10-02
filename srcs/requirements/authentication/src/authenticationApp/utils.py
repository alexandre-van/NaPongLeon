import json
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.core.serializers.json import DjangoJSONEncoder

def HttpResponseJD(message, status):
    key = 'message' if status in [200, 201] else 'error'
    response_data = {key: message}
    return HttpResponse(
        json.dumps(response_data),
        status=status,
        content_type='application/json'
    )

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
