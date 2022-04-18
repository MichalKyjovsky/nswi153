from rest_framework import serializers

from core.model.DataModel import *


class WebsiteRecordSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WebsiteRecord
        fields = ('url', 'label', 'interval', 'status', 'regex')


class TagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tag
        fields = ('tag', 'website_record')


class ExecutionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Execution
        fields = ('title', 'url', 'crawl_time', 'website_record')


class ExecutionLinkSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ExecutionLink
        fields = ('url', 'execution')


class NodeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Node
        fields = ('url', 'domain', 'website_record')


class EdgeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Edge
        fields = ('source', 'target')
