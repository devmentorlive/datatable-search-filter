from . import views
from django.urls import path, re_path


urlpatterns = [
    path("<event_id>", views.look_up),
    re_path(r'^ical/$', views.get_events_from_participant_ccid),
    re_path(r'^$', views.open_path, name="open path"),
    re_path(r'^(?P<event_id>\d+)/groups/$', views.get_event_groups),
    path("locations/", views.get_locations),
    path("student_count/", views.get_student_counts_same_location),
    path("<event_id>/groups/<group_id>/", views.manage_event_group),
    path("<event_id>/groups/<group_id>/instructors/", views.base_group_instructors),
    path("<event_id>/groups/<group_id>/instructors/<participant_id>/", views.handle_group_instructors),
    path("tags/", views.general_tags),
    path("tags/<tag_id>/", views.manage_tags),
    path("<event_id>/tags/", views.event_tags),
    path("<event_id>/tags/<tag_id>/", views.manage_event_tag),
    path("zoom/signature/", views.generate_zoom_signature),
    path("zoom/access_token/", views.get_zoom_access_token),
    path("zoom/user_data/", views.get_zoom_user_data),
    path("zoom/create-meeting/", views.create_zoom_meeting),
    re_path(r'^file-attachment/$', views.retrieve_google_drive),
    re_path(r'^zoom-meeting/$', views.retrieve_zoom_link),
    re_path(r'^instructor-file-attachment/$', views.retrieve_instructor_google_drive),
    re_path(r'^remove-google-drive-file/$', views.delete_google_drive_file),
]
