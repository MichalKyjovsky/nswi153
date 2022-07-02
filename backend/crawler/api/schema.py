import graphene
from graphene_django import DjangoObjectType

from .models import Node, Tag, Edge, WebsiteRecord, Execution, ExecutionLink


class NodeType(DjangoObjectType):
    class Meta:
        model = Node
        fields = ('url', 'domain', 'website_record')


class EdgeType(DjangoObjectType):
    class Meta:
        model = Edge
        fields = ('source', 'target')


class TagType(DjangoObjectType):
    class Meta:
        model = Tag
        fields = ('tag', 'website_record')


class WebsiteRecordType(DjangoObjectType):
    class Meta:
        model = WebsiteRecord
        fields = ('id', 'label', 'url', 'interval', 'status', 'regex', 'tag')

    tags = graphene.List(TagType)

    def resolve_tags(self, info):
        return Tag.objects.filter(website_record_id=self.Meta.id).all()


class ExecutionType(DjangoObjectType):
    class Meta:
        model = Execution
        fields = ('title', 'url', 'crawl_time', 'website_record')


class ExecutionLinkType(DjangoObjectType):
    class Meta:
        model = ExecutionLink
        fields = ('url', 'execution')


class Query(graphene.ObjectType):
    all_executions = graphene.List(ExecutionType)
    websites = graphene.List(WebsiteRecordType)

    def resolve_all_executions(self, info):
        return Execution.objects.select_related("website_record").all()

    def resolve_websites(self, info):
        return WebsiteRecord.objects.all()


schema = graphene.Schema(query=Query)
