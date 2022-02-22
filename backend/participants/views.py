from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework import status
from django.http import HttpResponse, HttpResponseBadRequest
from courses.courses_serializer import CourseSerializer
from courses.models import CourseParticipant
from groups.groups_serializer import GroupParticipantSerializer
from groups.models import GroupParticipant
from .models import Participant
from .participants_serializer import ParticipantSerializer
from django.core import serializers

@api_view(["GET", "POST"])
def open_path(request):
    """
        handles paths participants/
        adds a participant and returns a participant
    """
    if(request.method == "GET"):
        data = Participant.objects.all().filter(deleted=False)
        serializer = ParticipantSerializer(data, many=True)
        return JsonResponse(serializer.data, safe=False)
    if(request.method == "POST"):
        json_data = request.data
        participant_id = json_data["participant_id"]
        if(Participant.objects.filter(participant_id=participant_id).count() == 0):
            NewParticipant = Participant(participant_id=participant_id)
            for k, v in json_data.items():
                setattr(NewParticipant, k, v)
            NewParticipant.save()
            serializer = ParticipantSerializer(NewParticipant)
            return JsonResponse(serializer.data, safe=False)
        return HttpResponse("participant already exists", status=status.HTTP_409_CONFLICT)


# check
@api_view(["GET", "DELETE", "PUT"])
def look_up(request, pk):
    """
        handles paths participants/{participant_id}
        gets a participantm edits a participant and deletes them
    """
    if(request.method == "GET"):
        data = Participant.objects.filter(participant_ccid=pk)
        # serializer = ParticipantSerializer(data)
        json_data = serializers.serialize("json", data)
        print("json_data: ", json_data)
        return JsonResponse(json_data, safe=False)
    if(request.method == "DELETE"):
        data = Participant.objects.filter(participant_ccid=pk)
        data.deleted = True
        data.save()
    if(request.method == "PUT"):
        json = request.data
        data = Participant.objects.filter(participant_ccid=pk)
        for k, v in json.items():
            setattr(data, k, v)
        data.save()

@api_view(["GET"])
def get_course_instructors(request):
    """
        handles paths participants/instructors
        gets all course instructors
    """
    instructors = Participant.objects.all().fitler(participant_type='instructor', deleted=False)
    serializer = ParticipantSerializer(instructors, many=True)
    return JsonResponse(serializer.data, safe=False)

# check
@api_view(["GET"])
def get_courses(request, pk):
    """
        handles paths participants/{participant_id}/courses
        gets all courses associated with a participant_id
    """
    data = CourseParticipant.objects.all().filter(participant_id=pk)
    all_courses = []
    for part in data.iterator():
        course = part.course_id
        ser = CourseSerializer(course)
        all_courses.append(ser.data)
    return JsonResponse(all_courses, safe=False)


# check
@api_view(["GET"])
def get_groups(request, pk):
    """
        handles paths participants/{participant_id}/groups
        gets all gropus associated with a participant_id
    """
    data = GroupParticipant.objects.all().filter(participant_id=pk)
    all_groups = []
    for part in data.iterator():
        group = part.group_id
        ser = GroupParticipantSerializer(group)
        all_groups.append(ser.data)
    return JsonResponse(all_groups, safe=False)
