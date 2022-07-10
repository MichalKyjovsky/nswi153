from django.test import TestCase
from api.models import WebsiteRecord, Tag


request_url = '/api/record/add/'
content_type = "application/json"


class AddRecordTest(TestCase):
    fixtures = ['empty.json']

    def test_add_valid_record(self):
        request_data = {"url": "www.google.com", "label": "test", "interval": 120, "active": False, "regex": ".+",
                        "tags": "a,b,1"}
        response = self.client.put(request_url, data=request_data, content_type=content_type)
        assert 'message' in response.data
        assert len(WebsiteRecord.objects.filter(label='test')) > 0
        record = WebsiteRecord.objects.filter(label='test').first()
        assert len(Tag.objects.filter(websiterecord=record)) == 3

    def test_add_valid_record_no_tags(self):
        request_data = {"url": "www.google.com", "label": "test", "interval": 120, "active": False, "regex": ".+"}
        response = self.client.put(request_url, data=request_data, content_type=content_type)
        assert 'message' in response.data
        assert len(WebsiteRecord.objects.filter(label='test')) > 0
        record = WebsiteRecord.objects.filter(label='test')[0]
        assert len(Tag.objects.filter(websiterecord=record)) == 0

    def test_add_invalid_record_label(self):
        request_data = {"url": "www.google.com", "label": "", "interval": 120, "active": False, "regex": ".+",
                        "tags": "a,b,1"}
        response = self.client.put(request_url, data=request_data, content_type=content_type)
        assert 'error' in response.data
        assert len(WebsiteRecord.objects.filter(url='www.google.com')) == 0
        assert len(Tag.objects.all()) == 0

    def test_add_invalid_record_url(self):
        request_data = {"url": "", "label": "test", "interval": 120, "active": False, "regex": ".+",
                        "tags": "a,b,1"}
        response = self.client.put(request_url, data=request_data, content_type=content_type)
        assert 'error' in response.data
        assert len(WebsiteRecord.objects.filter(label='test')) == 0
        assert len(Tag.objects.all()) == 0

    def test_add_invalid_record_interval(self):
        request_data = {"url": "www.google.com", "label": "test", "interval": -120, "active": False, "regex": ".+",
                        "tags": "a,b,1"}
        response = self.client.put(request_url, data=request_data, content_type=content_type)
        assert 'error' in response.data
        assert len(WebsiteRecord.objects.filter(label='test')) == 0
        assert len(Tag.objects.all()) == 0

    def test_add_invalid_record_regex(self):
        request_data = {"url": "www.google.com", "label": "test", "interval": 120, "active": False,
                        "tags": "a,b,1"}
        response = self.client.put(request_url, data=request_data, content_type=content_type)
        assert 'error' in response.data
        assert len(WebsiteRecord.objects.filter(label='test')) == 0
        assert len(Tag.objects.all()) == 0
