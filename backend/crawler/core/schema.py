import graphene
from graphene_django import DjangoObjectType

from .model.DataModel import Node, Tag, Edge, WebsiteRecord, Execution, ExecutionLink


class NodeType(DjangoObjectType):
    class Meta:
        model = Node
        # TODO: Specify fields once finalized
        fields = ()


class EdgeType(DjangoObjectType):
    class Meta:
        model = Edge
        # TODO: Specify fields once finalized
        fields = ()


class TagType(DjangoObjectType):
    class Meta:
        model = Tag
        # TODO: Specify fields once finalized
        fields = ()


class WebsiteRecordType(DjangoObjectType):
    class Meta:
        model = WebsiteRecord
        # TODO: Specify fields once finalized
        fields = ()


class ExecutionType(DjangoObjectType):
    class Meta:
        model = Execution
        # TODO: Specify fields once finalized
        fields = ()


class ExecutionLinkType(DjangoObjectType):
    class Meta:
        model = ExecutionLink
        # TODO: Specify fields once finalized
        fields = ()


class Query(graphene.ObjectType):
    all_executions = graphene.List(ExecutionType)

    def resolve_all_executions(self, info):
        pass


schema = graphene.Schema(query=Query)
