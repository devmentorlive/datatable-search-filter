import json

from django.http import JsonResponse
from django.test import TestCase
from rest_framework.test import APIClient

from courses.models import Course, CourseParticipant
from events.events_serializer import EventSerializer
from events.models import Event
from participants.models import Participant
from participants.participants_serializer import ParticipantSerializer

test_participants = [{"participant_id": "imagib", "participant_type": "student",
                      "first": "Imaad", "last": "Gibbons"},
                     {"participant_id": "kelboy", "participant_type": "student",
                      "first": "Kelis", "last": "Boyle"},
                     {"participant_id": "tifdea", "participant_type": "student",
                      "first": "Tiffany", "last": "Dean"}]

test_courses = [{"course_name": "Gastroenterology and Nutrition",
                 "course_code": "DMED 521",
                 "year_level": 1,
                 "course_objectives": "Learn about Gastroenterology and Nutrition",
                 "course_overview": "An integrated course covering nutrition, gastrointestinal "
                                    "physiology, pathophysiology and anatomy."},
                {"course_name": "Pulmonary System", "course_code": "DMED 516",
                 "year_level": 1,
                 "course_objectives": "Learn about Pulmonary System",
                 "course_overview": "The normal function of the lungs, the changes in these functions which occur in disease and the "
                                    "management of the conditions which result from such changes in function."}
                ]

test_events = [{"training_session": "2020-2021",
                "event_type": "Whole Class",
                "event_title": "Pick up Welcome Package& name tags",
                "event_date": "2020-08-24",
                "start_time": "08:00:00",
                "end_time": "08:30:00",
                "total_duration": 30},
               {"training_session": "2020-2021",
                "event_type": "Whole Class",
                "event_title": "Pancake Breakfast - All Programs",
                "event_date": "2020-08-24",
                "start_time": "08:30:00",
                "end_time": "09:30:00",
                "total_duration": 60}]


def create_participant(participant):
    NewParticipant = Participant(participant_id=test_participants[participant]["participant_id"],
                                 participant_type=test_participants[participant]["participant_type"],
                                 first=test_participants[participant]["first"],
                                 last=test_participants[participant]["last"])
    NewParticipant.save()
    serializer = ParticipantSerializer(NewParticipant)
    return JsonResponse(serializer.data, safe=False)


def create_event(event, course_id):
    NewEvent = Event()
    course = Course.objects.get(course_id=course_id)
    NewEvent.course_id = course
    for k, v in test_events[event].items():
        setattr(NewEvent, k, v)
    NewEvent.save()
    serializer = EventSerializer(NewEvent)
    return JsonResponse(serializer.data, safe=False)


