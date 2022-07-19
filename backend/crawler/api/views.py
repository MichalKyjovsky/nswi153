from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from django.db import transaction, DatabaseError, IntegrityError
from django.core.paginator import Paginator

from django.core import serializers
from .models import *

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from tasks.crawler import manage_tasks, start_periodic_task, stop_periodic_task
from tasks.transformer import get_graph as transformer_get_graph

status_mapper = {
    1: "IN PROGRESS",
    2: "FINISHED",
    3: "IN QUEUE",
    4: "NEVER EXECUTED",
    5: "UNKNOWN"  # for cases when something goes horribly wrong
}

OPTIONAL_CLAUSE = "Several filters can be used at the same time."
SEE_ERROR = 'See the "error" key in the response body for details.'


@swagger_auto_schema(
    methods=['get'],
    operation_description='Returns an execution graph for the selected record. Not implemented yet.',
    manual_parameters=[
        openapi.Parameter('mode', openapi.IN_PATH,
                          "Mode in which the graf should be displayed. i.e., website or domain ",
                          type=openapi.TYPE_STRING,
                          required=True),
        openapi.Parameter('record', openapi.IN_QUERY,
                          "IDd of the record whose graph we want to receive, "
                          + "concatenated by a comma without a whitespace.",
                          type=openapi.TYPE_STRING, example="5,6,7")
    ],
    responses={
        200: openapi.Response('Graph data for the request.', examples={"application/json": {
            'nodes': [
                {
                    'model': 'api.node',
                    'pk': 1,
                    'fields': {
                        'title': 'Node A',
                        'crawl_time': '',
                        'url': 'www.com.foo.baz',
                        'owner': 5
                    }
                },
                {
                    'model': 'api.node',
                    'pk': 2,
                    'fields': {
                        'title': 'Node B',
                        'crawl_time': '',
                        'url': 'www.com.foo.baz.sas',
                        'owner': 5
                    }
                }
            ],
            'edges': [
                {
                    'model': 'api.edge',
                    'pk': 1,
                    'fields': {
                        'source': 1,
                        'target': 2
                    }
                }
            ]
        }}),
        400: openapi.Response('List of queried Website Record IDs was either not present or they were not integers. '
                              + SEE_ERROR)
    },
    tags=['Graph'])
@api_view(['GET'])
def get_graph(request, mode):
    """
    Returns an execution graph for the selected record.
    @param mode: mode of the graph - either 'domain' or 'website' (if non-domain string, 'website' is assumed)
    @param request: the request that for routed to this API endpoint
    @return: the request response
    """
    if 'record' not in request.query_params:
        return Response({"error": f"The Website Record ID(s) query parameter was not found!"},
                        status=status.HTTP_400_BAD_REQUEST)
    records = request.query_params.get('record').split(',')
    record_ids = []
    domain_flag = mode == 'domain'
    for record in records:
        if not record.isnumeric():
            return Response({"error": f"The Website Record ID {record} is not an integer!"},
                            status=status.HTTP_400_BAD_REQUEST)
        record_ids.append(int(record))
    edges = Edge.objects.select_related().filter(Q(source__owner__in=record_ids) | Q(target__owner__in=record_ids))
    nodes = Node.objects.filter(owner__in=record_ids)
    output = transformer_get_graph(edges, nodes, domain_flag)
    return Response(data=output, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description='Returns details of a single `WebsiteRecord` object.',
    manual_parameters=[
        openapi.Parameter('record', openapi.IN_PATH, "The ID of the `WebsiteRecord` whose data are requested.",
                          type=openapi.TYPE_INTEGER,
                          required=True, example=42)
    ],
    responses={
        200: openapi.Response('Record was returned.', examples={"application/json": [
            {
                'model': 'api.websiterecord',
                'pk': 1,
                'fields': {
                    'url': 'http://www.google.com',
                    'label': 'my_label',
                    'interval': 120,
                    'active': True,
                    'regex': '.*',
                    'tags': [
                        'my_tag',
                        'super_awersome_website',
                        'third_tag'
                    ]
                }
            }
        ]}),
        400: openapi.Response(
            "Invalid request! The request must contain the 'record' key with ID specified as a numeric value. "
            + SEE_ERROR),
        404: openapi.Response('Record with ID {record_id} was not found! ' + SEE_ERROR)
    },
    tags=['Website Record'])
