from django.conf.urls import patterns, include, url

from sc2game import views

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'sc2litescores.views.home', name='home'),
                       # url(r'^blog/', include('blog.urls')),
                       url(r'^$', views.index, name='index'),
                       url(r'^(?P<stream_url>\w+)/', views.stream, name='stream')
                       )
