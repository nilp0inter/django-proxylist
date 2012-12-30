# -*- coding: utf-8 -*-
import json

from django.http import HttpResponse
from django.utils.timezone import now

def mirror(request):
    """
    from dateutil.parser import parse
    parse("2012-12-28 22:22:12.868342+04:00")
    datetime.datetime(2012, 12, 28, 22, 22, 12, 868342, tzinfo=tzoffset(None, 14400))
    """

    start = now()

    SERIALIZABLE = (str, unicode, bool, int, float)

    output = dict()

    output['REMOTE_ADDR'] = request.META.get('REMOTE_ADDR', '')
    output['REMOTE_HOST'] = request.META.get('REMOTE_HOST', '')

    # HTTP Headers
    output['http_headers'] = dict()
    for k, v in request.META.items():
        if k.startswith('HTTP_') and type(v) in SERIALIZABLE:
               output['http_headers'][k[5:]] = v

    # Timing
    output['response_start'] = str(start)
    output['response_end'] = str(now())

    return HttpResponse(json.dumps(output))

