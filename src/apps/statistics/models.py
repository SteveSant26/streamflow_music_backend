from django.db import models


class StatisticsModel(models.Model):
    """Modelo proxy para las estadísticas - no crea tabla nueva"""
    
    class Meta:
        managed = False  # No crear tabla en la BD
        verbose_name = "Estadística"
        verbose_name_plural = "Estadísticas"
