from django.test import TestCase
from ..models import WebsiteRecord


class ActivateRecordTest(TestCase):
    fixtures = ['basic.json']

    def test_activate_valid_record(self):
        response = self.client.put('/api/activate/6/')
        assert 'message' in response.data
        assert WebsiteRecord.objects.filter(pk=6)[0].status == 1

    def test_activate_invalid_record(self):
        response = self.client.put('/api/activate/777/')
        assert 'error' in response.data
