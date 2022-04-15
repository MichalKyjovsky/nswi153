from django.db import models
import json


class WebsiteRecordManager(models.Manager):
    fields = ('url', 'label', 'interval', 'status', 'regex')

    def valid_record_data(self, data):
        """
        Helper function for verification of the data for adding a new :class: `WebsiteRecord`.
        """
        for field in self.fields:
            if field not in data or data[field] is None:
                return False

        if len(data['url']) > 256 or len(data['url']) == 0:
            return False

        if len(data['label']) > 2564 or len(data['label']) == 0:
            return False

        if int(data['interval']) <= 0:
            # invalid casting ValueError should be caught in the views.py
            return False

        if not (int(data['status']) == 0 or int(data['status']) == 1):
            # invalid casting ValueError should be caught in the views.py
            return False

        if len(data['regex']) == 0:
            return False

        return True

    def create_record(self, json_data):
        """
        Creates a new :class: `WebsiteRecord` instance.
        """
        dict_data = json.loads(json_data)
        dict_data = {k: dict_data[k] for k in dict_data if k in self.fields}
        if not self.valid_record_data(dict_data):
            raise ValueError
        return self.create(**dict_data)


class TagManager(models.Manager):
    def create_tag(self, record, tag):
        """
        Creates a new :class: `Tag` instance.
        """
        return self.create(website_record=record, tag=tag)
