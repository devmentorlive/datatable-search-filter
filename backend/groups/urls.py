from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.open_path),
    re_path(r'^(?P<group_id>\d+)/participants/$', views.participant_look_up),
    path("<str:group_id>/participants/<str:participant_id>/", views.participant_operation),
    re_path(r'^(?P<group_id>\d+)', views.look_up),
]
