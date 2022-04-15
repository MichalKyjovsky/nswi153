from django.db import models
from .DataModelManager import *


class WebsiteRecord(models.Model):
    """
    Represents a single website crawling record - instructions for crawling.
    """
    STATUS = ((1, 'Active'), (0, 'Inactive'))
    url = models.CharField(max_length=256)
    label = models.CharField(max_length=64)
    interval = models.IntegerField()
    status = models.IntegerField(choices=STATUS)
    regex = models.CharField(max_length=128)

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
    url = models.CharField(max_length=2048)
    domain = models.CharField(max_length=2048)
    website_record = models.ForeignKey(WebsiteRecord, on_delete=models.CASCADE)


class Edge(models.Model):
    """
    A single edge between two :class: `Node` objects in the website graph.
    """
    source = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='source_node')
    target = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='target_node')
