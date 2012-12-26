from djangoproxy.models import Proxy, ProxyChecker, ProxyCheckResult 
from django.contrib import admin

admin.site.register(Proxy)
admin.site.register(ProxyChecker)
admin.site.register(ProxyCheckResult)
