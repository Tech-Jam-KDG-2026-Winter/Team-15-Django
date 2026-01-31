from django.contrib import admin
from .models import ConditionLog, ExerciseMenu, Routine, Tag

# Register your models here.
admin.site.register(ConditionLog)
admin.site.register(ExerciseMenu)
admin.site.register(Routine)
admin.site.register(Tag) 

