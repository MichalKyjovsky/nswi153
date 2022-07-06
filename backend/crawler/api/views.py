from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from django.db import transaction, DatabaseError, IntegrityError
from django.core.paginator import Paginator

from django.core import serializers
from .models import *

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

status_mapper = {
    1: "IN PROGRESS",
    2: "FINISHED",
    3: "IN QUEUE",
    4: "NEVER EXECUTED",
    5: "UNKNOWN"  # for cases when something goes horribly wrong
}

OPTIONAL_CLAUSE = "Several filters can be used at the same time."
SEE_ERROR = 'See the "error" key in the response for details.'


@swagger_auto_schema(
    methods=['get'],
    operation_description='Returns an execution graph for the selected record. Not implemented yet.',
    manual_parameters=[
        openapi.Parameter('record', openapi.IN_PATH, "ID of the record whose graph we want to receive",
                          type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: openapi.Response('Graph data for the request.'),
    },
    tags=['Graph'])
@api_view(['GET'])
def get_graph(request, record):
    """
    Returns an execution graph for the selected record.
    @param request: the request that for routed to this API endpoint
    @param record: ID of the record whose graph we want to receive
    @return: the request response
    """
    return Response({"message": "Hello World!"}, status=status.HTTP_200_OK)


@swagger_auto_schema(
    methods=['post'],
    operation_description='Adds a new `WebsiteRecord` to the database.',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['url', 'label', 'interval', 'active', 'regex'],
        properties={
            'url': openapi.Schema(type=openapi.TYPE_STRING,
                                  description="The URL where the crawler shall start. "
                                              + "Must be between 1 and 255 characters long.",
                                  example="http://www.crawler.com"),
            'label': openapi.Schema(type=openapi.TYPE_STRING,
                                    description="The label of the to-be-created `WebsiteRecord`. "
                                                + "1-2563 characters long.",
                                    example="My first website record"),
            'interval': openapi.Schema(type=openapi.TYPE_INTEGER,
                                       description="Crawling interval (in seconds). Must be be a non-negative integer.",
                                       example=3600),
            'active': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                     description="One of the values: False (deactivated) or True (activated).",
                                     example=True),
            'regex': openapi.Schema(type=openapi.TYPE_STRING,
                                    description="A non-empty regex to define the URLs to be crawled next. "
                                                + "If everything should be matched, use `.*`.",
                                    example="crawler.com"),
            'tags': openapi.Schema(type=openapi.TYPE_STRING,
                                   description="A comma-separated list of the `WebsiteRecord`'s tags.",
                                   example="awesome,crawl,quick")
        }),
    responses={
        201: openapi.Response('Record was created successfully.'),
        400: openapi.Response('When invalid record data was provided. ' + SEE_ERROR)
    },
    tags=['Website Record'])
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
            tags = [Tag.objects.create_tag(tag.strip()) for tag in request.data['tags'].split(',')]
        with transaction.atomic():
            # atomic to preserve consistency
            record.save()
            for tag in tags:
                record.tags.add(tag)
                tag.save()

        return Response({"message": f"Record and its tags created successfully! (1 record, {len(tags)} tags)"},
                        status=status.HTTP_201_CREATED)
    except (ValueError, DatabaseError, IntegrityError, transaction.TransactionManagementError):
        return Response({"error": "Invalid record parameters entered!"}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    methods=['delete'],
    operation_description='Deletes a `WebsiteRecord` from the database.',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['record_id'],
        properties={
            'record_id': openapi.Schema(type=openapi.TYPE_INTEGER,
                                        description="ID of the record to be deleted.",
                                        example=69),
        }),
    responses={
        200: openapi.Response('The requested record was successfully deleted.'),
        400: openapi.Response(
            'Invalid requested record (not an integer, ID not found or the record ID missing entirely. ' + SEE_ERROR)
    },
    tags=['Website Record'])
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
            return Response({"error": "Invalid record ID for deleting entered!"}, status=status.HTTP_400_BAD_REQUEST)
        record = WebsiteRecord.objects.filter(id=record_id)
        if record:
            record.delete()
            return Response({"message": "Record deleted successfully!"}, status=status.HTTP_200_OK)
        return Response({"error": "Could not find and delete selected record."}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "No Website Record ID for deleting provided!"}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    methods=['get'],
    operation_description='Returns all `WebsiteRecord` object from the database (paginated list).',
    manual_parameters=[
        openapi.Parameter('page', openapi.IN_PATH, "Page of the records to show",
                          type=openapi.TYPE_INTEGER,
                          required=True),
        openapi.Parameter('page_size', openapi.IN_QUERY, "Size of one page",
                          type=openapi.TYPE_INTEGER,
                          example=20,
                          default=10),
        openapi.Parameter('url-filter', openapi.IN_QUERY,
                          "Filters records to only those `WebsiteRecord`s that start at the filtered URL. "
                          + OPTIONAL_CLAUSE,
                          type=openapi.TYPE_STRING,
                          example="http://www.crawler.com"),
        openapi.Parameter('label-filter', openapi.IN_QUERY,
                          "Filters records to only those `WebsiteRecord`s that have the specified label. "
                          + OPTIONAL_CLAUSE,
                          type=openapi.TYPE_STRING,
                          example="My first record"),
        openapi.Parameter('tag-filter', openapi.IN_QUERY,
                          "Filters records to only those `WebsiteRecord`s that contain the specified tag. "
                          + OPTIONAL_CLAUSE,
                          type=openapi.TYPE_STRING,
                          example="my-tag")
    ],
    responses={
        200: openapi.Response('Records were returned.', examples={"application/json": {"records": [
            {"model": "api.websiterecord", "pk": 6,
             "fields": {"url": "http://www.amazon.com", "label": "amazon_crawl", "interval": 100, "active": "true",
                        "regex": "www.amazon.com.*"}, "tags": ["a", "b", "c"]}, {"model": "api.websiterecord", "pk": 5,
                                                                                 "fields": {
                                                                                     "url": "http://www.google.com",
                                                                                     "label": "my_label",
                                                                                     "interval": 120, "active": "false",
                                                                                     "regex": ".*"}, "tags": []}],
            "total_pages": 1,
            "total_records": 2}}),
        400: openapi.Response('Requested page of the list is invalid. ' + SEE_ERROR)
    },
    tags=['Website Record'])
