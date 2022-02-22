from datetime import datetime
from django.core.exceptions import ValidationError
from django.core import serializers
from django.http import HttpResponse, HttpResponseBadRequest
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from courses.models import Course
from groups.models import Group, GroupParticipant
from participants.models import Participant
from .events_serializer import EventSerializer, EventGroupSerializer, TagSerializer, EventTagSerializer, \
    EventGroupInstructorSerializer, EventFileAttachmentSerializer, EventInstructorFileAttachmentSerializer, EventVodcastSerializer, ZoomMeetingSerializer
from django.db.models import Sum
import hashlib, hmac, base64, time
from .models import Event, EventGroup, Tag, EventTag, EventGroupInstructor, EventFileAttachment, EventInstructorFileAttachment, EventVodcast, ZoomMeeting
from programs.models import Program
from programs.programs_serializer import ProgramSerializer
import requests, json

# import http.client

# helper function to check if search query has a number in it
def has_numbers(input_string):
    return any(char.isdigit() for char in input_string)


# query check search string has a number
def search_number(query):
    """
    Search through all events and the return a set of
    all the events where the query is contained by the field
    """
    session = Event.objects.filter(training_session__icontains=query)
    date = Event.objects.filter(event_date__icontains=query)
    end = Event.objects.filter(start_time__icontains=query)
    start = Event.objects.filter(end_time__icontains=query)
    total_set = session | date | end | start
    return total_set


def search_non_number(query):
    """
    Search through all events and the retrun a set of
    all the events where the query is contained by the field
    It also cycles through the event tags
    """
    titles = Event.objects.filter(event_title__icontains=query)
    desc = Event.objects.filter(event_desc__icontains=query)
    e_type = Event.objects.filter(event_type__icontains=query)
    tags = Tag.objects.filter(tag_name__icontains=query)
    total_set = titles | desc | e_type
    for tag in tags:
        event_tags = EventTag.objects.filter(tag_id=tag.tag_id)
        for event_tag in event_tags:
            total_set = total_set | Event.objects.filter(event_id=event_tag.event_id.event_id)
    return total_set


# helper function to check if a Course exists with with a certain id, if it doesnt it returns a validation error
def validate_course_id(data):
    if "course_id" not in data:
        raise ValidationError("The field 'course_id' is required")
    course = Course.objects.filter(course_id=data["course_id"], deleted=False).first()
    # if course is None:
    #     raise ValidationError("Invalid course_id")
    data.pop("course_id")
    return course


# checks to see if start time is before end time and returns difference between times in minutes
def validate_start_and_end_time(start_time, end_time):
    if start_time > end_time:
        raise ValidationError("End time cannot be before start time")
    formatted_start_time = datetime.strptime(start_time, '%H:%M:%S')
    formatted_end_time = datetime.strptime(end_time, '%H:%M:%S')
    return int((formatted_end_time - formatted_start_time).total_seconds() / 60)


