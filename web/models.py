from django.contrib.gis.db import models


class TimezoneShape(models.Model):
    name = models.CharField(max_length=255)
    poly = models.PolygonField(srid=4326)

    def __str__(self):
        return self.name


class TimezoneGeneral(models.Model):
    name = models.CharField(max_length=255)
    long_min = models.FloatField()
    long_max = models.FloatField()

    def __str__(self):
        return self.name
