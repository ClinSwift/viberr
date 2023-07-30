#from django.conf.urls import url
from django.urls import re_path
from . import views 

app_name = 'music' 

urlpatterns = [ 
    re_path(r'^$', views.index, name='index'), 
    re_path(r'^register/$', views.register, name='register'), 
    re_path(r'^login_user/$', views.login_user, name='login_user'), 
    re_path(r'^logout_user/$', views.logout_user, name='logout_user'), 
    re_path(r'^(?P<album_id>[0-9]+)/$', views.detail, name='detail'), 
    re_path(r'^(?P<song_id>[0-9]+)/favorite/$', views.favorite, name='favorite'), 
    re_path(r'^songs/(?P<filter_by>[a-zA_Z]+)/$', views.songs, name='songs'), 
    re_path(r'^create_album/$', views.create_album, name='create_album'), 
    re_path(r'^(?P<album_id>[0-9]+)/create_song/$', views.create_song, name='create_song'), 
    re_path(r'^(?P<album_id>[0-9]+)/delete_song/(?P<song_id>[0-9]+)/$', views.delete_song, name='delete_song'), 
    re_path(r'^(?P<album_id>[0-9]+)/favorite_album/$', views.favorite_album, name='favorite_album'), 
    re_path(r'^(?P<album_id>[0-9]+)/delete_album/$', views.delete_album, name='delete_album'),
    ]