@api_view(["GET", "POST"])
def open_path(request):
    """
    handles event path "events/" and events?param=search
    """
    if request.method == "GET":
        if len(request.GET) > 0:
            return general_query(request)
        data = Event.objects.all().filter(deleted=False)
        serializer = EventSerializer(data, many=True)
        return JsonResponse(serializer.data, safe=False)
    else:
        json_data = request.data
        new_event = Event()
        # TODO: make sure event does not exist already (check deleted)
        try:
            new_event.course_id = validate_course_id(json_data)
        except ValidationError as e:
            return HttpResponseBadRequest(e.message)
        try:
            duration = validate_start_and_end_time(json_data["start_time"], json_data["end_time"])
        except ValidationError:
            return HttpResponseBadRequest("End time cannot be before start time")
        json_data["total_duration"] = duration
        #checks if program exists, if not, reject
        try:
            new_event.prog_id = Program.objects.get(prog_id = json_data["prog_id"])
            json_data.pop("prog_id")
        except Program.DoesNotExist:
            return HttpResponseBadRequest("Program does not exist")
        for k, v in json_data.items():
            if k == "event_file_attachment":
                event_file_attachment = v
                print("v:", v)
            elif k == "event_instructor_file_attachment":
                event_instructor_file_attachment = v
                print("v for instructor:", v)
            elif k == "vodcast_url":
                event_vodcast_url = v
            else:
                setattr(new_event, k, v)

        new_event.full_clean()
        new_event.save()

        # upload a new query into cal_event_file_attachment table
        if event_file_attachment:
            new_event_fileAttachment = EventFileAttachment(event_id=new_event)
            for k, v in event_file_attachment.items():
                setattr(new_event_fileAttachment, k, v)
            new_event_fileAttachment.full_clean()
            new_event_fileAttachment.save()

         # upload a new query into cal_event_instructor_file_attachment table
        if event_instructor_file_attachment:
            new_event_instructor_fileAttachment = EventInstructorFileAttachment(event_id=new_event)
            for k, v in event_instructor_file_attachment.items():
                setattr(new_event_instructor_fileAttachment, k, v)
            new_event_instructor_fileAttachment.full_clean()
            new_event_instructor_fileAttachment.save()

        # upload a new query into cal_event_vodcast_url table
        if event_vodcast_url:
            new_event_vodcast = EventVodcast(event_id=new_event)
            setattr(new_event_vodcast, "vodcast_url", event_vodcast_url)
            new_event_vodcast.full_clean()
            new_event_vodcast.save()

        return HttpResponse("Event successfully added")


@api_view(["GET", "DELETE", "PUT"])
def look_up(request, event_id):
    """
    allows GET, DELETE, PUT commands
    handles event path "events/{event_id}"
    """
    if request.method == "GET":
        data = get_object_or_404(Event, pk=event_id, deleted=False)
        serializer = EventSerializer(data)
        return JsonResponse(serializer.data, safe=False)
    elif request.method == "DELETE":
        data = get_object_or_404(Event, pk=event_id, deleted=False)
        data.deleted = True
        data.save()
        return HttpResponse("Event successfully deleted")
    else:
        # TODO: validate end and start time here as well
        updated_event = get_object_or_404(Event, pk=event_id, deleted=False)
        json_data = request.data
        try:
            updated_event.course_id = validate_course_id(json_data)
        except ValidationError as e:
            return HttpResponseBadRequest(e.message)
        try:
            duration = validate_start_and_end_time(json_data["start_time"], json_data["end_time"])
        except ValidationError:
            return HttpResponseBadRequest("End time cannot be before start time")
        json_data["total_duration"] = duration
        for k, v in json_data.items():
            if k == "event_file_attachment":
                event_file_attachment = v
                print("v:", v)
            elif k == "event_instructor_file_attachment":
                event_instructor_file_attachment = v
                print("v for instructor:", v)
            else:
                setattr(updated_event, k, v)
        updated_event.save()
        if event_file_attachment:
            old_event_fileAttachment = EventFileAttachment.objects.filter(event_id=updated_event.event_id)
            if old_event_fileAttachment:
                old_event_fileAttachment.delete()
            new_event_fileAttachment = EventFileAttachment(event_id=updated_event)
            for k, v in event_file_attachment.items():
                setattr(new_event_fileAttachment, k, v)
            new_event_fileAttachment.full_clean()
            new_event_fileAttachment.save()

         # upload a new query into cal_event_instructor_file_attachment table
        if event_instructor_file_attachment:
            old_event_instructor_fileAttachment = EventInstructorFileAttachment.objects.filter(event_id=updated_event.event_id)
            if old_event_instructor_fileAttachment:
                old_event_instructor_fileAttachment.delete()
            new_event_instructor_fileAttachment = EventInstructorFileAttachment(event_id=updated_event)
            for k, v in event_instructor_file_attachment.items():
                setattr(new_event_instructor_fileAttachment, k, v)
            new_event_instructor_fileAttachment.full_clean()
            new_event_instructor_fileAttachment.save()
        return HttpResponse("Event successfully updated")

