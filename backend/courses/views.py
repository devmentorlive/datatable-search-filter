from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.http.response import HttpResponse
from rest_framework.decorators import api_view
from courses.models import Participant
from events.events_serializer import EventSerializer
from events.models import Event
from participants.participants_serializer import ParticipantSerializer
from .courses_serializer import CourseSerializer
from .models import Course, CourseParticipant
from django.shortcuts import get_object_or_404
import json

@api_view(["GET", "POST"])
def open_path(request):
    """
        handles paths courses/
        adds a course and gets a list of courses
    """
    if request.method == "GET":
        data = Course.objects.all().filter(deleted=False)
        serializer = CourseSerializer(data, many=True)
        return JsonResponse(serializer.data, safe=False)
    else:
        json_data = request.data
        NewCourse = Course()
        for k, v in json_data.items():
            setattr(NewCourse, k, v)
        NewCourse.save()
        serializer = CourseSerializer(NewCourse)
        return JsonResponse(serializer.data, safe=False)


@api_view(["GET"])
def look_up(request, pk):
    """
        handles paths courses/{course_id}
        adds a course associated to course_id
    """
    # data = Course.objects.get(course_id=pk)
    data = get_object_or_404(Course, course_id=pk)
    serializer = CourseSerializer(data)
    return JsonResponse(serializer.data, safe=False)


@api_view(["POST"])
def add_participant_to_course(request, pk, participant_id):
    """
        handles paths courses/{course_id}/participants/
        adds a course associated to course_id
    """
    course = Course.objects.filter(course_id=pk).first()
    participant = Participant.objects.filter(
        participant_id=participant_id).first()
    if course and participant:
        course_p = CourseParticipant(course_id=course,
                                     participant_id=participant)
        course_p.save()
        return JsonResponse(["status code 200"], safe=False)
    else:
        error_message = ""
        if not course:
            error_message += ("Course with course_id=%s does not exist. " % pk)
        if not participant:
            error_message += ("Participant with participant_id=%s does not exist. " % participant_id)
        return HttpResponseBadRequest(error_message)


@api_view(["GET"])
def get_course_participants(request, pk):
    """
        handles paths courses/{course_id}/participants/
        adds a course associated to course_id
    """
    data = CourseParticipant.objects.all().filter(course_id=pk)
    all_part = []
    for cp in data.iterator():
        part = cp.participant_id
        ser = ParticipantSerializer(part)
        all_part.append(ser.data)
    return JsonResponse(all_part, safe=False)


@api_view(["GET"])
def event_lookup(request, pk):
    data = Event.objects.all().filter(course_id=pk)
    serializer = EventSerializer(data, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(["GET"])
def check_course_director(request, pk, participant_ccid):
    """
        returns all the events associated with a participant_id
    """
    participants = Participant.objects.filter(participant_ccid=participant_ccid)
    course = Course.objects.get(course_id=pk)
    for participant in participants:
        if participant.participant_type == "instructor":
            if participant.participant_id == course.course_director.participant_id:
                return HttpResponse(json.dumps({'result': "true"}),content_type="application/json")
    return HttpResponse(json.dumps({'result': "false"}), content_type="application/json")