from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.db import transaction, DatabaseError, IntegrityError

import json

from .serializers import *
from core.model.DataModel import *


@api_view(['GET'])
def get_graph(request, record):
    return Response({"message": "Hello World!"})


@api_view(['POST'])
def add_record(request):
    json_data = json.dumps(request.data)
    try:
        record = WebsiteRecord.objects.create_record(json_data)
        tags = []
        if 'tags' in request.data:
            tags = [Tag.objects.create_tag(record, tag.strip()) for tag in request.data['tags'].split(',')]
        with transaction.atomic():
            record.save()
            for tag in tags:
                tag.save()
        return Response({"message": f"Record and its tags created successfully! (1 record, {len(tags)} tags)"})
    except (ValueError, DatabaseError, IntegrityError, transaction.TransactionManagementError) as e:
        return Response({"error": "Invalid record parameters entered!"})


@api_view(['DELETE'])
def delete_record(request):
    pass


@api_view(['GET'])
def get_records(request):
    pass


@api_view(['GET'])
def get_executions(request):
    pass


@api_view(['GET'])
def get_execution(request, execution):
    pass


@api_view(['GET'])
def get_stats(request):
    pass
