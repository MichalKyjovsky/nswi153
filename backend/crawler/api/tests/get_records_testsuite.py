from django.test import TestCase


class GetRecordsTest(TestCase):
    fixtures = ['basic.json']

    def test_get_records(self):
        response = self.client.get('/api/record/1/')
        assert 'error' not in response.data
        assert len(response.data) == 3
        assert len(response.data['records']) == 2
        assert len(response.data['records'][0]) > 0

    def test_get_records_by_tag(self):
        response = self.client.get('/api/record/1/?tag-filter=a')
        assert 'error' not in response.data
        assert len(response.data) == 3
        assert len(response.data['records']) == 1
        assert len(response.data['records'][0]) > 0

    def test_get_records_set_page_size(self):
        response = self.client.get('/api/record/2/?page_size=1')
        assert 'error' not in response.data
        assert len(response.data) == 3
        assert len(response.data['records']) == 1
        assert len(response.data['records'][0]) > 0
        assert response.data['total_pages'] == 2
        assert response.data['total_records'] == 2

    def test_get_records_invalid_page(self):
        response = self.client.get('/api/record/3/')
        assert 'error' in response.data

    def test_get_records_by_url(self):
        response = self.client.get('/api/record/1/?url-filter=http://www.google.com')
        assert 'error' not in response.data
        assert len(response.data) == 3
        assert len(response.data['records']) == 1

    def test_get_records_by_label(self):
        response = self.client.get('/api/record/1/?label-filter=amazon_crawl')
        assert 'error' not in response.data
        assert len(response.data['records']) == 1
        assert len(response.data['records'][0]) > 0

    def test_get_records_by_url_and_label(self):
        response = self.client.get('/api/record/1/?url-filter=http://www.amazon.com&label-filter=amazon_crawl')
        assert 'error' not in response.data
        assert len(response.data) == 3
        assert len(response.data['records']) == 1

    def test_get_records_empty_result(self):
        response = self.client.get('/api/record/1/?url-filter=http://www.amazon.com&label-filter=my_label')
        assert 'error' not in response.data
        assert len(response.data) == 3
        assert len(response.data['records']) == 0

    def test_get_records_sort_label(self):
        response = self.client.get('/api/record/1/?sort_property=label&sort_order=desc')
        assert 'error' not in response.data
        assert len(response.data) == 3
        assert len(response.data['records']) == 2
        assert len(response.data['records'][0]) > 0
        assert 'google' in response.data['records'][0]['fields']['url']

    def test_get_records_sort_url(self):
        response = self.client.get('/api/record/1/?sort_property=url&sort_order=desc')
        assert 'error' not in response.data
        assert len(response.data) == 3
        assert len(response.data['records']) == 2
        assert len(response.data['records'][0]) > 0
        assert 'google' in response.data['records'][0]['fields']['url']

    def test_get_records_sort_last_crawl(self):
        response = self.client.get('/api/record/1/?sort_property=last_crawl&sort_order=desc')
        assert 'error' not in response.data
        assert len(response.data) == 3
        assert len(response.data['records']) == 2
        assert len(response.data['records'][0]) > 0
        assert 'google' in response.data['records'][0]['fields']['url']

    def test_get_records_sort_wrong_property(self):
        response = self.client.get('/api/record/1/?sort_property=potato&sort_order=desc')
        assert 'error' not in response.data
        assert len(response.data) == 3
        assert len(response.data['records']) == 2
        assert len(response.data['records'][0]) > 0
        assert 'amazon' in response.data['records'][0]['fields']['url']
