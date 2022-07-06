from django.db import models
import json


class WebsiteRecordManager(models.Manager):
    fields = ('url', 'label', 'interval', 'active', 'regex')

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

        if data['active'] not in ["True", "False"]:
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
    def create_tag(self, tag):
        """
        Creates a new :class: `Tag` instance.
        """
        return self.create(tag=tag)


class Tag(models.Model):
    """
    Represents a single :class: `WebsiteRecord` tag.
    """
    tag = models.CharField(max_length=64)

    objects = TagManager()


class WebsiteRecord(models.Model):
    """
    Represents a single website crawling record - instructions for crawling.
    """

    class Meta:
        ordering = ('label', 'interval')

    url = models.CharField(max_length=256)
    label = models.CharField(max_length=64)
    interval = models.IntegerField()
    active = models.BooleanField(default=False)
    regex = models.CharField(max_length=128)
    tags = models.ManyToManyField(Tag)

    objects = WebsiteRecordManager()


class Execution(models.Model):
    """
    Represents a single web crawler execution of the :class: `WebsiteRecord`.
    """

    class Meta:
        ordering = ('title', 'url')

    title = models.CharField(max_length=72)
    url = models.CharField(max_length=2048)
    crawl_time = models.DateTimeField()
    website_record = models.ForeignKey(WebsiteRecord, on_delete=models.CASCADE)


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
    url = models.CharField(max_length=2048)
    owner = models.ForeignKey(WebsiteRecord, on_delete=models.CASCADE)


class Edge(models.Model):
    """
    A single edge between two :class: `Node` objects in the website graph.
    """
    source = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='source_node')
    target = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='target_node')
