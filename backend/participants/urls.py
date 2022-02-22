from django.urls import path

from . import views

urlpatterns = [
    path('', views.open_path),
    path("<pk>", views.look_up),
    path("<pk>/courses/", views.get_courses),
    path("<pk>/groups/", views.get_groups),
    path("instructors/", views.get_course_instructors)
]