@api_view(["GET"])
def get_locations(request):
    data = Event.objects.all().filter(deleted=False)
    locations = []
    for eventgroup in data:
        if eventgroup.location not in locations:
            locations.append(eventgroup.location)
    response = json.dumps({"data": locations})
    return HttpResponse(response)

@api_view(["GET"])
def get_event_groups(request, event_id):
    """
    allows GET commands
    handles event path "events/{event_id}/groups"
    returns all the events_groups associated with an event_id
    """
    if request.GET.get("participant"):
        participant_id = request.GET.get("participant")
        groups = GroupParticipant.objects.filter(participant_id=participant_id)
        query = []
        for group in groups.iterator():
            events = EventGroup.objects.filter(group_id=group.group_id.group_id, event_id=event_id)
            if(events.count() > 0):
                ser = EventGroupSerializer(events, many=True)
                query.append(ser.data)
        return JsonResponse(query, safe=False)
    data = EventGroup.objects.all().filter(event_id=event_id, deleted=False)
    serializer = EventGroupSerializer(data, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(["POST", "DELETE", "PUT", "GET"])
def manage_event_group(request, event_id, group_id):
    """
    handles event path "events/{event_id}/groups/{group_id}/"
    """
    if request.method == "POST":
        json_data = request.data
        event = get_object_or_404(Event, pk=event_id)
        g = get_object_or_404(Group, pk=group_id)
        search = EventGroup.objects.filter(event_id=event_id, group_id=group_id)
        if search.count() == 0:
            event_group = EventGroup(event_id=event, group_id=g)
            for k, v in json_data.items():
                setattr(event_group, k, v)
            event_group.save()
            return HttpResponse("Group successfully added to event")
        return HttpResponse("Group with that id already exists", status=status.HTTP_409_CONFLICT)
    elif request.method == "DELETE":
        event_group = EventGroup.objects.get(event_id=event_id, group_id=group_id)
        event_group.deleted = True
        event_group.save()
        return HttpResponse("Group successfully deleted from event")
    elif request.method == "GET":
        event_group = EventGroup.objects.get(event_id=event_id, group_id=group_id)
        ser = EventGroupSerializer(event_group)
        return JsonResponse(ser.data, safe=True)
    else:
        json_data = request.data
        search = EventGroup.objects.filter(event_id=event_id, group_id=group_id)
        if search.count() > 1:
            return HttpResponse("too many event groups exist", status=status.HTTP_403_FORBIDDEN)
        elif search.count() == 1:
            event = EventGroup.objects.get(event_id=event_id, group_id=group_id)
            for k, v in json_data.items():
                setattr(event, k, v)
            event.full_clean()
            event.save()
            return HttpResponse("event group editied")
        return HttpResponse("event group doesnt exist", status=status.HTTP_406_NOT_ACCEPTABLE)


@api_view(["POST", "GET"])
def general_tags(request):
    """
    handles event path "events/tags/"
    creates a new tag and gets a list of tags
    """
    if request.method == "GET":
        data = Tag.objects.filter(deleted=False)
        ser = TagSerializer(data, many=True)
        return JsonResponse(ser.data, safe=False)
    elif request.method == "POST":
        json_data = request.data
        if "tag_name" in json_data:
            tag_name = json_data["tag_name"]
            new_tag = Tag(tag_name=tag_name)
            new_tag.full_clean()
            new_tag.save()
            return HttpResponse("Tag successfully created")


@api_view(["GET", "PUT", "DELETE"])
def manage_tags(request, tag_id):
    """
    handles event path "events/tags/{tag_id}"
    edits tag and gets a specific tag and deletes a tag
    """
    if request.method == "GET":
        data = Tag.objects.filter(tag_id=tag_id)
        ser = TagSerializer(data, many=True)
        return JsonResponse(ser.data, safe=False)
    elif request.method == "PUT":
        json_data = request.data
        if "tag_name" in json_data:
            tag_name = json_data["tag_name"]
            data = get_object_or_404(Tag, tag_id=tag_id)
            data.tag_name = tag_name
            data.full_clean()
            data.save()
            return HttpResponse("Tag successfully edited")
    else:
        data = get_object_or_404(Tag, tag_id=tag_id)
        data.deleted = True
        data.full_clean()
        data.save()
        return HttpResponse("Tag successfully deleted")

@api_view(["POST", "GET"])
def event_tags(request, event_id):
    """
    handles event path "events/{event_id}/tags/"
    creates a event tag and gets a list of event tags
    """
    if request.method == "POST":
        event = get_object_or_404(Event, pk=event_id, deleted=False)
        json_data = request.data
        if "tag_id" in json_data:
            tag_id = json_data["tag_id"]
            tag = get_object_or_404(Tag, pk=tag_id, deleted=False)
            if EventTag.objects.filter(event_id=event, tag_id=tag).count() < 1:
                new_tag = EventTag(event_id=event, tag_id=tag)
                new_tag.full_clean()
                new_tag.save()
                return HttpResponse("Event tag successfully created")
            return HttpResponse("tag already added to this event", status=status.HTTP_403_FORBIDDEN)
    if request.method == "GET":
        data = EventTag.objects.filter(event_id=event_id, deleted=False)
        ser = EventTagSerializer(data, many=True)
        return JsonResponse(ser.data, safe=False)


@api_view(["GET", "DELETE"])
def manage_event_tag(request, event_id, tag_id):
    """
    handles event path "events/{event_id}/tags/{tag_id}/"
    gets a specific tag and deletes it
    """
    if request.method == "GET":
        get_object_or_404(Tag, pk=tag_id, deleted=False)
        get_object_or_404(Event, pk=event_id, deleted=False)
        data = EventTag.objects.filter(event_id=event_id, tag_id=tag_id)
        ser = EventTagSerializer(data, many=True)
        return JsonResponse(ser.data, safe=False)
    else:
        data = EventTag.objects.get(tag_id=tag_id, event_id=event_id)
        data.deleted = True
        data.full_clean()
        data.save()
        return HttpResponse("Tag successfully deleted")


def general_query(request):
    """
    handles event path "events?search={search query}"
    , "events?search={search query}"&participant={participant=_id}
    , "events?event_type={event_type1,event_type2}"&participant={participant=_id}
    """
    search = request.GET.get("search")
    # if there is a participant id available
    part_events = Event.objects.all().filter(deleted=False)
    if request.GET.get("participant"):
        part_events = get_events_from_participant(request)

    if search:
        if "," not in search:
            if has_numbers(search):
            # union set of all events with strings matching query
                non_number = search_non_number(search)
                number = search_number(search)
                data = non_number | number
                data = data & part_events
                serializer = EventSerializer(data.distinct(), many=True)
                return JsonResponse(serializer.data, safe=False)
        # check title, description, type
            else:
                data = search_non_number(search)
                data = data & part_events
                serializer = EventSerializer(data.distinct(), many=True)
                return JsonResponse(serializer.data, safe=False)
        else:
            sub = search.split(",")
            total_data = Event.objects.none()
            for i in range(0, len(sub)):
            # check every field
                if has_numbers(sub[i]):
                    # union set of all events with strings matching query
                    non_number = search_non_number(sub[i])
                    number = search_number(sub[i])
                    data = non_number | number
                    data = data & part_events
                    if not total_data:
                        total_data = data
                    total_data = total_data & data
                    
                # check title, description, type
                else:
                    data = search_non_number(sub[i])
                    data = data & part_events
                    if not total_data:
                        total_data = data
                    total_data = total_data & data
            if total_data:
                print(total_data)
                serializer = EventSerializer(total_data.distinct(), many=True)
                return JsonResponse(serializer.data, safe=False)
            else:
                return HttpResponse("No Data Found",status=400)
    # general filtering for most paths
    else:
        query_set = Event.objects.none()
        is_filtered = False
        if request.GET.get("event_type"):
            # unions set of all event_types
            string = request.GET.get("event_type")
            initial = Event.objects.none()
            if string == "None":
                initial |= Event.objects.filter(deleted=False, event_type="")
                initial |= Event.objects.filter(deleted=False, event_type=None)
            else:
                sub = string.split(",")
                for i in range(0, len(sub)):
                    initial |= Event.objects.filter(deleted=False, event_type=sub[i])
            # intersects them with set of participants and all event_types
            query_set_participant = initial & part_events
            if (not query_set) & (not is_filtered):
                query_set = query_set_participant
            query_set = query_set_participant & query_set
            is_filtered = True

        if request.GET.get("training_session"):
            string = request.GET.get("training_session")
            initial = Event.objects.none()
            if string == "None":
                initial |= Event.objects.filter(deleted=False, training_session=None)
                initial |= Event.objects.filter(deleted=False, training_session="")
            else:
                sub = string.split(",")
                for i in range(0, len(sub)):
                    initial |= Event.objects.filter(deleted=False, training_session=sub[i])
            query_set_participant = initial & part_events
            if (not query_set) & (not is_filtered):
                query_set = query_set_participant
            query_set = query_set_participant & query_set
            is_filtered = True

        if request.GET.get("prog_id"):
            string = request.GET.get("prog_id")
            initial = Event.objects.none()
            if string == "None":
                initial |= Event.objects.filter(deleted=False, prog_id=None)
                initial |= Event.objects.filter(deleted=False, prog_id="")
            else:
                sub = string.split(",")
                for i in range(0, len(sub)):
                    initial |= Event.objects.filter(deleted=False, prog_id=sub[i])
            query_set_participant = initial & part_events
            if (not query_set) & (not is_filtered):
                query_set = query_set_participant
            query_set = query_set_participant & query_set
            is_filtered = True

        if request.GET.get("course_id"):
            string = request.GET.get("course_id")
            initial = Event.objects.none()
            if string == "None":
                initial |= Event.objects.filter(deleted=False, course_id=None)
                initial |= Event.objects.filter(deleted=False, prog_id="")
            else:
                sub = string.split(",")
                for i in range(0, len(sub)):
                    initial |= Event.objects.filter(deleted=False, course_id=int(sub[i]))
            query_set_participant = initial & part_events
            if (not query_set) & (not is_filtered):
                query_set = query_set_participant
            query_set = query_set_participant & query_set
            is_filtered = True

        if is_filtered:
            serializer = EventSerializer(query_set.distinct(), many=True)
            return JsonResponse(serializer.data, safe=False)
        else:
            serializer = EventSerializer(part_events.distinct(), many=True)
            return JsonResponse(serializer.data, safe=False)
        

@api_view(["GET"])
def base_group_instructors(request, event_id, group_id):
    """
        handles event path "events/{event_id}/groups/{group_id}/instructors/
        gets a list of instructors tied to and event
    """
    event_group = EventGroup.objects.get(event_id=event_id, group_id=group_id)
    data = EventGroupInstructor.objects.filter(event_group_id=event_group.event_group_id, deleted=False)
    ser = EventGroupInstructorSerializer(data, many=True)
    return JsonResponse(ser.data, safe=False)


@api_view(["POST", "DELETE"])
def handle_group_instructors(request, event_id, group_id, participant_id):
    """
        handles event path "events/{event_id}/groups/{group_id}/instructors/{participant_id}
        creates event_instructor table instance and deletes it
    """
    if request.method == "POST":
        event_group = EventGroup.objects.get(event_id=event_id, group_id=group_id)
        part = get_object_or_404(Participant, pk=participant_id)
        if part.participant_type == "instructor":
            if EventGroupInstructor.objects.filter(event_group_id=event_group, instructor_id=part).count() == 0:
                new_EGI = EventGroupInstructor(event_group_id=event_group, instructor_id=part)
                new_EGI.full_clean()
                new_EGI.save()
                return HttpResponse("instructor successfully added")
            return HttpResponse("participant with that id already exists", status=status.HTTP_409_CONFLICT)
        else:
            return HttpResponse("participant not an instructor", status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    else:
        event_group = EventGroup.objects.get(event_id=event_id, group_id=group_id)
        part = Participant.objects.get(participant_id=participant_id)
        new_EGI = EventGroupInstructor.objects.get(event_group_id=event_group, instructor_id=part)
        new_EGI.delete()
        return HttpResponse("instructor removed")


# returns every event associated with a particular participant_id
def get_events_from_participant(request):
    """
        returns all the events associated with a participant_id
    """
    participant_ccid = request.GET.get("participant")
    participants = Participant.objects.filter(participant_ccid__icontains=participant_ccid)
    final_events = Event.objects.none()
    for participant in participants:
        if participant.participant_type != "instructor":
            group_part = GroupParticipant.objects.filter(participant_id=participant.participant_id)
            if group_part.count() > 0:
                for i in range(0, len(group_part)):
                    e_groups = EventGroup.objects.filter(group_id=group_part[i].group_id)
                    for x in range(0, len(e_groups)):
                        final_events |= Event.objects.filter(deleted=False, event_id=e_groups[x].event_id.event_id)
        else:
            courses = Course.objects.filter(course_director=participant.participant_id)
            EGI = EventGroupInstructor.objects.filter(instructor_id=participant.participant_id)
            EGI2 = Event.objects.filter(instructors__contains=participant_ccid, deleted=False)
            for i in range(0, len(EGI)):
                final_events |= Event.objects.filter(deleted=False, event_id=EGI[i].event_group_id.event_id.event_id)
            final_events |= EGI2

            for course in courses:
                final_events |= Event.objects.filter(deleted=False, course_id=course.course_id)
    return final_events

@api_view(["GET"])
def get_events_from_participant_ccid(request):
    """
        returns all the events associated with a participant_id
    """
    participant_ccid = request.GET.get("participant")
    participants = Participant.objects.filter(participant_ccid__icontains=participant_ccid)
    final_events = Event.objects.none()
    for participant in participants:
        if participant.participant_type != "instructor":
            group_part = GroupParticipant.objects.filter(participant_id=participant.participant_id)
            if group_part.count() > 0:
                for i in range(0, len(group_part)):
                    e_groups = EventGroup.objects.filter(group_id=group_part[i].group_id)
                    for x in range(0, len(e_groups)):
                        final_events |= Event.objects.filter(deleted=False, event_id=e_groups[x].event_id.event_id)
        else:
            courses = Course.objects.filter(course_director__participant_id__contains=participant.participant_id)
            EGI = EventGroupInstructor.objects.filter(instructor_id=participant.participant_id)
            EGI2 = Event.objects.filter(instructors__contains=participant_ccid, deleted=False)
            for i in range(0, len(EGI)):
                final_events |= Event.objects.filter(deleted=False, event_id=EGI[i].event_group_id.event_id.event_id)
            final_events |= EGI2

            for course in courses:
                final_events |= Event.objects.filter(deleted=False, course_id__course_id__contains=course.course_id)

    serializer = EventSerializer(final_events.distinct(), many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(["GET"])
def get_student_counts_same_location(request):
    locations = Event.objects.all().values('location').distinct()
    start_times = Event.objects.all().values('start_time').distinct()
    event_dates = Event.objects.all().values('event_date').distinct()
    total_result = []
    
    for location in locations:
        for event_date in event_dates:
            for start_time in start_times:
                result = (Event.objects
                    .values_list('location','start_time', 'event_date')
                    .annotate(count=Sum('number_of_students'))
                    .filter(location=location['location'], event_date=event_date['event_date'], start_time=start_time['start_time'])
                    .order_by('start_time')
                )
                if result:
                    total_result.append(result[0])
    return JsonResponse(total_result, safe=False)


@api_view(["POST"])
def generate_zoom_signature(request):
    print(request.data)
    meeting_config = request.data
    ts = int(round(time.time() * 1000)) - 30000;
    msg = '3_AxyIRYRUy25-RterFeuA' + str(meeting_config['meetingNumber']) + str(ts) + str(meeting_config['role'])
    message = base64.b64encode(bytes(msg, 'utf-8'))
    secret = bytes('H5ZI6qOSEDVKfY0w6Ub8UuJ4c1MCtS81Isbp', 'utf-8')
    hash = hmac.new(secret, message, hashlib.sha256)
    hash =  base64.b64encode(hash.digest())
    hash = hash.decode("utf-8")
    tmpString = "%s.%s.%s.%s.%s" % ('3_AxyIRYRUy25-RterFeuA', str(meeting_config['meetingNumber']), str(ts), str(meeting_config['role']), hash)
    signature = base64.b64encode(bytes(tmpString, "utf-8"))
    signature = signature.decode("utf-8")
    print(signature)
    return HttpResponse(signature.rstrip("="))

@api_view(["POST"])
def get_zoom_access_token(request):
    headers = request.data['headers']
    body = request.data['body']
    print('headers: ' + str(headers))
    print('body: ' + str(body))
    url = 'https://zoom.us/oauth/token?code=' + body['code'] + '&grant_type=authorization_code&redirect_uri=http%3A%2F%2Flocalhost%3A3000%2Feventcreate'
    r = requests.post(url, headers=headers)
    return HttpResponse(r)

@api_view(["GET"])
def get_zoom_user_data(request):
    headers = request.headers
    print(headers['Authorization'])
    url = 'https://api.zoom.us/v2/users/me'
    r = requests.get(url, headers={'Authorization':request.headers['Authorization']})
    return HttpResponse(r)

@api_view(["POST"])
def create_zoom_meeting(request):
    print(request.data)
    headers = request.data['headers']
    body = request.data['body']
    email = request.data['user_info']['email']
    url = 'https://api.zoom.us/v2/users/' + email + '/meetings'
    print("User email: " + email)
    r = requests.post(url, headers={'Authorization':headers['Authorization'], 'Content-Type':headers['Content-Type']}, data=body)
    print(r)

    return HttpResponse(r)

# Make a function that retrieves google drive info 
@api_view(["GET"])
def retrieve_google_drive(request):
    event_id = request.GET.get("event_id")
    print(event_id)
    files = get_object_or_404(EventFileAttachment, event_id=event_id)
    serializer = EventFileAttachmentSerializer(files)
    return JsonResponse(serializer.data, safe=False)

# Make a function that retrieves google drive info 
@api_view(["GET"])
def retrieve_instructor_google_drive(request):
    event_id = request.GET.get("event_id")
    print(event_id)
    files = get_object_or_404(EventInstructorFileAttachment, event_id=event_id)
    serializer = EventInstructorFileAttachmentSerializer(files)
    return JsonResponse(serializer.data, safe=False)

@api_view(["DELETE"])
def delete_google_drive_file(request):
    event_file_attachment_id = request.GET.get("event_file_attachment_id")
    file = EventFileAttachment.objects.get(event_file_attachment_id=event_file_attachment_id)
    file.delete()
    return HttpResponse({'result':'file has been removed'})

# Make a function that retrieves google drive info
@api_view(["GET"])
def retrieve_zoom_link(request):
    event_id = request.GET.get("event_id")
    print(event_id)
    zoom_link = get_object_or_404(ZoomMeeting, event_id=event_id)
    serializer = ZoomMeetingSerializer(zoom_link)
    return JsonResponse(serializer.data, safe=False)