@api_view(['GET'])
def get_records(request, page):
    """
    Retrieves all :class: `WebsiteRecord` objects, returns a paginated list
    (page parameterized by the `page` parameter).
    @param request: the request that for routed to this API endpoint
    @param page: the page of the returned objects to display
    @return: the request response
    """
    page_size, page_num = get_page_data(request, page)
    records = load_and_filter_records(request)
    record_tags = get_tags(records)
    response_dict = serialize_data(records, "records", page_size, page_num)
    if type(response_dict) == Response:
        return response_dict
    response_dict = add_tags(response_dict, record_tags)
    return Response(response_dict, status=status.HTTP_200_OK)


@swagger_auto_schema(
    methods=['post'],
    operation_description='Updates details of a `WebsiteRecord` in the database. Not implemented yet.',
    responses={
        200: openapi.Response('The record was updated successfully.'),
    },
    tags=['Website Record'])
@api_view(['POST'])
def update_record(request):
    """
    Updates a record data.
    @param request: the request that for routed to this API endpoint
    @return: the request response
    """
    pass


@swagger_auto_schema(
    methods=['get'],
    operation_description='Returns a list of `Execution` objects from the database (paginated list).',
    manual_parameters=[
        openapi.Parameter('page', openapi.IN_PATH, "Page of the executions to show",
                          type=openapi.TYPE_INTEGER,
                          required=True),
        openapi.Parameter('page_size', openapi.IN_QUERY, "Size of one page",
                          type=openapi.TYPE_INTEGER,
                          example=20,
                          default=10),
    ],
    responses={
        200: openapi.Response('Executions were returned.', examples={
            "application/json": {
                'executions': [
                    {
                        'model': 'api.execution',
                        'pk': 15,
                        'fields': {
                            'title': 'Amazon purchases',
                            'url': 'www.amazon.com',
                            'crawl_duration': 600,
                            'last_crawl': '2022-04-15T14:30:00Z',
                            'website_record': 6,
                            'status': 'IN QUEUE'
                        },
                        'links': 0
                    },
                    {
                        'model': 'api.execution',
                        'pk': 11,
                        'fields': {
                            'title': 'Google browser',
                            'url': 'www.google.com',
                            'crawl_duration': 0,
                            'last_crawl': None,
                            'website_record': 5,
                            'status': 'NEVER EXECUTED'
                        },
                        'links': 0
                    },
                    {
                        'model': 'api.execution',
                        'pk': 13,
                        'fields': {
                            'title': 'Google browser',
                            'url': 'www.google.com',
                            'crawl_duration': 69,
                            'last_crawl': '2022-04-16T13:30:59Z',
                            'website_record': 5,
                            'status': 'IN PROGRESS'
                        },
                        'links': 0
                    }
                ],
                'total_pages': 1,
                'total_records': 3
            }}),
        400: openapi.Response('Requested page of the list is invalid. ' + SEE_ERROR)
    },
    tags=['Execution'])
