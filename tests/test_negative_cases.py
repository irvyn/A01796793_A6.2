"""Negative unit tests for src.models error handling and validations."""
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


def _capture_stdout(func, *args, **kwargs) -> tuple[str, any]:
    """Run func(*args, **kwargs) capturing stdout."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        result = func(*args, **kwargs)
    return buf.getvalue(), result


class TestNegativeCases(unittest.TestCase):
    """Collection of explicit negative scenarios (≥5) for rubric compliance."""

    def setUp(self):
        """Reset JSON files with empty lists before each test."""
        os.makedirs(DATA_DIR, exist_ok=True)
        _safe_save_json(os.path.join(DATA_DIR, "hotels.json"), [])
        _safe_save_json(os.path.join(DATA_DIR, "customers.json"), [])
        _safe_save_json(os.path.join(DATA_DIR, "reservations.json"), [])

    def test_hotel_total_rooms_negative(self):
        """total_rooms cannot be negative."""
        with self.assertRaises(ValueError):
            Hotel(
                id="HNEG",
                name="X",
                city="Y",
                total_rooms=-1,
                available_rooms=0,
            )

    def test_hotel_available_rooms_greater_than_total(self):
        """available_rooms cannot exceed total_rooms."""
        with self.assertRaises(ValueError):
            Hotel(
                id="HOVR",
                name="X",
                city="Y",
                total_rooms=1,
                available_rooms=2,
            )

    def test_reservation_checkin_after_checkout(self):
        """check_in must be strictly earlier than check_out."""
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
        """Status must be in {'ACTIVE', 'CANCELLED'}."""
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
        """Missing file should return empty list and print a warning."""
        path = os.path.join(DATA_DIR, "hotels.json")
        if os.path.exists(path):
            os.remove(path)

        out, hotels = _capture_stdout(Hotel.load_all)
        self.assertEqual(hotels, [])
        self.assertIn("no encontrado", out.lower())

    def test_load_json_empty_file(self):
        """Empty file should return empty list and print a warning."""
        path = os.path.join(DATA_DIR, "customers.json")
        with open(path, "w", encoding="utf-8") as fcu:
            fcu.write("")

        out, customers = _capture_stdout(Customer.load_all)
        self.assertEqual(customers, [])
        self.assertIn("vacío", out.lower())

    def test_load_json_malformed_not_list(self):
        """Valid JSON but not a list should be ignored gracefully."""
        path = os.path.join(DATA_DIR, "reservations.json")
        with open(path, "w", encoding="utf-8") as frs:
            frs.write('{"id": "R1"}')  # objeto, no lista

        out, reservations = _capture_stdout(Reservation.load_all)
        self.assertEqual(reservations, [])
        self.assertIn("no contiene una lista", out.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
