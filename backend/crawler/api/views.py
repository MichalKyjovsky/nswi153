from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.db import transaction, DatabaseError, IntegrityError
from django.core.paginator import Paginator

import json

from django.core import serializers
from core.model.DataModel import *


@api_view(['GET'])
def get_graph(request, record):
    """
    Returns an execution graph for the selected record.
    @param request: the request that for routed to this API endpoint
    @param record:
    @return: the request response
    """
    return Response({"message": "Hello World!"})


@api_view(['POST'])
def add_record(request):
    """
    Adds a new :class: `WebsiteRecord` to the database.
    @param request: the request that for routed to this API endpoint
    @return: the request response
    """
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
    """
    Deletes a single :class: `WebsiteRecord` object from the database.
    @param request: the request that for routed to this API endpoint
    @return: the request response
    """
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
    """
    Retrieves all :class: `WebsiteRecord` objects, returns a paginated list (page parameterized by the `page` parameter).
    @param request: the request that for routed to this API endpoint
    @param page: the page of the returned objects to display
    @return: the request response
    """
    page_size, page_num = get_page_data(request, page)
    records = load_and_filter_records(request)
    record_tags = get_tags(records)
    response_dict = serialize_data(records, "records", page_size, page_num)
    response_dict = add_tags(response_dict, record_tags)
    return Response(response_dict)


@api_view(['POST'])
def update_record(request):
    """
    Updates a record data.
    @param request: the request that for routed to this API endpoint
    @return: the request response
    """
    pass


@api_view(['GET'])
def get_executions(request, page):
    """
    Retrieves a list of all :class: `Execution`. This view is paginated and parameterized by the `page` parameter.
    @param request: the request that for routed to this API endpoint
    @param page: the page to display
    @return: the request response
    """
    page_size, page_num = get_page_data(request, page)
    executions = Execution.objects.all().select_related()
    response_data = serialize_data(executions, "executions", page_size, page_num)
    link_counts = dict()
    for execution in executions:
        id = execution.pk
        link_counts = len(execution.executionlink_set)
    for execution in response_data['executions']:
        id = execution['pk']
        if id in response_data:
            execution['links'] = len(response_data[id])
        else:
            execution['links'] = 0
    return Response(response_data)


@api_view(['GET'])
def get_execution(request, record):
    """
    Retrieves the details about a certains :class: `Execution`.
    @param request: the request that for routed to this API endpoint
    @param record: the record whose executions we want to
    @return: the request response
    """
    JSONserializer = serializers.get_serializer("json")
    serializer = JSONserializer()
    execution = Execution.objects.filter(website_record=record)
    if len(execution) == 0:
        return Response({"error": f"Executions for Website Record ID {record} were not found!"})
    response_dict = json.loads(serializer.serialize(execution))
    return Response(response_dict)


@api_view(['GET'])
def get_stats(request):
    """
    Returns the system stats.
    @param request: the request that for routed to this API endpoint
    @return: the request response
    """
    pass


@api_view(['PUT'])
def activate(request, record):
    """
    Activates a :class: `WebsiteRecord`.
    @param request: the request that for routed to this API endpoint
    @return: the request response
    @return: the request response
    """
    return do_activation(record, 1, "activated")


@api_view(['PUT'])
def deactivate(request, record):
    """
    Deactivates a :class: `WebsiteRecord`.
    @param request: the request that for routed to this API endpoint
    @param record: the record to be deactivated
    @return: the request response
    """
    return do_activation(record, 0, "deactivated")


########################################################

def has_tag(tags, target) -> bool:
    """
    Verifies that the `target` tag is present in a query set.
    @param tags: tags to be checked
    @param target: the tag searched for
    @return: True if the target is present, False otherwise
    """
    for tag in tags:
        if tag.tag == target:
            return True
    return False


def get_page_data(request, page):
    """
    Retrieves details about page size and page number.
    @param request: the request with the data
    @param page: the target page to be parsed
    @return: page and its size, if not present, page size = 10 and page number = 1
    """
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
    return page_size, page_num


def load_and_filter_records(request):
    """
    Loads and filters :class: `WebsiteRecord` data.
    @param request: the request with the data
    @return: :class: `WebsiteRecord` data
    """
    records = WebsiteRecord.objects.all().select_related()

    if 'url-filter' in request.data and request.data['url-filter'] is not None:
        records = records.filter(url=request.data['url-filter'])

    if 'label-filter' in request.data and request.data['label-filter'] is not None:
        records = records.filter(label=request.data['label-filter'])

    if 'tag-filter' in request.data and request.data['tag-filter'] is not None:
        records = [record for record in records if has_tag(record.tag_set.all(), request.data['tag-filter'])]

    return records


def get_tags(records):
    """
    Creates a dictionary of tags mapped to :class: `WebsiteRecord`.
    @param records: the records whose tags are to be transformed
    @return: A map of :class: `WebsiteRecord` with their tags
    """
    record_tags = dict()

    for record in records:
        id = record.pk
        l = []
        for tag in record.tag_set.all():
            l.append(tag.tag)
        record_tags[id] = l

    return record_tags


def serialize_data(records, key, page_size, page_num):
    """
    Serializes data provided to JSON format and adds paging details.
    @param records: the data to be serialized
    @param key: the key in JSON where the output should be stored
    @param page_size: objects per page
    @param page_num: page to be serialized
    @return: paginated and serialzied data
    """
    JSONserializer = serializers.get_serializer("json")
    serializer = JSONserializer()
    records = Paginator(records, page_size)
    response_dict = json.loads(serializer.serialize(records.page(page_num)))
    response_dict = {key: response_dict, 'total_pages': records.num_pages, 'total_records': records.count}
    return response_dict


def add_tags(response_dict, record_tags):
    """
    Adds tag information into serialized :class: `WebsiteRecord` data in JSON.
    @param response_dict: the serialized data
    @param record_tags: tags to be added
    @return: serialized data with additional information
    """
    for model in response_dict['records']:
        pk = model['pk']
        if pk in record_tags:
            model['tags'] = record_tags[pk]
    return response_dict


def do_activation(record, value, log):
    """
    Performs a (de) activation of a :class: `WebsiteRecord`.
    @param record: record to be activated
    @param value: expected value (1 for activation, 0 for deactivation)
    @param log: log message
    @return: response to the request
    """
    record = WebsiteRecord.objects.filter(id=record)
    if len(record) < 1:
        return Response({"error": f"Website Record with ID {record} was not found! The record was not {log}."})
    record = record[0]
    record.status = value
    record.save()
    return Response({"error": f"Website Record with ID {record} was {log}."})