@api_view(['GET'])
def get_executions(request, page):
    """
    Retrieves a list of all :class: `Execution`. This view is paginated and parameterized by the `page` parameter.
    @param request: the request that for routed to this API endpoint
    @param page: the page to display
    @return: the request response
    """
    page_size, page_num = get_page_data(request, page)
    executions = map_execution_status(Execution.objects.all().select_related())
    response_data = serialize_data(executions, "executions", page_size, page_num)
    if type(response_data) == Response:
        return response_data
    link_counts = dict()
    for execution in executions:
        execution_id = execution.pk
        link_counts[execution_id] = len(execution.executionlink_set.all())
    for execution in response_data['executions']:
        execution_id = execution['pk']
        if execution_id in response_data:
            execution['links'] = len(response_data[execution_id])
        else:
            execution['links'] = 0
    return Response(response_data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    methods=['get'],
    operation_description="Returns the specified `WebsiteRecord`'s all `Execution`s (paginated list).",
    manual_parameters=[
        openapi.Parameter('record', openapi.IN_PATH, "The ID of the record whose `Execution`s to show",
                          type=openapi.TYPE_INTEGER,
                          required=True,
                          example=69),
        openapi.Parameter('page', openapi.IN_PATH, "Page of the executions to show",
                          type=openapi.TYPE_INTEGER,
                          required=True),
        openapi.Parameter('page_size', openapi.IN_QUERY, "Size of one page",
                          type=openapi.TYPE_INTEGER,
                          example=20,
                          default=10),
    ],
    responses={
        200: openapi.Response('Executions were returned.', examples={"application/json": {
            'executions': [
                {
                    'model': 'api.execution',
                    'pk': 11,
                    'fields': {
                        'title': 'Google browser',
                        'url': 'www.google.com',
                        'crawl_duration': 0,
                        'last_crawl': None,
                        'website_record': 5,
                        'status': 'NEVER EXECUTED'
                    }
                },
                {
                    'model': 'api.execution',
                    'pk': 13,
                    'fields': {
                        'title': 'Google browser',
                        'url': 'www.google.com',
                        'crawl_duration': 69,
                        'last_crawl': '2022-04-16T13:30:59Z',
                        'website_record': 5,
                        'status': 'IN PROGRESS'
                    }
                },
                {
                    'model': 'api.execution',
                    'pk': 14,
                    'fields': {
                        'title': 'Google browser',
                        'url': 'www.google.com',
                        'crawl_duration': 42,
                        'last_crawl': '2022-04-17T13:30:59Z',
                        'website_record': 5,
                        'status': 'FINISHED'
                    }
                }
            ],
            'total_pages': 1,
            'total_records': 3
        }}),
        400: openapi.Response('Invalid Record ID or page provided in the request. ' + SEE_ERROR)
    },
    tags=['Execution'])
@api_view(['GET'])
def get_execution(request, record, page):
    """
    Retrieves the details about a certain :class: `WebsiteRecord`'s all `Execution`s.
    @param request: the request that for routed to this API endpoint
    @param record: the record whose executions we want to
    @param page: the page to be displayed
    @return: the request response
    """
    page_size, page_num = get_page_data(request, page)
    try:
        record_id = int(record)
    except ValueError:
        return Response({"error": f"Invalid Website Record ID {id}: an integer expect!"},
                        status=status.HTTP_400_BAD_REQUEST)
    executions = Execution.objects.filter(website_record=record_id)
    if len(executions) == 0:
        return Response({"error": f"Executions for Website Record ID {record} were not found!"},
                        status=status.HTTP_400_BAD_REQUEST)
    response_dict = serialize_data(map_execution_status(executions), "executions", page_size, page_num)
    if type(response_dict) == Response:
        return response_dict
    return Response(response_dict, status=status.HTTP_200_OK)


@swagger_auto_schema(
    methods=['get'],
    operation_description="Returns metrics of the application.  Not implemented yet, to be removed.",
    responses={
        200: openapi.Response('Metrics data returned.')
    },
    tags=['Monitoring'])
@api_view(['GET'])
def get_stats(request):
    """
    Returns the system stats.
    @param request: the request that for routed to this API endpoint
    @return: the request response
    """
    pass


