from django.urls import path
from . import views

urlpatterns = [
    path('graph/<record>/', views.get_graph, name='get graph'),
    path('record/add/', views.add_record, name='add record'),
    path('record/delete/', views.delete_record, name='delete record'),
    path('record/<page>/', views.get_records, name='get records'),
    path('executions/<page>/', views.get_executions, name='get executions'),
    path('execution/<record>/', views.get_execution, name='get execution'),
    path('stats/', views.get_stats, name='get statistics'),
    path('activate/<record>/', views.activate, name='activate record'),
    path('deactivate/<record>/', views.deactivate, name='deactivate record'),
    path('record/update/', views.update_record, name='update record')
]
