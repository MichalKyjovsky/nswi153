from django.test import TestCase
from core.model.DataModel import WebsiteRecord


class DeactivateRecordTest(TestCase):
    fixtures = ['basic.json']

    def test_deactivate_valid_record(self):
        response = self.client.put('/api/deactivate/5/')
        assert 'message' in response.data
        assert WebsiteRecord.objects.filter(pk=5)[0].status == 0

    def test_deactivate_invalid_record(self):
        response = self.client.put('/api/deactivate/777/')
        assert 'error' in response.data
