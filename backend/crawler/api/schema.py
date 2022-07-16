import graphene
from graphene_django import DjangoObjectType, DjangoListField

from .models import Node, Tag, Edge, WebsiteRecord, Execution, ExecutionLink


class NodeType(DjangoObjectType):
    class Meta:
        model = Node
        fields = ('title', 'url', 'owner', 'crawl_time')

    links = graphene.List(lambda: NodeType)

    def resolve_links(self, root):
        return [x.target for x in Edge.objects.filter(source=self.id).all()]


class EdgeType(DjangoObjectType):
    class Meta:
        model = Edge
        fields = ('source', 'target')


class TagType(DjangoObjectType):
    class Meta:
        model = Tag
        fields = ('tag',)


class WebsiteRecordType(DjangoObjectType):
    class Meta:
        model = WebsiteRecord
        fields = ('id', 'label', 'url', 'interval', 'active', 'regex')

    tags = graphene.List(TagType)

    @staticmethod
    def resolve_tags(website_record, *args, **kwargs):
        return website_record.tags.all()


class ExecutionType(DjangoObjectType):
    class Meta:
        model = Execution
        fields = ('title', 'url', 'crawl_duration', 'last_crawl', 'website_record', 'status')


class ExecutionLinkType(DjangoObjectType):
    class Meta:
        model = ExecutionLink
        fields = ('url', 'execution')


class Query(graphene.ObjectType):
    all_executions = graphene.List(ExecutionType)
    websites = graphene.List(WebsiteRecordType)
    nodes_by_ids = DjangoListField(NodeType, web_pages=graphene.List(graphene.Int))

    def resolve_all_executions(self, info):
        return Execution.objects.select_related("website_record").all()

    def resolve_websites(self, info):
        return WebsiteRecord.objects.all()

    def resolve_nodes_by_ids(self, info, web_pages):
        return Node.objects.filter(owner__in=web_pages).all()


schema = graphene.Schema(query=Query)
