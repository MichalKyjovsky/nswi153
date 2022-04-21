from django.contrib import admin
from .models import *

admin.site.register(WebsiteRecord)
admin.site.register(Tag)
admin.site.register(Node)
admin.site.register(Edge)
admin.site.register(Execution)
admin.site.register(ExecutionLink)
