from django.contrib import admin
from .models import Equipment, Dataset

@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ['filename', 'uploaded_at', 'total_records']
    list_filter = ['uploaded_at']
    search_fields = ['filename']

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['equipment_name', 'equipment_type', 'flowrate', 'pressure', 'temperature', 'uploaded_at']
    list_filter = ['equipment_type', 'uploaded_at']
    search_fields = ['equipment_name', 'equipment_type']