@swagger_auto_schema(
    method='post',
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
        201: openapi.Response('Record was created successfully. Includes ID of the new record under key "pk".',
                              examples={"application/json": {
                                  'message': 'Record and its tags created successfully! (1 record, 3 tags)',
                                  'pk': 1
                              }}),
        400: openapi.Response('When invalid record data was provided. ' + SEE_ERROR)
    },
    tags=['Website Record'])
@swagger_auto_schema(
    method='put',
    operation_description='Updates details of a `WebsiteRecord` in the database.',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['id'],
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER,
                                 description="A valid ID of the `WebsiteRecord` to be updated.",
                                 example=69),
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
                                     description="One of the values: `False` (deactivated) or `True` (activated).",
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
        204: openapi.Response('Record was updated successfully!'),
        400: openapi.Response('Invalid data! Record was not updated. ' + SEE_ERROR),
    },
    tags=['Website Record'])
@swagger_auto_schema(
    method='delete',
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
@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def record_crud(request):
    """
    A routing functions for processing record non-parameterized requests (not paginated get_records).
    @param request: request to be handled
    @return: the result of the corresponding operation
    """
    if request.method == 'GET':
        return get_record(request)
    if request.method == 'PUT':
        return update_record(request)
    if request.method == 'DELETE':
        return delete_record(request)
    return add_record(request)


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
                          example="my-tag"),
        openapi.Parameter('sort_property', openapi.IN_QUERY,
                          "Property according to which results shall be returned. "
                          + "One of 'label', 'url' or 'last_crawl'.",
                          type=openapi.TYPE_STRING,
                          example="last_crawl"),
        openapi.Parameter('sort_order', openapi.IN_QUERY,
                          "A required parameter when 'sort_property' parameter is used. "
                          + "Ascending (ASC) or descending (DESC) sort order.",
                          type=openapi.TYPE_STRING,
                          example="ASC")
    ],
    responses={
        200: openapi.Response('Records were returned.', examples={"application/json": {
            'records': [
                {
                    'model': 'api.websiterecord',
                    'pk': 6,
                    'fields': {
                        'url': 'http://www.amazon.com',
                        'label': 'amazon_crawl',
                        'interval': 100,
                        'active': False,
                        'regex': 'www.amazon.com.*'
                    },
                    'tags': [
                        '2',
                        'a',
                        'c'
                    ],
                    'last_duration': 5000,
                    'last_status': 'IN PROGRESS'
                },
                {
                    'model': 'api.websiterecord',
                    'pk': 5,
                    'fields': {
                        'url': 'http://www.google.com',
                        'label': 'my_label',
                        'interval': 120,
                        'active': True,
                        'regex': '.*'
                    },
                    'tags': [
                        '1',
                        '3',
                        'b'
                    ],
                    'last_duration': 42,
                    'last_status': 'FINISHED'
                }
            ],
            'total_pages': 1,
            'total_records': 2
        }}),
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
    response_dict = add_execution_details(response_dict)
    sort_property, is_ascending = get_sort_details(request)
    if sort_property is not None and sort_property != 'last_crawl':
        response_dict['records'].sort(key=lambda a: a['fields'].__getitem__(sort_property).lower(),
                                      reverse=is_ascending)
    elif sort_property == 'last_crawl':
        response_dict['records'].sort(key=lambda a: a.__getitem__(sort_property), reverse=is_ascending)
    return Response(response_dict, status=status.HTTP_200_OK)


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
                        'pk': 11,
                        'fields': {
                            'title': 'Google browser',
                            'url': 'www.google.com',
                            'crawl_duration': 0,
                            'last_crawl': None,
                            'website_record': 5,
                            'status': 'NEVER EXECUTED',
                            'label': 'my_label'
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
                            'status': 'IN PROGRESS',
                            'label': 'my_label'
                        },
                        'links': 0
                    }
                ],
                'total_pages': 3,
                'total_records': 5
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

    if 'executions' in response_data:
        for execution in response_data['executions']:
            record_label = WebsiteRecord.objects.filter(pk=execution['fields']['website_record'])[0].label
            execution['fields']['label'] = record_label

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
                        'status': 'NEVER EXECUTED',
                        'label': 'my_label'
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
                        'status': 'IN PROGRESS',
                        'label': 'my_label'
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
                        'status': 'FINISHED',
                        'label': 'my_label'
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
    if not record.isnumeric():
        return Response({"error": f"Invalid Website Record ID {id}: an integer expect!"},
                        status=status.HTTP_400_BAD_REQUEST)
    record_id = int(record)
    executions = Execution.objects.filter(website_record=record_id).select_related()
    if len(executions) == 0:
        return Response({"error": f"Executions for Website Record ID {record} were not found!"},
                        status=status.HTTP_400_BAD_REQUEST)
    response_dict = serialize_data(map_execution_status(executions), "executions", page_size, page_num)
    if 'executions' in response_dict and len(response_dict['executions']) > 0:
        record_label = WebsiteRecord.objects.filter(pk=response_dict['executions'][0]['fields']['website_record'])[
            0].label
        for execution in response_dict['executions']:
            execution['fields']['label'] = record_label
    if type(response_dict) == Response:
        return response_dict
    return Response(response_dict, status=status.HTTP_200_OK)


