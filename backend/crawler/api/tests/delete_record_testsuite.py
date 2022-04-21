from django.test import TestCase
from ..models import WebsiteRecord


class DeleteRecordTest(TestCase):
    fixtures = ['basic.json']

    def test_delete_valid_record(self):
        response = self.client.delete('/api/record/delete/', data={"record_id": 5}, content_type="application/json")
        assert 'message' in response.data
        assert len(WebsiteRecord.objects.filter(pk=5)) == 0

    def test_delete_invalid_record(self):
        response = self.client.delete('/api/record/delete/', data={"record_id": 777}, content_type="application/json")
        assert 'error' in response.data

    def test_delete_no_record(self):
        response = self.client.delete('/api/record/delete/')
        assert 'error' in response.data
