from django.test import TestCase
from api.models import WebsiteRecord


test_url = '/api/record/delete/'


class DeleteRecordTest(TestCase):
    fixtures = ['basic.json']

    def test_delete_valid_record(self):
        response = self.client.delete(test_url, data={"record_id": 5}, content_type="application/json")
        assert 'message' in response.data
        assert len(WebsiteRecord.objects.filter(pk=5)) == 0

    def test_delete_invalid_record(self):
        response = self.client.delete(test_url, data={"record_id": 777}, content_type="application/json")
        assert 'error' in response.data

    def test_delete_no_record(self):
        response = self.client.delete(test_url)
        assert 'error' in response.data
