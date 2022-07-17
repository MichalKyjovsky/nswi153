from django.test import TestCase
from rest_framework import status


class GetRecordTest(TestCase):
    fixtures = ['nodes.json']

    def test_get_graph(self):
        response = self.client.get('/api/graph/5/')
        assert 'error' not in response.data
        assert len(response.data) == 2
        assert len(response.data['nodes']) == 4
        assert len(response.data['edges']) == 3

    def test_get_graph_invalid_record(self):
        response = self.client.get('/api/graph/7/')
        assert 'error' in response.data
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_graph_invalid_record_format(self):
        response = self.client.get('/api/graph/potato/')
        assert 'error' in response.data
        assert response.status_code == status.HTTP_400_BAD_REQUEST
