from django.http import JsonResponse
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="calendar.med API",
      default_version='v1',
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)


def display_text(request):
    text = request.GET.get("text", "")
    return JsonResponse({"message": text})
