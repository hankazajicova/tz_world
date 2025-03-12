import logging

from rest_framework.response import Response

logger = logging.getLogger(__name__)


def _get_value_from_request(request, key, default=None):
    return request.GET.get(key, default)


def _is_valid_lat_lon(lat: float, lon: float) -> bool:
    return -90 <= lat <= 90 and -180 <= lon <= 180


def _check_lat_lon(lat: float | None, lon: float | None) -> tuple[bool, str | None]:
    if lat is None and lon is None:
        return False, None

    if lat is None or lon is None or not _is_valid_lat_lon(lat, lon):
        return False, "Please provide both valid 'lat' and 'lon'"

    return True, None


def _try_float_or_none(value: str) -> float | None:
    try:
        return float(value) if value else None
    except ValueError:
        return None


def _handle_error_response(error_message: str) -> Response:
    logger.error(error_message)

    return Response({'error': error_message}, status=400)
