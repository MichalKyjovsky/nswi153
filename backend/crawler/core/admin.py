from django.contrib import admin
from .model import DataModel
# Register your models here.

admin.site.register(DataModel.WebsiteRecord)
admin.site.register(DataModel.Tag)
admin.site.register(DataModel.Node)
admin.site.register(DataModel.Edge)
admin.site.register(DataModel.Execution)
admin.site.register(DataModel.ExecutionLink)
