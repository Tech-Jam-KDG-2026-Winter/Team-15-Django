from django.contrib import admin
from .models import CustomUser, ConditionLog, ExerciseMenu, Routine

admin.site.register(CustomUser)
admin.site.register(ConditionLog)
admin.site.register(ExerciseMenu)
admin.site.register(Routine)
