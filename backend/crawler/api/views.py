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
    if 'record_id' in request.data:
        try:
            record_id = int(request.data['record_id'])
        except ValueError:
            return Response({"error": "Invalid record ID for deleting entered!"})
        record = WebsiteRecord.objects.filter(id=record_id)
        if record:
            record.delete()
            return Response({"message": "Record deleted successfully!"})
        return Response({"error": "Could not find and delete selected record."})


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

    records = WebsiteRecord.objects.all().select_related()
    for record in records:
        for tag in record.tag_set.all():
            print(tag.tag)

    if 'url-filter' in request.data and request.data['url-filter'] is not None:
        records = records.filter(url=request.data['url-filter'])

    if 'label-filter' in request.data and request.data['label-filter'] is not None:
        records = records.filter(label=request.data['label-filter'])

    if 'tag-filter' in request.data and request.data['tag-filter'] is not None:
        records = [record for record in records if has_tag(record.tag_set.all(), request.data['tag-filter'])]

    record_tags = dict()

    for record in records:
        id = record.pk
        l = []
        for tag in record.tag_set.all():
            l.append(tag.tag)
        record_tags[id] = l

    JSONserializer = serializers.get_serializer("json")
    serializer = JSONserializer()
    records = Paginator(records, page_size)
    response_dict = json.loads(serializer.serialize(records.page(page_num)))
    response_dict = {'records': response_dict}

    for model in response_dict['records']:
        pk = model['pk']
        if pk in record_tags:
            model['tags'] = record_tags[pk]

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


@api_view(['PUT'])
def activate(request, record):
    pass


@api_view(['PUT'])
def deactivate(request, record):
    pass


########################################################

def has_tag(tags, target) -> bool:
    for tag in tags:
        if tag.tag == target:
            return True
    return False