@swagger_auto_schema(
    methods=['POST'],
    operation_description='Starts crawler execution of a specified `WebsiteRecord`.',
    responses={
        200: openapi.Response('Crawling has started or it was placed in a queue. No body.'),
        400: openapi.Response('The `WebsiteRecord` ID was not present or is invalid. ' + SEE_ERROR)
    },
    tags=['Execution'])
@api_view(['POST'])
def start_execution(request, record):
    # Get the ID from path param
    try:
        record_id = int(record)
    except ValueError:
        return Response({"error": f"Invalid Website Record ID {record}: an integer expect!"},
                        status=status.HTTP_400_BAD_REQUEST)
    record_rs = WebsiteRecord.objects.filter(pk=record_id)
    if record_rs.exists():
        # Run crawling
        try:
            task = manage_tasks(record_rs)

        except Exception:
            return Response({"error": "Celery server crashed processing the request!"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Task started.",
                         "taskId": task},
                        status=status.HTTP_201_CREATED)
    else:
        return Response({"error": "Invalid record parameters entered!"}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    methods=['get'],
    operation_description='Returns a list of `WebsiteRecord` objects from the database (non-paginated list) '
                          + 'with 2 fields: pk and label.',
    responses={
        200: openapi.Response('WebsiteRecord info was returned.', examples={
            "application/json": {
                'records': [
                    {
                        'pk': 6,
                        'label': 'amazon_crawl'
                    },
                    {
                        'pk': 5,
                        'label': 'my_label'
                    }
                ]
            }
        })
    },
    tags=['Website Record'])
@api_view(['GET'])
def list_records(request):
    record_data = WebsiteRecord.objects.all().only('pk', 'label')
    record_data_list = ",".join(
        ['{"pk": ' + str(record.pk) + ', "label": "' + record.label + '"}' for record in record_data])
    json_data = json.loads('{"records": [' + record_data_list + ']}')
    return Response(data=json_data, status=status.HTTP_200_OK)



########################################################
# WebsiteRecord CRUD operations

def add_record(request):
    """
    Adds a new :class: `WebsiteRecord` to the database.
    @param request: the request that for routed to this API endpoint
    @return: the request response
    """
    json_data = request.body.decode('utf-8')
    try:
        record = WebsiteRecord.objects.create_record(json_data)
        tags = []
        if 'tags' in request.data:
            tags = [Tag.objects.create_tag(record, tag.strip()) for tag in request.data['tags'].split(',')]
            with transaction.atomic():
                # atomic to preserve consistency
                record.save()
                for tag in tags:
                    if len(tag.tag.strip()) > 0:  # non-empty string
                        tag.save()

        # Run crawling
        try:
            task = manage_tasks(record)
        except Execution:
            return Response({"error": "Celery server crashed processing the request!"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": f"Record and its tags created successfully! (1 record, {len(tags)} tags)",
                         "taskId": task, "pk": record.pk},
                        status=status.HTTP_201_CREATED)
    except (ValueError, DatabaseError, IntegrityError, transaction.TransactionManagementError):
        return Response({"error": "Invalid record parameters entered!"}, status=status.HTTP_400_BAD_REQUEST)


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
        record = WebsiteRecord.objects.filter(pk=record_id)
        if record:
            stop_periodic_task(record)
            record.delete()
            return Response({"message": "Record deleted successfully!"}, status=status.HTTP_200_OK)
        return Response({"error": "Could not find and delete selected record."}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "No Website Record ID for deleting provided!"}, status=status.HTTP_400_BAD_REQUEST)


