from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test import Client

from events.models import Event, EventGroup
from courses.models import Course
import json

from groups.models import Group
from participants.models import Participant
from events.views import validate_start_and_end_time, has_numbers

test_events = [{"training_session": "2020-2021",
                "event_type": "Whole Class",
                "event_title": "Pick up Welcome Package& name tags",
                "event_desc": "Welcome",
                "event_date": "2020-08-24",
                "start_time": "08:00:00",
                "end_time": "08:30:00",
                "total_duration": 30},
               {"training_session": "2020-2021",
                "event_type": "Whole Class",
                "event_title": "Pancake Breakfast - All Programs",
                "event_desc": "Pancakes are delicious",
                "event_date": "2020-08-24",
                "start_time": "08:30:00",
                "end_time": "09:30:00",
                "total_duration": 60}]

test_event_groups = [{"location": "2F1.04 WMC (Classroom D)",
                      "vodcast_url": "https://www.ualberta.ca/vodcasts/KXJJ550"}]


class EventsViewsTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        Course.objects.create(course_name="Gastroenterology and Nutrition",
                              course_code="DMED 521", course_objectives="Learn about Gastroenterology and Nutrition",
                              year_level=1,
                              course_overview="An integrated course covering nutrition, gastrointestinal "
                                              "physiology, pathophysiology and anatomy.")
        self.course_id = Course.objects.get(course_name="Gastroenterology and Nutrition").course_id
        Group.objects.create(course_id=Course.objects.get(course_name="Gastroenterology and Nutrition"),
                             group_name="Group 1")
        self.group_id = Group.objects.get(group_name="Group 1").group_id
        # # create an instructor
        Participant.objects.create(participant_id="glefra",
                                   first="Glen",
                                   last="Franks",
                                   participant_type="instructor")
        self.instructor_id = "glefra"

    def test_post_and_look_up_event_successful(self):
        """Test posting an event and looking up that event successfully"""
        self.assertEqual(Event.objects.count(), 0)
        test_event = dict(test_events[0])
        test_event["course_id"] = self.course_id
        post_response = self.client.post('/events/', json.dumps(test_event), content_type="application/json")
        self.assertEqual(post_response.status_code, 200)
        self.assertEqual(post_response.content.decode("utf-8"), "Event successfully added")
        self.assertEqual(Event.objects.count(), 1)

        event_id = json.loads(self.client.get('/events/').content)[0]["event_id"]
        get_response = self.client.get('/events/%d' % event_id)
        self.assertEqual(get_response.status_code, 200)
        test_event["event_id"] = event_id
        test_event["deleted"] = False
        self.assertJSONEqual(get_response.content, test_event)

    def test_look_up_event_does_not_exist_unsuccessful(self):
        """Test looking up that event that does not exist unsuccessfully"""
        self.assertEqual(Event.objects.count(), 0)
        get_response = self.client.get('/events/%d' % 1)
        self.assertEqual(get_response.status_code, 404)

    def test_post_with_course_id_not_provided_unsuccessful(self):
        """Test posting an event where course_id is not provided"""
        self.assertEqual(Event.objects.count(), 0)
        post_response = self.client.post('/events/', json.dumps(test_events[0]), content_type="application/json")
        self.assertEqual(post_response.status_code, 400)
        self.assertEqual(post_response.content.decode("utf-8"), "The field 'course_id' is required")
        self.assertEqual(Event.objects.count(), 0)

    def test_post_with_invalid_course_id_unsuccessful(self):
        """Test posting an event where course_id is for a non-existent course"""
        self.assertEqual(Event.objects.count(), 0)
        test_event = dict(test_events[0])
        test_event["course_id"] = 10000000000
        post_response = self.client.post('/events/', json.dumps(test_event), content_type="application/json")
        self.assertEqual(post_response.status_code, 400)
        self.assertEqual(post_response.content.decode("utf-8"), "Invalid course_id")
        self.assertEqual(Event.objects.count(), 0)

    def test_post_invalid_times_unsuccessful(self):
        """Test posting an event where end time is before start time"""
        self.assertEqual(Event.objects.count(), 0)
        test_event_time = dict(test_events[0])
        test_event_time["start_time"] = "10:00:00"
        test_event_time["course_id"] = self.course_id
        post_response = self.client.post('/events/', json.dumps(test_event_time), content_type="application/json")
        self.assertEqual(post_response.status_code, 400)
        self.assertEqual(post_response.content.decode("utf-8"), "End time cannot be before start time")
        self.assertEqual(Event.objects.count(), 0)

    def test_delete_event_successful(self):
        """Test deleting an event successfully"""
        test_event = dict(test_events[0])
        test_event["course_id"] = self.course_id
        post_response = self.client.post('/events/', json.dumps(test_event), content_type="application/json")
        self.assertEqual(post_response.status_code, 200)
        event_id = json.loads(self.client.get('/events/').content)[0]["event_id"]

        delete_response = self.client.delete('/events/%d' % event_id)
        self.assertEqual(delete_response.status_code, 200)
        self.assertEqual(delete_response.content.decode("utf-8"), "Event successfully deleted")

        get_response = json.loads(self.client.get('/events/').content)
        self.assertFalse(get_response)

    def test_delete_non_existent_event_unsuccessfully(self):
        """Test deleting a non-existent event unsuccessfully"""
        self.assertEqual(Event.objects.count(), 0)
        response = self.client.delete('/events/%d' % 1)
        self.assertEqual(response.status_code, 404)

    def test_add_event_to_deleted_course_unsuccessfully(self):
        """Test adding an event to a deleted course unsuccessfully"""
        self.assertEqual(Event.objects.count(), 0)
        Course.objects.filter(pk=self.course_id).update(deleted=True)

        test_event = dict(test_events[0])
        test_event["course_id"] = self.course_id
        post_response = self.client.post('/events/', json.dumps(test_event), content_type="application/json")
        self.assertEqual(post_response.status_code, 400)
        self.assertEqual(post_response.content.decode("utf-8"), "Invalid course_id")
        self.assertEqual(Event.objects.count(), 0)

    def test_modify_event_successfully(self):
        """Test modifying an event successfully"""
        test_event = dict(test_events[0])
        test_event["course_id"] = self.course_id
        post_response = self.client.post('/events/', json.dumps(test_event), content_type="application/json")
        self.assertEqual(post_response.status_code, 200)
        event_id = json.loads(self.client.get('/events/').content)[0]["event_id"]

        modified_test_event = dict(test_events[0])
        modified_test_event["course_id"] = self.course_id
        modified_test_event["event_date"] = "2020-08-26"
        modified_test_event["event_type"] = Event.EventType.CLINICAL_SKILLS

        put_response = self.client.put('/events/%d' % event_id, json.dumps(modified_test_event), content_type="application/json")
        self.assertEqual(put_response.status_code, 200)
        self.assertEqual(put_response.content.decode("utf-8"), "Event successfully updated")

        modified_test_event["event_id"] = event_id
        modified_test_event["deleted"] = False
        get_response = self.client.get('/events/%d' % event_id)
        self.assertJSONEqual(get_response.content, modified_test_event)

    def test_modify_non_existent_event_unsuccessfully(self):
        """Test modifying a non-existent event unsuccessfully"""
        modified_test_event = dict(test_events[0])
        modified_test_event["course_id"] = self.course_id
        modified_test_event["event_date"] = "2020-08-26"

        put_response = self.client.put('/events/%d' % 1, json.dumps(modified_test_event), content_type="application/json")
        self.assertEqual(put_response.status_code, 404)

    def test_modify_deleted_event_unsuccessfully(self):
        """Test modifying a deleted event unsuccessfully"""
        test_event = dict(test_events[0])
        test_event["course_id"] = self.course_id
        post_response = self.client.post('/events/', json.dumps(test_event), content_type="application/json")
        event_id = json.loads(self.client.get('/events/').content)[0]["event_id"]

        delete_response = self.client.delete('/events/%d' % event_id)
        self.assertEqual(delete_response.content.decode("utf-8"), "Event successfully deleted")

        modified_test_event = dict(test_events[0])
        modified_test_event["course_id"] = self.course_id
        modified_test_event["event_type"] = Event.EventType.CLINICAL_SKILLS
        put_response = self.client.put('/events/%d' % event_id, json.dumps(modified_test_event),
                                       content_type="application/json")
        self.assertEqual(put_response.status_code, 404)

    def test_modify_with_invalid_course_id_unsuccessfully(self):
        """Test modifying a event with invalid course_id unsuccessfully"""
        test_event = dict(test_events[0])
        test_event["course_id"] = self.course_id
        post_response = self.client.post('/events/', json.dumps(test_event), content_type="application/json")
        self.assertEqual(post_response.content.decode("utf-8"), "Event successfully added")
        event_id = json.loads(self.client.get('/events/').content)[0]["event_id"]

        modified_test_event = dict(test_events[0])
        modified_test_event["course_id"] = 100000
        put_response = self.client.put('/events/%d' % event_id, json.dumps(modified_test_event),
                                       content_type="application/json")
        self.assertEqual(put_response.status_code, 400)
        self.assertEqual(put_response.content.decode("utf-8"), "Invalid course_id")

    def test_modify_with_deleted_course_id_unsuccessfully(self):
        """Test modifying a event with deleted course_id unsuccessfully"""
        self.assertEqual(Event.objects.count(), 0)

        Course.objects.create(course_name="Reproductive Medicine and Urology",
                              course_code="DMED 522", course_objectives="Learn about Reproductive Medicine and Urology",
                              year_level=2,
                              course_overview="An overview of reproductive medicine in both genders, including "
                                              "discussion of conception, pregnancy and fetal development, birth, "
                                              "reproductive technology and relevant health-related issues.")
        mod_course_id = Course.objects.get(course_name="Reproductive Medicine and Urology").course_id
        Course.objects.filter(pk=mod_course_id).update(deleted=True)

        test_event = dict(test_events[0])
        test_event["course_id"] = self.course_id
        post_response = self.client.post('/events/', json.dumps(test_event), content_type="application/json")
        self.assertEqual(post_response.content.decode("utf-8"), "Event successfully added")
        event_id = json.loads(self.client.get('/events/').content)[0]["event_id"]

        modified_test_event = dict(test_events[0])
        modified_test_event["course_id"] = mod_course_id

        put_response = self.client.put('/events/%d' % event_id, json.dumps(modified_test_event),
                                       content_type="application/json")
        self.assertEqual(put_response.status_code, 400)
        self.assertEqual(put_response.content.decode("utf-8"), "Invalid course_id")

    def test_modify_with_invalid_times_unsuccessfully(self):
        """Test modifying a event with end time before start time unsuccessfully"""
        test_event = dict(test_events[0])
        test_event["course_id"] = self.course_id
        post_response = self.client.post('/events/', json.dumps(test_event), content_type="application/json")
        self.assertEqual(post_response.status_code, 200)
        event_id = json.loads(self.client.get('/events/').content)[0]["event_id"]

        modified_test_event = dict(test_events[0])
        modified_test_event["course_id"] = self.course_id
        modified_test_event["start_time"] = "12:00:00"

        put_response = self.client.put('/events/%d' % event_id, json.dumps(modified_test_event),
                                       content_type="application/json")
        self.assertEqual(put_response.status_code, 400)
        self.assertEqual(put_response.content.decode("utf-8"), "End time cannot be before start time")

    def test_add_group_to_event_and_get_event_group_successfully(self):
        """Test adding a group to an event and get event group successfully"""
        self.assertEqual(EventGroup.objects.count(), 0)

        test_event = dict(test_events[0])
        test_event["course_id"] = self.course_id
        post_response = self.client.post('/events/', json.dumps(test_event), content_type="application/json")
        self.assertEqual(post_response.content.decode("utf-8"), "Event successfully added")

        event_id = json.loads(self.client.get('/events/').content)[0]["event_id"]

        test_event_group = dict(test_event_groups[0])

        post_group_response = self.client.post('/events/%d/groups/%d/' % (event_id, self.group_id),
                                               json.dumps(test_event_group),
                                               content_type="application/json")
        self.assertEqual(post_group_response.status_code, 200)
        self.assertEqual(EventGroup.objects.count(), 1)

        event_group_id = EventGroup.objects.get(event_id=event_id, group_id=self.group_id).event_group_id

        test_event_group["group_id"] = self.group_id
        test_event_group["event_group_id"] = event_group_id
        test_event_group["event_id"] = event_id
        test_event_group["deleted"] = False

        get_response = self.client.get('/events/%d/groups/' % event_id)
        self.assertEqual(get_response.status_code, 200)
        self.assertJSONEqual(get_response.content, [test_event_group])

    def test_validate_start_end_time_start_before_end(self):
        """"Test validate_start_end_time with start time before end time"""
        start_time = "08:00:00"
        end_time = "09:00:00"
        minutes_between = validate_start_and_end_time(start_time, end_time)
        self.assertEqual(minutes_between, 60)

    def test_validate_start_end_time_equal(self):
        """"Test validate_start_end_time with start time the same as end time"""
        start_time = "08:00:00"
        end_time = "08:00:00"
        minutes_between = validate_start_and_end_time(start_time, end_time)
        self.assertEqual(minutes_between, 0)

    def test_validate_start_end_time_end_before_start(self):
        """"Test validate_start_end_time with end time before start time"""
        start_time = "09:00:00"
        end_time = "08:00:00"
        with self.assertRaises(ValidationError):
            validate_start_and_end_time(start_time, end_time)

    def test_has_numbers_numbers_only(self):
        """"Test has_numbers with a string of numbers only"""
        input_string = "4554"
        self.assertTrue(has_numbers(input_string))

    def test_has_numbers_number_only(self):
        """"Test has_numbers with a string of one number only"""
        input_string = "4"
        self.assertTrue(has_numbers(input_string))

    def test_has_numbers_number_and_chars(self):
        """"Test has_numbers with a string of numbers and characters"""
        input_string = "45aaa54bbb"
        self.assertTrue(has_numbers(input_string))

    def test_has_numbers_chars_and_symbols(self):
        """"Test has_numbers with a string of characters and symbols"""
        input_string = "fg%@!:-?]"
        self.assertFalse(has_numbers(input_string))

    def test_has_numbers_chars_only(self):
        """"Test has_numbers with a string of characters only"""
        input_string = "abcdddd"
        self.assertFalse(has_numbers(input_string))

    def test_has_numbers_symbols_only(self):
        """"Test has_numbers with a string of symbols only"""
        input_string = "44$$2@"
        self.assertTrue(has_numbers(input_string))

    def test_has_numbers_empty_string(self):
        """"Test has_numbers with an empty string"""
        input_string = ""
        self.assertFalse(has_numbers(input_string))
