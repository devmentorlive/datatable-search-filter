import json

from django.test import Client
from django.test import TestCase

from participants.models import Participant

test_participants = [{"participant_id": "imagib", "participant_type": "student",
                      "first": "Imaad", "last": "Gibbons"},
                     {"participant_id": "kelboy", "participant_type": "student",
                      "first": "Kelis", "last": "Boyle"},
                     {"participant_id": "tifdea", "participant_type": "student",
                      "first": "Tiffany", "last": "Dean"}]


class ParticipantViewsTestCase(TestCase):

    def setUp(self):
        self.client = Client()

    def test_post_and_look_up_participant_successful(self):
        """Test posting a participant and looking up that participant successfully"""
        self.assertEqual(Participant.objects.count(), 0)
        post_response = self.client.post('/participants/', json.dumps(test_participants[0]), content_type="application/json")
        self.assertEqual(post_response.status_code, 200)
        self.assertEqual(Participant.objects.count(), 1)

        participant_id = test_participants[0]["participant_id"]
        get_response = self.client.get('/participants/%s' % participant_id)
        self.assertEqual(get_response.status_code, 200)
        test_participant = test_participants[0]
        test_participant["deleted"] = False
        self.assertJSONEqual(get_response.content, test_participant)

    def test_retrieving_deleted_participant(self):
        """Test retrieving a participant that has been deleted unsuccessfully"""
        pass

    def test_add_participant_with_invalid_participant_type(self):
        """Test posting a participant with an invalid participant type unsuccessfully"""
        pass
