from django.test import TestCase


class GetExecutionTest(TestCase):
    fixtures = ['basic.json']

    def test_get_execution(self):
        response = self.client.get('/api/execution/5/1/')
        assert 'error' not in response.data
        assert len(response.data) == 3

    def test_get_execution_paginated(self):
        response = self.client.get('/api/execution/5/2/?page_size=2')
        assert 'error' not in response.data
        assert len(response.data['executions']) == 1
        assert response.data['total_records'] == 3
        assert response.data['total_pages'] == 2

    def test_get_invalid_execution(self):
        response = self.client.get('/api/execution/777/1/')
        assert 'error' in response.data

    def test_get_invalid_execution_wrong_format(self):
        response = self.client.get('/api/execution/abc/1/')
        assert 'error' in response.data

    def test_invalid_page(self):
        response = self.client.get('/api/execution/5/40/')
        assert 'error' in response.data
