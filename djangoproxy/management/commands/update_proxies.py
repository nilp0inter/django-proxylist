import os
from django.core.management.base import BaseCommand, CommandError
from phishink.models import Country, Proxy

class Command(BaseCommand):
    args = '<hidemyass proxy list files>'
    help = 'Update hidemyass proxy list files into phishink'

    def handle(self, *args, **options):
        firstproxy = True
        new_proxies = []
        same_proxies = []
        for hmafile in args:
            if not os.path.isfile(hmafile):
                self.stderr.write("File %s does not exists!\n" % hmafile)
                continue
           
            self.stdout.write("Loading %s...\n" % hmafile)
            # Get country from filename
            try:
                country_name = ".".join(os.path.basename(hmafile).split('.')[:-1]).upper()
                country = Country.objects.get(code=country_name)
            except Country.DoesNotExist:
                country = None
            
            with open(hmafile, 'r') as f:
                for proxy in f:
                    proxy = proxy.replace('\n','').replace('\r','')

                    if firstproxy:
                        # Disable all proxies at inserting first proxy
                        Proxy.objects.all().update(enabled=False)
                        firstproxy=False

                    try:
                        p = Proxy.objects.get(http_proxy=proxy).pk
                        same_proxies.append(p)
                        created = False
                    except Proxy.DoesNotExist:
                        p = Proxy(http_proxy=proxy)
                        p.proxy_type='MANUAL'
                        p.ssl_proxy=proxy
                        p.country=country
                        p.enabled=True
                        created = True
                        new_proxies.append(p)

        Proxy.objects.filter(pk__in=same_proxies).update(enabled=True)
        Proxy.objects.exclude(pk__in=same_proxies).update(enabled=False)
        Proxy.objects.bulk_create(new_proxies)

