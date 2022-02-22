from django.core.exceptions import ValidationError
from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.http import HttpResponse, HttpResponseBadRequest
from courses.models import Course
from participants.models import Participant
from participants.participants_serializer import ParticipantSerializer
from .groups_serializer import GroupSerializer, GroupParticipantSerializer
from .models import Group, GroupParticipant
from django.shortcuts import get_object_or_404


def validate_course_id(data):
    if "course_id" not in data:
        raise ValidationError("The field 'course_id' is required")
    course = Course.objects.filter(course_id=data["course_id"], deleted=False).first()
    if course is None:
        raise ValidationError("Invalid course_id")
    data.pop("course_id")
    return course


def validate_group_id(data):
    if "group_id" not in data:
        raise ValidationError("The field 'group_id' is required")
    group = data["group_id"]
    if group is None:
        raise ValidationError("Invalid group_id")
    data.pop("group_id")
    return group


@api_view(["GET", "POST"])
def open_path(request):
    """
        handles paths groups/
        gets a list of all groups and creates a new group
    """
    if request.method == "GET":
        data = Group.objects.all().filter(deleted=False)
        serializer = GroupSerializer(data, many=True)
        return JsonResponse(serializer.data, safe=False)
    else:
        json_data = request.data
        try:
            course_id = validate_course_id(json_data)
        except ValidationError as e:
            return HttpResponseBadRequest(e.message)
        if "group_name" not in json_data:
            return HttpResponseBadRequest("The field 'group_name' is required")
        new_group = Group(course_id=course_id, group_name=json_data["group_name"])
        new_group.full_clean()
        new_group.save()
        return HttpResponse("Group successfully added")


@api_view(["GET", "DELETE", "PUT"])
def look_up(request, group_id):
    """
        handles paths groups/{group_id}
        gets a list of specific groups and edits a group and deletes it
    """
    if request.method == "GET":
        data = get_object_or_404(Group, pk=group_id, deleted=False)
        serializer = GroupSerializer(data)
        return JsonResponse(serializer.data, safe=False)
    elif request.method == "DELETE":
        data = get_object_or_404(Group, pk=group_id, deleted=False)
        data.deleted = True
        data.save()
        return HttpResponse("Group successfully deleted")
    else:
        json_data = request.data
        data = get_object_or_404(Group, pk=group_id, deleted=False)

        if "course_id" in json_data:
            try:
                data.course_id = Course.objects.get(course_id=json_data["course_id"])
            except Course.DoesNotExist:
                return HttpResponseBadRequest("Invalid course_id")
            json_data.pop("course_id")
        for k, v in json_data.items():
            setattr(data, k, v)
        data.full_clean()
        data.save()
        return HttpResponse("Group successfully updated")


@api_view(["POST", "DELETE"])
def participant_operation(request, group_id, participant_id):
    """
        handles paths groups/{group_id}/participants/{participant_id}
        adds a participant to a group and deletes a participant
    """
    if request.method == "DELETE":
        group_part = get_object_or_404(GroupParticipant, group_id=group_id,
                                       participant_id=participant_id, deleted=False)
        group_part.deleted = True
        group_part.save()
        return HttpResponse("Participant deleted from group")
    else:
        part = get_object_or_404(Participant, participant_id=participant_id, deleted=False)
        group = get_object_or_404(Group, group_id=group_id, deleted=False)
        group_part = GroupParticipant(participant_id=part, group_id=group)
        group_part.full_clean()
        group_part.save()
        return HttpResponse("Participant added to group")


@api_view(["GET"])
def participant_look_up(request, group_id):
    """
        handles paths groups/{group_id}/participants
        gets a list of all participants associated with a group id
    """
    if request.method == "GET":
        if len(request.GET) > 0:
            return group_query(request, group_id)
        data = GroupParticipant.objects.all().filter(deleted=False, group_id=group_id)
        part_data = []
        for part in data.iterator():
            serializer = ParticipantSerializer(part.participant_id, many=False)
            part_data.append(serializer.data)
        return JsonResponse(part_data, safe=False)


def group_query(request, group_id):
    """
        handles paths groups/{group_id}/participants/?participant_type={param}
        returns all participants wiith participant_type = {param} in the group
    """
    part_type = request.GET.get("participant_type")
    if part_type:
        group_part = GroupParticipant.objects.filter(deleted=False, group_id=group_id)
        part_data = []
        for part in group_part.iterator():
            if part.participant_id.participant_type == part_type:
                serializer = ParticipantSerializer(part.participant_id, many=False)
                part_data.append(serializer.data)
        return JsonResponse(part_data, safe=False)
