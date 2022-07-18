from rest_framework import status
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from celery.result import AsyncResult
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view


@swagger_auto_schema(
    method='get',
    operation_description='Returns status of the asynchronous task associated with given ID.',
    manual_parameters=[
        openapi.Parameter('task_id', openapi.IN_PATH,
                          "UUID of the asynchronous task",
                          type=openapi.TYPE_STRING,
                          required=True)
    ],
    responses={
        200: openapi.Response('Graph data for the request.', examples={"application/json": {
            "task_id": 'uuahf1553sdh',
            "task_status": 'PENDING',
            "task_result": 'None'
        }}),
        400: openapi.Response('Task under the given ID does not exist.')
    },
    tags=['Tasks'])
@api_view(['GET'])
@csrf_exempt
def get_status(request, task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return Response(data=result, status=status.HTTP_200_OK)
