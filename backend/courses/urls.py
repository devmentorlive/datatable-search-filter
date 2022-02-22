from django.urls import path
from . import views


urlpatterns = [
    path('', views.open_path),
    path("<pk>", views.look_up),
    path("<pk>/participants/", views.get_course_participants),
    path("<int:pk>/participants/<participant_id>", views.add_participant_to_course),
    path("<int:pk>/events/", views.event_lookup),
    path("<int:pk>/course-director/<str:participant_ccid>", views.check_course_director)
]
