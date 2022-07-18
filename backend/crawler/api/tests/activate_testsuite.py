from django.test import TestCase
from api.models import WebsiteRecord

content_type = "application/json"


class ActivateRecordTest(TestCase):
    fixtures = ['basic.json']

    def test_activate_valid_record(self):
        request_data = {'id': 6, 'active': True}
        response = self.client.put('/api/record/', data=request_data, content_type=content_type)
        assert 'message' in response.data
        assert WebsiteRecord.objects.filter(pk=6).first().active

    def test_activate_invalid_record(self):
        request_data = {'id': 777, 'active': True}
        response = self.client.put('/api/record/', data=request_data, content_type=content_type)
        assert 'error' in response.data
