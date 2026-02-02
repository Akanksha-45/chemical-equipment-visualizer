from django.db import models

class Dataset(models.Model):
    """Stores metadata about uploaded CSV files"""
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    total_records = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.filename} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"

class Equipment(models.Model):
   
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='equipment', null=True, blank=True)
    equipment_name = models.CharField(max_length=200)
    equipment_type = models.CharField(max_length=100)
    flowrate = models.FloatField()
    pressure = models.FloatField()
    temperature = models.FloatField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.equipment_name} ({self.equipment_type})"
