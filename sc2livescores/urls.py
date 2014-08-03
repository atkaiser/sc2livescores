from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^sc2game/', include('sc2game.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('sc2game.urls')),
)
