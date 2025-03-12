import itertools
import logging

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from rest_framework import viewsets
from rest_framework.response import Response

from .models import TimezoneGeneral, TimezoneShape
from .serializers import TimezoneSerializer
from .utils import _check_lat_lon, _get_value_from_request, _try_float_or_none

logger = logging.getLogger(__name__)


class TimezoneViewSet(viewsets.ViewSet):
    UNINHABITED = 'uninhabited'
    TERITORIAL_SEE_RADIUS = 12  # nautical miles

    def list(self, request):
        lat = _try_float_or_none(_get_value_from_request(request, 'lat'))
        lon = _try_float_or_none(_get_value_from_request(request, 'lon'))
        is_valid, message = _check_lat_lon(lat, lon)
        if message:
            return Response({'error': message}, status=400)

        if not is_valid:
            queryset = list(
                itertools.chain(
                    TimezoneShape.objects.exclude(name=self.UNINHABITED).distinct('name'),
                    TimezoneGeneral.objects.all(),
                )
            )
            serializer = TimezoneSerializer(queryset, many=True)
            return Response(serializer.data)

        point = GEOSGeometry(f'POINT({lon} {lat})', srid=4326)

        # Check if the point is in the shapefile or within the territorial waters
        item = (
            TimezoneShape.objects.exclude(name=self.UNINHABITED)
            .filter(poly__distance_lte=(point, D(nm=self.TERITORIAL_SEE_RADIUS)))
            .annotate(distance=Distance('poly', point))
            .order_by('distance')
            .first()
        )

        if not item:
            item = TimezoneGeneral.objects.filter(long_min__lte=lon, long_max__gte=lon).first()
            if not item:
                return Response({'error': 'Invalid longtitude'}, status=400)

        serializer = TimezoneSerializer(item)
        return Response(serializer.data)
