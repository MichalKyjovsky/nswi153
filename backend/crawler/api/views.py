from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.db import transaction, DatabaseError, IntegrityError
from django.core.paginator import Paginator

import json

from django.core import serializers
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
            # atomic to preserve consistency
            record.save()
            for tag in tags:
                tag.save()
        return Response({"message": f"Record and its tags created successfully! (1 record, {len(tags)} tags)"})
    except (ValueError, DatabaseError, IntegrityError, transaction.TransactionManagementError) as e:
        return Response({"error": "Invalid record parameters entered!"})


@api_view(['DELETE'])
def delete_record(request):
    ...


@api_view(['GET'])
def get_records(request, page):
    page_size = 10
    page_num = 1
    try:
        page_num = int(page)
    except ValueError:
        # int parsing error
        pass

    if 'page_size' in request.data:
        try:
            page_size = int(request.data['page_size'])
        except ValueError:
            # int parsing error
            pass
    JSONserializer = serializers.get_serializer("json")
    serializer = JSONserializer()

    records = Paginator(WebsiteRecord.objects.all(), page_size)
    response_dict = json.loads(serializer.serialize(records.page(page_num)))
    response_dict = {'records': response_dict}
    print(type(response_dict))
    response_dict['total_pages'] = records.num_pages
    response_dict['total_records'] = records.count
    return Response(response_dict)


@api_view(['GET'])
def get_executions(request):
    pass


@api_view(['GET'])
def get_execution(request, execution):
    pass


@api_view(['GET'])
def get_stats(request):
    pass
