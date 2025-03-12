import itertools
import logging

from django.conf import settings
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from rest_framework import viewsets
from rest_framework.response import Response

from .models import TimezoneGeneral, TimezoneShape
from .serializers import TimezoneSerializer
from .utils import (
    get_value_from_request,
    handle_error_response,
    is_valid_lat_lon,
    try_float_or_none,
)

logger = logging.getLogger(__name__)


class TimezoneViewSet(viewsets.ViewSet):
    UNINHABITED = 'uninhabited'
    TERRITORIAL_SEA_RADIUS = 12  # nautical miles

    def list(self, request):
        lat, lon = self._get_lat_lon_from_request(request)

        if lat is None and lon is None:
            return self._list_all_timezones_response()

        if lat is None or lon is None or not is_valid_lat_lon(lat, lon):
            return handle_error_response("Please provide both valid 'lat' and 'lon'")

        return self._list_single_timezone_response(lat, lon)

    def _get_lat_lon_from_request(self, request) -> tuple[float | None, float | None]:
        lat = try_float_or_none(get_value_from_request(request, 'lat'))
        lon = try_float_or_none(get_value_from_request(request, 'lon'))

        return lat, lon

    def _list_all_timezones_response(self) -> Response:
        queryset = self._list_all_timezones()
        serializer = TimezoneSerializer(queryset, many=True)

        return Response(serializer.data)

    def _list_single_timezone_response(self, lat: float, lon: float) -> Response:
        item, location_message = self._get_single_timezone(lat, lon)
        if not item:
            return handle_error_response(
                f'Timezone not found for the provided location at lat: {lat}, lon: {lon}'
            )

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
        point = GEOSGeometry(f'POINT({lon} {lat})', srid=settings.EPSG_WGS84)

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
