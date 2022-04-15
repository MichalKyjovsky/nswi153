from django.db import models


class WebsiteRecord(models.Model):
    STATUS = ((1, 'Active'), (0, 'Inactive'))
    url = models.CharField(max_length=256)
    label = models.CharField(max_length=64)
    interval = models.IntegerField()
    status = models.IntegerField(max_length=1, choices=STATUS)
    regex = models.CharField(max_length=128)


class Tag(models.Model):
    tag = models.CharField(max_length=64)
    website_record = models.ForeignKey(WebsiteRecord, on_delete=models.CASCADE())


class Execution(models.Model):
    title = models.CharField(max_length=72)
    url = models.CharField(max_length=2048)
    crawl_time = models.DateTimeField()
    website_record = models.ForeignKey(WebsiteRecord, on_delete=models.CASCADE())


class ExecutionLink(models.Model):
    url = models.CharField(max_length=2048)
    execution = models.ForeignKey(Execution, on_delete=models.CASCADE())


class Node(models.Model):
    url = models.CharField(max_length=2048)
    domain = models.CharField(max_length=2048)
    website_record = models.ForeignKey(WebsiteRecord, on_delete=models.CASCADE())


class Edge(models.Model):
    source = models.ForeignKey(Node, on_delete=models.CASCADE())
    target = models.ForeignKey(Node, on_delete=models.CASCADE())
