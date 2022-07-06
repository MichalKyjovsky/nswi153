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
    path('graph/<record>/', views.get_graph, name='get_graph'),
    path('record/add/', views.add_record, name='add_record'),
    path('record/delete/', views.delete_record, name='delete_record'),
    path('record/<page>/', views.get_records, name='get_records'),
    path('executions/<page>/', views.get_executions, name='get_executions'),
    path('execution/<record>/<page>/', views.get_execution, name='get_execution'),
    path('activate/<record>/', views.activate, name='activate_record'),
    path('deactivate/<record>/', views.deactivate, name='deactivate_record'),
    path('record/update/', views.update_record, name='update_record'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='api_docs')
]
