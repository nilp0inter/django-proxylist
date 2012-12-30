from django.conf.urls import patterns, url                             
                                                                                
urlpatterns = patterns('',                                                      
    url(r'^mirror$', 'proxylist.views.mirror', name='proxylist_mirror'),
)
