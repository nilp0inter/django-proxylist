from djangoproxy.models import Proxy, ProxyChecker, ProxyCheckResult 
from django.contrib import admin

class ProxyAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'port', 'country', 'anonymity_level', 
                    'last_check', 'proxy_type',  )
    list_filter = ('anonymity_level', 'proxy_type', )
    search_fields = ('=ip_address', '=port', 'country', )

admin.site.register(Proxy, ProxyAdmin)
admin.site.register(ProxyChecker)

# Debug
#admin.site.register(ProxyCheckResult)
