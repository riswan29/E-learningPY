from django.contrib import admin
from .models import *
from django.db import models
# from django.utils.translation import ugettext_lazy as _
from datetime import date

# Register your models here.

class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'deadline', 'semester', 'departement', 'author')
    list_filter = ('semester',('deadline', admin.DateFieldListFilter))
    search_fields = ('title', 'description', 'author__username')
    list_per_page = 10

    
admin.site.register(CustomUser)
admin.site.register(JadwalMengajar)
admin.site.register(Assignment,AssignmentAdmin)
admin.site.register(Submission)
admin.site.register(AssignmentGrade)