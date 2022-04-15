from django.contrib import admin
from model import DataModel
# Register your models here.

admin.site.register(DataModel.WebsiteRecord, DataModel.Tag, DataModel.Node, DataModel.Edge, DataModel.Execution, DataModel.ExecutionLink)
