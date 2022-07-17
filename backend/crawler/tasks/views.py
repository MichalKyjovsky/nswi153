from celery.result import AsyncResult
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from celery.result import AsyncResult
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view

from .crawler import run_crawler_task


@swagger_auto_schema(
    methods=['POST'],
    operation_description="Runs a celery process.",
    responses={
        200: openapi.Response('The celery process was run.'),
    },
    tags=['Celery'])
@api_view(['POST'])
@csrf_exempt
def run_crawler_async(request):
    task = run_crawler_task.delay()
    return JsonResponse({"task_id": task.id}, status=202)


@csrf_exempt
def get_status(request, task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return JsonResponse(result, status=200)