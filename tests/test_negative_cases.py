import io
import os
import unittest
from contextlib import redirect_stdout
from datetime import date, timedelta

from src.models import (
    Hotel,
    Customer,
    Reservation,
    DATA_DIR,
    _safe_save_json,
)


class TestNegativeCases(unittest.TestCase):
    def setUp(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        _safe_save_json(os.path.join(DATA_DIR, "hotels.json"), [])
        _safe_save_json(os.path.join(DATA_DIR, "customers.json"), [])
        _safe_save_json(os.path.join(DATA_DIR, "reservations.json"), [])

    def test_hotel_total_rooms_negative(self):
        with self.assertRaises(ValueError):
            Hotel(id="HNEG", name="X", city="Y", total_rooms=-1, available_rooms=0)

    def test_hotel_available_rooms_greater_than_total(self):
        with self.assertRaises(ValueError):
            Hotel(id="HOVR", name="X", city="Y", total_rooms=1, available_rooms=2)

    def test_reservation_checkin_after_checkout(self):
        today = date.today()
        with self.assertRaises(ValueError):
            Reservation(
                id="RNEG",
                hotel_id="H001",
                customer_id="C001",
                room_number=1,
                check_in=(today + timedelta(days=5)).isoformat(),
                check_out=(today + timedelta(days=4)).isoformat(),
                status="ACTIVE",
            )

    def test_reservation_invalid_status_value(self):
        today = date.today()
        with self.assertRaises(ValueError):
            Reservation(
                id="RSTAT",
                hotel_id="H001",
                customer_id="C001",
                room_number=2,
                check_in=(today + timedelta(days=1)).isoformat(),
                check_out=(today + timedelta(days=2)).isoformat(),
                status="UNKNOWN",
            )

    def test_load_json_file_not_found(self):
        path = os.path.join(DATA_DIR, "hotels.json")
        if os.path.exists(path):
            os.remove(path)

        buf = io.StringIO()
        with redirect_stdout(buf):
            hotels = Hotel.load_all()
        output = buf.getvalue()

        self.assertEqual(hotels, [])
        self.assertIn("no encontrado", output.lower())

    def test_load_json_empty_file(self):
        path = os.path.join(DATA_DIR, "customers.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write("")

        buf = io.StringIO()
        with redirect_stdout(buf):
            customers = Customer.load_all()
        output = buf.getvalue()

        self.assertEqual(customers, [])
        self.assertIn("vacío", output.lower())

    def test_load_json_malformed_not_list(self):
        path = os.path.join(DATA_DIR, "reservations.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write('{"id": "R1"}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            reservations = Reservation.load_all()
        output = buf.getvalue()

        self.assertEqual(reservations, [])
        self.assertIn("no contiene una lista", output.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)