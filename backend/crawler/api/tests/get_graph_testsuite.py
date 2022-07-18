from django.test import TestCase
from rest_framework import status


class GetRecordTest(TestCase):
    fixtures = ['nodes.json']

    def test_get_graph(self):
        response = self.client.get('/api/graph/website/?record=5,6')
        assert 'error' not in response.data
        assert len(response.data) == 2
        assert len(response.data['nodes']) == 8
        assert len(response.data['edges']) == 4

    def test_get_graph_domain(self):
        response = self.client.get('/api/graph/domain/?record=5,6')
        assert 'error' not in response.data
        assert len(response.data) == 2
        assert len(response.data['nodes']) == 3
        assert len(response.data['edges']) == 3

    def test_get_graph_invalid_record(self):
        response = self.client.get('/api/graph/website/')
        assert 'error' in response.data
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_graph_invalid_record_format(self):
        response = self.client.get('/api/graph/domain/?record=potato,tomato/')
        assert 'error' in response.data
        assert response.status_code == status.HTTP_400_BAD_REQUEST
