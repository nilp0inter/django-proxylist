import os

from datetime import datetime

from django.utils.timezone import now
from django.core.management.base import BaseCommand, CommandError

from djangoproxy.models import Proxy, ProxyChecker

from celery import group 

class Command(BaseCommand):
    args = '<hidemyass proxy list files>'
    help = 'Update proxy list from file(s)'

    def handle(self, *args, **options):
        c = ProxyChecker.objects.all()[0]

        proxies = Proxy.objects.filter(next_check__lte=now())
        to_check = []
        for p in proxies:
            if not c.is_checking(p):
                c.check(p)
            else:
                print p, "is checking now!"
