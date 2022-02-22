from .programs_serializer import ProgramSerializer
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .models import Program

@api_view(["GET"])
def get_all(request):
    data = Program.objects.all().filter(deleted=False)
    serializer = ProgramSerializer(data, many=True)
    return JsonResponse(serializer.data, safe=False)