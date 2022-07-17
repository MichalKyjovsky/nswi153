from django.urls import path
from . import views

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Web Crawler API",
        default_version='v1',
        description="Web Crawl simple implementation API documentation",
        terms_of_service="https://www.google.com/policies/terms/",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('graph/', views.get_graph, name='get_graph'),
    path('record/', views.record_crud, name='record_crud'),
    path('record/list/', views.list_records, name='list_records'),
    path('record/<page>/', views.get_records, name='get_records'),
    path('executions/<page>/', views.get_executions, name='get_executions'),
    path('execution/<record>/<page>/', views.get_execution, name='get_execution'),
    path('execution/<record>/', views.start_execution, name='start_execution'),
    path('activate/<record>/', views.activate, name='activate_record'),
    path('deactivate/<record>/', views.deactivate, name='deactivate_record'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='api_docs')
]
