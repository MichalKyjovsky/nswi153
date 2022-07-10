from django.test import TestCase
from api.models import WebsiteRecord, Tag
from rest_framework import status
import json

request_url = '/api/record/update/'


class UpdateRecordTest(TestCase):
    fixtures = ['basic.json']

    def test_valid_update_remove_tags(self):
        request_data = {'id': 5, "label": "test", "tags": "a,b"}
        response = self.client.post(request_url, data=request_data)
        assert 'message' in response.data
        assert len(WebsiteRecord.objects.filter(label='test')) > 0
        record = WebsiteRecord.objects.filter(label='test').first()
        assert len(Tag.objects.filter(websiterecord=record)) == 2

    def test_valid_update_add_tags(self):
        request_data = {'id': 5, "label": "test", "tags": "a,b,c,d,e"}
        response = self.client.post(request_url, data=request_data)
        assert 'message' in response.data
        assert len(WebsiteRecord.objects.filter(label='test')) > 0
        record = WebsiteRecord.objects.filter(label='test').first()
        assert len(Tag.objects.filter(websiterecord=record)) == 5

    def test_invalid_property_update(self):
        request_data = {'id': 5, "potato": "rotten"}
        response = self.client.post(request_url, data=request_data)
        assert 'message' in response.data
        assert 'potato' not in WebsiteRecord.objects.filter(pk=5)[0].__dict__

    def test_invalid_value_update(self):
        request_data = {'id': 5, "interval": -555}
        response = self.client.post(request_url, data=request_data)
        assert 'error' in response.data
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_id_update_numeric(self):
        request_data = {'id': 1, "label": "test", "tags": "a,b"}
        response = self.client.post(request_url, data=request_data)
        assert 'error' in response.data
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_no_id_update(self):
        request_data = {"label": "test"}
        response = self.client.post(request_url, data=request_data)
        assert 'error' in response.data
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_id_update_non_numeric(self):
        request_data = {'id': 'abcde', "label": "test", "tags": "a,b"}
        response = self.client.post(request_url, data=request_data)
        assert 'error' in response.data
        assert response.status_code == status.HTTP_400_BAD_REQUEST