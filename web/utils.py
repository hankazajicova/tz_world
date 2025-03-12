import logging

from rest_framework.response import Response
from rest_framework.request import Request

logger = logging.getLogger(__name__)


def get_value_from_request(request: Request, key: str, default=None):
    return request.GET.get(key, default)


def handle_error_response(error_message: str) -> Response:
    logger.error(error_message)

    return Response({'error': error_message}, status=400)


def is_valid_lat_lon(lat: float, lon: float) -> bool:
    return -90 <= lat <= 90 and -180 <= lon <= 180


def try_float_or_none(value: str) -> float | None:
    try:
        return float(value) if value else None
    except ValueError:
        return None
