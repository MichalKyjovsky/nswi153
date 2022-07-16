from django.test import TestCase


class ListRecordsTest(TestCase):
    fixtures = ['basic.json']

    def test_list_records(self):
        response = self.client.get('/api/record/list/')
        assert 'error' not in response.data
        assert len(response.data['records']) == 2
