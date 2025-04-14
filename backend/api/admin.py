from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Manager)
admin.site.register(Machine)
admin.site.register(Workflow)
admin.site.register(Availability)
admin.site.register(Task)