from django.test import SimpleTestCase
from django.test.client import RequestFactory

from web.utils import is_valid_lat_lon, try_float_or_none
from web.views import TimezoneViewSet


class ValidLatLonTest(SimpleTestCase):
    def test_valid_lat_lon(self):
        self.assertTrue(is_valid_lat_lon(0, 0))
        self.assertTrue(is_valid_lat_lon(90, 180))
        self.assertTrue(is_valid_lat_lon(-90, -180))

    def test_invalid_lat_lon(self):
        self.assertFalse(is_valid_lat_lon(91, 0))
        self.assertFalse(is_valid_lat_lon(0, 181))
        self.assertFalse(is_valid_lat_lon(-91, 0))
        self.assertFalse(is_valid_lat_lon(0, -181))


class TryFloatOrNoneTest(SimpleTestCase):
    def test_float(self):
        self.assertEqual(try_float_or_none('0'), 0)
        self.assertEqual(try_float_or_none('1.5'), 1.5)

    def test_none(self):
        self.assertIsNone(try_float_or_none(None))
        self.assertIsNone(try_float_or_none(''))
        self.assertIsNone(try_float_or_none('abc'))


class TimezoneViewSetTest(SimpleTestCase):
    def setUp(self):
        self.view = TimezoneViewSet()

    def test_get_lat_lon_from_request(self):
        rf = RequestFactory()
        request = rf.get('/timezones?lat=0&lon=0')
        lat, lon = self.view._get_lat_lon_from_request(request)
        self.assertEqual(lat, 0)
        self.assertEqual(lon, 0)
