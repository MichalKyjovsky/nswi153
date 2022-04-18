from django.test import TestCase


class GetExecutionsTest(TestCase):
    fixtures = ['basic.json']

    def test_get_executions(self):
        response = self.client.get('/api/executions/1/')
        assert 'error' not in response.data
        assert len(response.data['executions']) == 5

    def test_get_executions_invalid_page(self):
        response = self.client.get('/api/executions/55/')
        assert 'error' in response.data

    def test_get_executions_invalid_page_format(self):
        """ Should return first 10 results in page 1. """
        response = self.client.get('/api/executions/abc/')
        assert 'error' not in response.data
        assert len(response.data['executions']) == 5

    def test_get_executions_defined_page_size(self):
        response = self.client.get('/api/executions/2/?page_size=2')
        assert 'error' not in response.data
        assert len(response.data['executions']) == 2
        assert response.data['total_records'] == 5
        assert response.data['total_pages'] == 3
