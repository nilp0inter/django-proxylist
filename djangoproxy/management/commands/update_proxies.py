import os
from django.core.management.base import BaseCommand, CommandError
from djangoproxy.models import Proxy

class Command(BaseCommand):
    args = '<hidemyass proxy list files>'
    help = 'Update proxy list from file(s)'

    def handle(self, *args, **options):
        for filename in args:
            if not os.path.isfile(filename):
                self.stderr.write("File %s does not exists!\n" % filename)
                continue
           
            self.stdout.write("Loading %s...\n" % filename)
            
            with open(filename, 'r') as f:
                for proxy in f:

                    proxy = proxy.replace('\n','').replace('\r','')

                    try:
                        ip_address, port = proxy.split(':', 2)
                    except ValueError:
                        self.stderr.write("Invalid format %s. ip:port" % proxy)
                        continue

                    try:
                        port = int(port)
                    except ValueError:
                        self.stderr.write("Invalid port %s value" % port)
                        continue

                    p, created = Proxy.objects.get_or_create(
                                    ip_address=ip_address, 
                                    port=port)


