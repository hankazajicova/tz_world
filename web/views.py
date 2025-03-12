import itertools
import logging

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from rest_framework import viewsets
from rest_framework.response import Response

from .models import TimezoneGeneral, TimezoneShape
from .serializers import TimezoneSerializer
from .utils import (
    _check_lat_lon,
    _get_value_from_request,
    _handle_error_response,
    _try_float_or_none,
)

logger = logging.getLogger(__name__)


class TimezoneViewSet(viewsets.ViewSet):
    UNINHABITED = 'uninhabited'
    TERRITORIAL_SEA_RADIUS = 12  # nautical miles

    def list(self, request):
        lat, lon = self._get_lat_lon_from_request(request)
        is_valid, error_message = _check_lat_lon(lat, lon)

        if error_message:
            return _handle_error_response(error_message)

        if not is_valid:
            return self._list_all_timezones_response()

        return self._list_single_timezone_response(lat, lon)

    def _get_lat_lon_from_request(self, request) -> tuple[float | None, float | None]:
        lat = _try_float_or_none(_get_value_from_request(request, 'lat'))
        lon = _try_float_or_none(_get_value_from_request(request, 'lon'))

        return lat, lon

    def _list_all_timezones_response(self) -> Response:
        queryset = self._list_all_timezones()
        serializer = TimezoneSerializer(queryset, many=True)

        return Response(serializer.data)

    def _list_single_timezone_response(self, lat: float, lon: float) -> Response:
        item, location_message = self._get_single_timezone(lat, lon)
        if not item:
            return _handle_error_response('Timezone not found for the provided location')

        logger.info(
            f'Location at lat: {lat}, lon: {lon} is {location_message} within the {item.name} timezone'
        )

        serializer = TimezoneSerializer(item)
        return Response(serializer.data)

    def _list_all_timezones(self) -> list:
        items = list(
            itertools.chain(
                TimezoneShape.objects.exclude(name=self.UNINHABITED).distinct('name'),
                TimezoneGeneral.objects.all(),
            )
        )

        return items

    def _get_single_timezone(
        self, lat: float, lon: float
    ) -> tuple[TimezoneGeneral | TimezoneShape, str]:
        point = GEOSGeometry(f'POINT({lon} {lat})', srid=4326)

        # Check if the point is in the shapefile or within the territorial sea
        item = (
            TimezoneShape.objects.filter(
                poly__distance_lte=(point, D(nm=self.TERRITORIAL_SEA_RADIUS))
            )
            .annotate(distance=Distance('poly', point))
            .order_by('distance')
            .first()
        )

        location_message = 'in territorial sea' if item and item.distance.m > 0 else 'on land'
        is_uninhabited = item.name == self.UNINHABITED if item else False

        if not item or is_uninhabited:
            item = TimezoneGeneral.objects.filter(long_min__lte=lon, long_max__gte=lon).first()

            location_message = (
                'in international waters' if not is_uninhabited else 'in an uninhabited area'
            )

        return item, location_message
