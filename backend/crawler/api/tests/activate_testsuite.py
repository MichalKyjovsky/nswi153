from django.test import TestCase
from api.models import WebsiteRecord


class ActivateRecordTest(TestCase):
    fixtures = ['basic.json']

    def test_activate_valid_record(self):
        response = self.client.put('/api/activate/6/')
        assert 'message' in response.data
        assert not WebsiteRecord.objects.filter(pk=6)[0].active

    def test_activate_invalid_record(self):
        response = self.client.put('/api/activate/777/')
        assert 'error' in response.data