class CoursesTestCases(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_post_and_look_up_course_successful(self):
        """Test posting a course and looking up that course successfully"""
        self.assertEqual(Course.objects.count(), 0)
        post_response = self.client.post('/courses/', json.dumps(test_courses[0]), content_type="application/json")
        self.assertEqual(post_response.status_code, 200)
        self.assertEqual(Course.objects.count(), 1)

        course_id = json.loads(self.client.get('/courses/').content)[0]["course_id"]
        get_response_content = json.loads(self.client.get('/courses/%d' % course_id).content)
        self.assertEqual(get_response_content["course_name"], test_courses[0]["course_name"])

    def test_view_courses_successful(self):
        """Test posting 2 courses successfully and calling GET /courses/"""
        self.assertEqual(Course.objects.count(), 0)
        post_response_1 = self.client.post('/courses/', json.dumps(test_courses[0]), content_type="application/json")
        self.assertEqual(post_response_1.status_code, 200)
        post_response_2 = self.client.post('/courses/', json.dumps(test_courses[1]), content_type="application/json")
        self.assertEqual(post_response_2.status_code, 200)
        self.assertEqual(Course.objects.count(), 2)

        get_response_content = json.loads(self.client.get('/courses/').content)

        self.assertEqual(len(get_response_content), 2)
        self.assertEqual(get_response_content[0]["course_name"], test_courses[0]["course_name"])
        self.assertEqual(get_response_content[1]["course_name"], test_courses[1]["course_name"])

    def test_put_course_unsuccessful(self):
        """Test calling PUT on open_path(request) which should return an error"""
        response = self.client.put('/courses/')
        expected_response = b'{"detail":"Method \\"PUT\\" not allowed."}'
        self.assertEqual(response.content, expected_response)

    def test_view_look_up_course_empty(self):
        """Test look up course when course does not exist"""
        with self.assertRaises(Course.DoesNotExist):
            self.client.get('/courses/1')

    def test_put_course_unsuccessful_with_id(self):
        # TODO: Implement editing a course
        """Test calling PUT on open_path(request) which should return an error"""
        response = self.client.post('/courses/1')
        expected_response = b'{"detail":"Method \\"POST\\" not allowed."}'
        self.assertEqual(response.content, expected_response)

    def test_post_participant_to_course(self):
        """Test posting a participant to a course"""
        # Add participant to database
        create_participant_response = create_participant(0)
        self.assertEqual(create_participant_response.status_code, 200)
        self.assertEqual(Participant.objects.count(), 1)

        # Add course to database
        post_course_response = self.client.post('/courses/', json.dumps(test_courses[0]), content_type="application/json")
        self.assertEqual(post_course_response.status_code, 200)

        # Add course participant
        course_id = json.loads(self.client.get('/courses/').content)[0]["course_id"]
        post_course_participant_response = self.client.post('/courses/%d/participants/imagib' % course_id)
        self.assertEqual(post_course_participant_response.status_code, 200)
        self.assertEqual(CourseParticipant.objects.count(), 1)

    def test_post_non_existent_participant_to_course(self):
        """Test posting a non-existent participant to a course unsuccessfully"""
        post_course_response = self.client.post('/courses/',
                                                json.dumps(test_courses[0]),
                                                content_type="application/json")
        self.assertEqual(post_course_response.status_code, 200)

        course_id = list(Course.objects.values_list("course_id", flat=True))[0]
        post_course_participant_response = self.client.post('/courses/%d/participants/abcdef' % course_id)
        self.assertEqual(post_course_participant_response.status_code, 400)
        self.assertEqual(post_course_participant_response.content.decode("utf-8"),
                         "Participant with participant_id=abcdef does not exist. ")
        self.assertEqual(CourseParticipant.objects.count(), 0)

    def test_post_participant_to_non_existent_course(self):
        """Test posting a participant to a non-existent course unsuccessfully"""
        # Add participant to database
        create_participant_response = create_participant(0)
        self.assertEqual(create_participant_response.status_code, 200)

        post_course_participant_response = self.client.post('/courses/10000000000/participants/%s' % test_participants[0]["participant_id"])
        self.assertEqual(post_course_participant_response.status_code, 400)
        self.assertEqual(post_course_participant_response.content.decode("utf-8"),
                         "Course with course_id=10000000000 does not exist. ")
        self.assertEqual(CourseParticipant.objects.count(), 0)

    def test_get_course_participants_successfully(self):
        """Test getting course participants successfully"""
        # Add participant 1 to database
        create_participant_response = create_participant(0)
        self.assertEqual(create_participant_response.status_code, 200)

        # Add participant 2 to database
        create_participant_response = create_participant(1)
        self.assertEqual(create_participant_response.status_code, 200)

        # Add participant 3 to database
        create_participant_response = create_participant(2)
        self.assertEqual(create_participant_response.status_code, 200)

        self.assertEqual(Participant.objects.count(), 3)

        # Add course to database
        post_course_response = self.client.post('/courses/', json.dumps(test_courses[0]),
                                                content_type="application/json")
        self.assertEqual(post_course_response.status_code, 200)
        self.assertEqual(Course.objects.count(), 1)

        # Add two course participants
        course_id = json.loads(self.client.get('/courses/').content)[0]["course_id"]
        post_course_participant_response = self.client.post('/courses/%d/participants/%s' %
                                                            (course_id, test_participants[0]["participant_id"]))
        self.assertEqual(post_course_participant_response.status_code, 200)
        post_course_participant_response = self.client.post('/courses/%d/participants/%s' %
                                                            (course_id, test_participants[1]["participant_id"]))
        self.assertEqual(post_course_participant_response.status_code, 200)
        self.assertEqual(CourseParticipant.objects.count(), 2)

        # Make sure only two course participants are added and not all 3 participants added
        get_course_participant_response = self.client.get('/courses/%d/participants/' % course_id)
        self.assertEqual(get_course_participant_response.status_code, 200)
        test_participant_0 = test_participants[0]
        test_participant_0["deleted"] = False
        test_participant_1 = test_participants[1]
        test_participant_1["deleted"] = False
        self.assertJSONEqual(get_course_participant_response.content, [test_participants[0], test_participants[1]])

    def test_get_course_events_successfully(self):
        """Test getting course events successfully"""
        # Add course to database
        post_course_response = self.client.post('/courses/', json.dumps(test_courses[0]),
                                                content_type="application/json")
        self.assertEqual(post_course_response.status_code, 200)
        self.assertEqual(Course.objects.count(), 1)
        course_id = json.loads(self.client.get('/courses/').content)[0]["course_id"]

        # Add event 1 to database
        create_participant_response = create_event(0, course_id)
        self.assertEqual(create_participant_response.status_code, 200)

        # Add event 2 to database
        create_participant_response = create_event(1, course_id)
        self.assertEqual(create_participant_response.status_code, 200)
        self.assertEqual(Event.objects.count(), 2)

        get_course_events_response = self.client.get('/courses/%d/events/' % course_id)
        self.assertEqual(get_course_events_response.status_code, 200)
        exp_event_title_1 = json.loads(get_course_events_response.content)[0]["event_title"]
        exp_event_title_2 = json.loads(get_course_events_response.content)[1]["event_title"]
        self.assertEqual(exp_event_title_1, test_events[0]["event_title"])
        self.assertEqual(exp_event_title_2, test_events[1]["event_title"])
