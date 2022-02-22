from django.test import TestCase
from django.test import Client
from django.urls import reverse
from courses.models import Course
from groups.models import Group
import datetime
import json

test_groups = [{"group_name": "Group 1"}]


class GroupsViewsTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        Course.objects.create(course_name="Gastroenterology and Nutrition",
                              year_level=1,
                              course_code="DMED 521", course_objectives="Learn about Gastroenterology and Nutrition",
                              course_overview="An integrated course covering nutrition, gastrointestinal "
                                              "physiology, pathophysiology and anatomy.")
        self.course_id = Course.objects.get(course_name="Gastroenterology and Nutrition").course_id

    def test_post_and_look_up_group_successful(self):
        """Test posting a group and looking up that group successfully"""
        self.assertEqual(Group.objects.count(), 0)
        test_group = test_groups[0]
        test_group["course_id"] = self.course_id
        post_response = self.client.post('/groups/', json.dumps(test_group), content_type="application/json")
        self.assertEqual(post_response.status_code, 200)
        self.assertEqual(Group.objects.count(), 1)

        group_id = json.loads(self.client.get('/groups/').content)[0]["group_id"]
        get_response = self.client.get('/groups/%d' % group_id)
        self.assertEqual(get_response.status_code, 200)
        test_group["group_id"] = group_id
        test_group["deleted"] = False
        self.assertJSONEqual(get_response.content, test_group)