def get_record(request):
    """
    Retrieves details of a single :class: `WebsiteRecord`. Tag primary keys are swapped for their values.
    @param request: the request of the record
    @return: requested data, an error 404 if requested record could not be found,
             error 400 if ID field was not found or is not numeric
    """
    if 'record' in request.query_params:
        record = request.query_params.get('record')
        if record.isnumeric():
            record_id = int(record)
            record = WebsiteRecord.objects.select_related().filter(pk=record_id)
            if len(record) > 0:
                json_serializer = serializers.get_serializer("json")
                serializer = json_serializer()
                tags = get_tags(record)
                serialized = json.loads(serializer.serialize(record))
                serialized[0]['fields']['tags'] = tags[record_id]
                return Response(serialized, status=status.HTTP_200_OK)
            return Response({"error": f"Record with ID {record_id} was not found!"}, status=status.HTTP_404_NOT_FOUND)
    return Response(
        {"error": "Invalid request! The request must contain the 'record' key with ID specified as a numeric value."},
        status=status.HTTP_400_BAD_REQUEST)


def update_record(request):
    """
    Updates a record data.
    @param request: the request that for routed to this API endpoint
    @return: the request response
    """
    json_data = request.body.decode('utf-8')
    if WebsiteRecord.objects.update_record(json_data):
        update_tags(request.data)

        # Would not get here if ID not present
        # OPTIONAL: Figure something better
        data = json.loads(json_data)

        # Run crawling
        try:
            task = manage_tasks(WebsiteRecord.objects.get(id=data['id']), True)
        except Exception:
            return Response({"error": "Celery server crashed processing the request!"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": f"Record was updated successfully!",
                         "taskId": task}, status=status.HTTP_204_NO_CONTENT)
    return Response({"error": "Invalid data! Record was not updated."}, status=status.HTTP_400_BAD_REQUEST)


########################################################
# Helper functions

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
        records = records.filter(url__icontains=request.query_params.get('url-filter'))

    if 'label-filter' in request.query_params and request.query_params.get('label-filter') is not None:
        records = records.filter(label__icontains=request.query_params.get('label-filter'))

    if 'tag-filter' in request.query_params and request.query_params.get('tag-filter') is not None:
        records = [record for record in records if
                   has_tag(record.tag_set.all(), request.query_params.get('tag-filter'))]

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
        for tag in record.tag_set.all():
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
    json_serializer = serializers.get_serializer("json")
    serializer = json_serializer()
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


def update_tags(data) -> None:
    """
    Updates the tags of the :class: `WebsiteRecord` specified in the data under key 'id'.
    @param data: the data with record ID and tags to be added/removed for the record
    """
    if 'tags' in data:
        record = WebsiteRecord.objects.select_related().filter(pk=data['id'])[0]  # get record and its tags
        new_tags = set(data['tags'].split(','))  # a set of tags that we want to have associated at the end

        for tag in record.tag_set.all():
            tag_value = tag.tag.strip()
            if len(tag_value) == 0:
                continue
            if tag_value in new_tags:
                # preserved tag
                new_tags.remove(tag_value)  # remove from our consideration - was present, will be present
            else:
                # removed tag
                tag.delete()  # remove from DB

        created_tags = []
        for tag in new_tags:
            # added tag
            added_tag = Tag.objects.create_tag(record, tag.strip())
            created_tags.append(added_tag)  # add to list for later save operation
            record.tag_set.add(added_tag)  # add new tag

        with transaction.atomic():
            # atomic to preserve consistency
            record.save()  # save tag changes
            for tag in created_tags:
                tag.save()


def add_execution_details(response_dict):
    for model in response_dict['records']:
        pk = model['pk']
        executions = Execution.objects.filter(website_record=pk).order_by('-id')  # sort by ID DESC
        if len(executions) > 0:
            model['last_crawl'] = executions[0].last_crawl.strftime("%Y-%m-%d %H:%M:%S")
            model['last_status'] = status_mapper[executions[0].status]
        else:
            model['last_crawl'] = 'N/A'
            model['last_status'] = status_mapper[4]
    return response_dict


def get_sort_details(request):
    if 'sort_property' in request.query_params:
        sort_property = request.query_params.get('sort_property')
    else:
        sort_property = None
    if sort_property is None or sort_property not in (
            'label', 'last_crawl', 'url') or 'sort_order' not in request.query_params:
        return None, False
    return sort_property, False if request.query_params.get('sort_order') == 'ASC' else True