@swagger_auto_schema(
    methods=['put'],
    operation_description="Activates the specified `WebsiteRecord`.",
    manual_parameters=[
        openapi.Parameter('record', openapi.IN_PATH, "The ID of the record to be activated",
                          type=openapi.TYPE_INTEGER,
                          required=True,
                          example=69),
    ],
    responses={
        200: openapi.Response('The specified `WebsiteRecord` was activated.'),
        400: openapi.Response('Invalid Record ID provided. ' + SEE_ERROR)
    },
    tags=['Record'])
@api_view(['PUT'])
def activate(request, record):
    """
    Activates a :class: `WebsiteRecord`.
    @param request: the request that for routed to this API endpoint
    @param record: the ID of the record to be activated
    @return: the request response
    """
    return do_activation(record, True, "activated")


@swagger_auto_schema(
    methods=['put'],
    operation_description="Deactivates the specified `WebsiteRecord`.",
    manual_parameters=[
        openapi.Parameter('record', openapi.IN_PATH, "The ID of the record to be deactivated",
                          type=openapi.TYPE_INTEGER,
                          required=True,
                          example=69),
    ],
    responses={
        200: openapi.Response('The specified `WebsiteRecord` was deactivated.'),
        400: openapi.Response('Invalid Record ID provided. ' + SEE_ERROR)
    },
    tags=['Record'])
@api_view(['PUT'])
def deactivate(request, record):
    """
    Deactivates a :class: `WebsiteRecord`.
    @param request: the request that for routed to this API endpoint
    @param record: the record to be deactivated
    @return: the request response
    """
    return do_activation(record, False, "deactivated")


@swagger_auto_schema(
    methods=['POST'],
    operation_description="Runs a celery process.",
    responses={
        200: openapi.Response('The celery process was run.'),
    },
    tags=['Celery'])
@api_view(['POST'])
def run_celery(quest):
    # TODO: to be implemented by @mkyjovsky including docs and tests
    pass

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

    if 'page_size' in request.query_params:
        try:
            page_size = int(request.query_params.get('page_size'))
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

    if 'url-filter' in request.query_params and request.query_params.get('url-filter') is not None:
        records = records.filter(url=request.query_params.get('url-filter'))

    if 'label-filter' in request.query_params and request.query_params.get('label-filter') is not None:
        records = records.filter(label=request.query_params.get('label-filter'))

    if 'tag-filter' in request.query_params and request.query_params.get('tag-filter') is not None:
        records = [record for record in records if
                   has_tag(record.tags.all(), request.query_params.get('tag-filter'))]

    return records


def get_tags(records):
    """
    Creates a dictionary of tags mapped to :class: `WebsiteRecord`.
    @param records: the records whose tags are to be transformed
    @return: A map of :class: `WebsiteRecord` with their tags
    """
    record_tags = dict()

    for record in records:
        record_id = record.pk
        record_list = []
        for tag in record.tags.all():
            record_list.append(tag.tag)
        record_tags[record_id] = record_list

    return record_tags


def serialize_data(records, key, page_size, page_num):
    """
    Serializes data provided to JSON format and adds paging details.
    @param records: the data to be serialized
    @param key: the key in JSON where the output should be stored
    @param page_size: objects per page
    @param page_num: page to be serialized
    @return: paginated and serialized data
    """
    JSONserializer = serializers.get_serializer("json")
    serializer = JSONserializer()
    records = Paginator(records, page_size)
    if page_num > records.num_pages or page_num < 1:
        return Response({"error": f"Invalid page {page_num}!"}, status=status.HTTP_400_BAD_REQUEST)
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
    @param value: expected boolean value (True for activation, False for deactivation)
    @param log: log message
    @return: response to the request
    """
    try:
        record_id = int(record)
    except ValueError:
        return Response({"error": f"Invalid Website Record ID {record}: an integer expect!"},
                        status=status.HTTP_400_BAD_REQUEST)
    record = WebsiteRecord.objects.filter(id=record_id)
    if len(record) < 1:
        return Response({"error": f"Website Record with ID {record_id} was not found! The record was not {log}."},
                        status=status.HTTP_400_BAD_REQUEST)
    record = record[0]
    record.active = value
    record.save()
    return Response({"message": f"Website Record with ID {record_id} was {log}."}, status=status.HTTP_200_OK)


def map_execution_status(executions):
    """
    Maps execution statuses from int values to human-readable values.
    @param executions: an iterable containing :class: `Execution` instances to be mapped
    @return: the same executions, but with status mapped from ints to human-readable strings
    """
    for execution in executions:
        state = execution.status
        if type(state) is not int or int(state) < 1 or int(state) > 5:
            state = 5
        execution.status = status_mapper[int(state)]
    return executions
