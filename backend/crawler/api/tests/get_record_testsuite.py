from django.test import TestCase
from rest_framework import status


class GetRecordTest(TestCase):
    fixtures = ['basic.json']

    def test_get_valid_record(self):
        response = self.client.get('/api/record/?record=5')
        assert 'error' not in response.data
        assert len(response.data) == 1
        assert response.data[0]['fields']['label'] == 'my_label'
        assert len(response.data[0]['fields']['tags']) == 3
        assert 'b' in response.data[0]['fields']['tags']

    def test_get_invalid_record(self):
        response = self.client.get('/api/record/?record=666')
        assert 'error' in response.data
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_invalid_record_id_type(self):
        response = self.client.get('/api/record/?record=abc')
        assert 'error' in response.data
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_no_record_id(self):
        response = self.client.get('/api/record/?potato=rotten')
        assert 'error' in response.data
        assert response.status_code == status.HTTP_400_BAD_REQUEST