from django.conf.urls import patterns, include, url

from sc2game import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^about', views.about, name='about'),
                       url(r'^(?P<stream_url>\w+)/', views.stream, name='stream')
                       )
