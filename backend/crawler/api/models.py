from django.db import models
import json


class WebsiteRecordManager(models.Manager):
    fields = ('url', 'label', 'interval', 'active', 'regex')

    def valid_record_data(self, data):
        """
        Helper function for verification of the data for adding a new :class: `WebsiteRecord`.

        * Does NOT check that all fields are present - this must be done additionally, should it be needed.
        * Does not allow fields in the data whose keys are not in the fields of this manager.
        * If a valid key is present in the data, corresponding verification is performed.
        * Returns False at the FIRST failed check - does not continue till the end.
        * Allows 'tags' field in data as a special case
        """
        for field in data:
            if (field not in self.fields and field != 'tags') or data[field] is None:
                return False

        if 'url' in data.keys() and (len(data['url']) > 256 or len(data['url']) == 0):
            return False

        if 'label' in data.keys() and (len(data['label']) > 2564 or len(data['label']) == 0):
            return False

        if 'interval' in data.keys() and int(data['interval']) <= 0:
            # invalid casting ValueError should be caught in the views.py
            return False

        if 'active' in data.keys() and data['active'] not in [True, False]:
            # invalid casting ValueError should be caught in the views.py
            return False

        if 'regex' in data.keys() and len(data['regex']) == 0:
            return False

        return True

    def create_record(self, json_data):
        """
        Creates a new :class: `WebsiteRecord` instance.
        """
        dict_data = json.loads(json_data)
        dict_data = {k: dict_data[k] for k in dict_data if k in self.fields}
        if not self.valid_record_data(dict_data) or len(dict_data) != len(self.fields):
            raise ValueError
        return self.create(**dict_data)

    def update_record(self, json_data):
        """
        Updates a :class: `WebsiteRecord` instance.
        """
        dict_data = json.loads(json_data)
        if 'id' not in dict_data.keys() or type(dict_data['id']) is not int:
            return False
        record = WebsiteRecord.objects.filter(pk=dict_data['id'])
        if len(record) < 1:
            return False
        record = record[0]
        dict_data = {k: dict_data[k] for k in dict_data if k in self.fields}
        if not self.valid_record_data(dict_data):
            return False
        for key in dict_data.keys():
            if key == 'tags':
                continue
            record.__setattr__(key, dict_data[key])
        record.save()
        return True


class NodeManager(models.Manager):
    fields = ('title', 'url', 'crawl_time', 'owner')

    def valid_node_data(self, data):
        """
        Helper function for verification of the data for adding a new :class: `Node`.

        """
        for field in data:
            if field not in self.fields or data[field] is None:
                return False

            if 'boundary_record' in data.keys() and data['boundary_record'] not in [True, False]:
                # invalid casting ValueError should be caught in the views.py
                return False

        return True

    def create_node(self, dict_data: dict):
        """
        Creates a new :class: `Node` instance.
        """
        dict_data = {k: dict_data[k] for k in dict_data if k in self.fields}
        if not self.valid_node_data(dict_data) or len(dict_data) != len(self.fields):
            raise ValueError
        return self.create(**dict_data)


class EdgeManager(models.Manager):
    fields = ('source', 'target')

    def valid_edge_data(self, data):
        """
        Helper function for verification of the data for adding a new :class: `Edge`.

        """
        for field in data:
            if field not in self.fields or data[field] is None:
                return False

        return True

    def create_edge(self, dict_data: dict):
        """
        Creates a new :class: `Edge` instance.
        """
        print(dict_data)
        dict_data = {k: dict_data[k] for k in dict_data if k in self.fields}
        if not self.valid_edge_data(dict_data) or len(dict_data) != len(self.fields):
            print(dict_data)
            print(self.valid_edge_data(dict_data))
            raise ValueError
        return self.create(**dict_data)


class TagManager(models.Manager):
    def create_tag(self, record, tag):
        """
        Creates a new :class: `Tag` instance.
        """
        return self.create(website_record=record, tag=tag)


class WebsiteRecord(models.Model):
    """
    Represents a single website crawling record - instructions for crawling.
    """

    class Meta:
        ordering = ('url', 'interval')

    url = models.CharField(max_length=256)
    label = models.CharField(max_length=64)
    interval = models.IntegerField()
    active = models.BooleanField(default=False)
    regex = models.CharField(max_length=128)
    job_id = models.CharField(max_length=128, null=True)

    objects = WebsiteRecordManager()


class Tag(models.Model):
    """
    Represents a single :class: `WebsiteRecord` tag.
    """
    tag = models.CharField(max_length=64)
    website_record = models.ForeignKey(WebsiteRecord, on_delete=models.CASCADE)

    objects = TagManager()


class Execution(models.Model):
    """
    Represents a single web crawler execution of the :class: `WebsiteRecord`.
    """

    class Meta:
        ordering = ('title', 'url')

    title = models.CharField(max_length=72)
    url = models.CharField(max_length=2048)
    crawl_duration = models.IntegerField(default=0)  # 0 before first execution
    last_crawl = models.DateTimeField(null=True)  # null before first execution
    website_record = models.ForeignKey(WebsiteRecord, on_delete=models.CASCADE)
    status = models.IntegerField(default=4)


class ExecutionLink(models.Model):
    """
    A link visited during an :class: `Execution`.
    """
    url = models.CharField(max_length=2048)
    execution = models.ForeignKey(Execution, on_delete=models.CASCADE)


class Node(models.Model):
    """
    A class object for a web map resulting from an :class: `Execution`.
    Only one graph is stored per every :class: `WebsiteRecord` (the latest one).
    """
    title = models.CharField(max_length=2048, null=True)
    crawl_time = models.CharField(max_length=2048)
    boundary_record = models.BooleanField(default=False)
    url = models.CharField(max_length=2048)
    owner = models.ForeignKey(WebsiteRecord, on_delete=models.CASCADE)

    objects = NodeManager()


class Edge(models.Model):
    """
    A single edge between two :class: `Node` objects in the website graph.
    """
    source = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='source_node')
    target = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='target_node')

    objects = EdgeManager()
