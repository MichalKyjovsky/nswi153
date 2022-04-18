from django.urls import path
from . import views

urlpatterns = [
    path('graph/<record>/', views.get_graph, name='get_graph'),
    path('record/add/', views.add_record, name='add_record'),
    path('record/delete/', views.delete_record, name='delete_record'),
    path('record/<page>/', views.get_records, name='get_records'),
    path('executions/<page>/', views.get_executions, name='get_executions'),
    path('execution/<record>/<page>/', views.get_execution, name='get_execution'),
    path('stats/', views.get_stats, name='get_statistics'),
    path('activate/<record>/', views.activate, name='activate_record'),
    path('deactivate/<record>/', views.deactivate, name='deactivate_record'),
    path('record/update/', views.update_record, name='update_record')
]
