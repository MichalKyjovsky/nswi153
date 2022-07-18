from django.test import TestCase
from api.models import WebsiteRecord

content_type = "application/json"


class DeactivateRecordTest(TestCase):
    fixtures = ['basic.json']

    def test_deactivate_valid_record(self):
        request_data = {'id': 5, 'active': False}
        response = self.client.put('/api/record/', data=request_data, content_type=content_type)
        assert 'message' in response.data
        assert not WebsiteRecord.objects.filter(pk=5)[0].active

    def test_deactivate_invalid_record(self):
        request_data = {'id': 777, 'active': False}
        response = self.client.put('/api/record/', data=request_data, content_type=content_type)
        assert 'error' in response.data
