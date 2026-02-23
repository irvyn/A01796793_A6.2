"""Unit tests for src.models core behaviors.

Covers JSON load/save, validations, error handling and roundtrip serialization.
"""
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


class TestModels(unittest.TestCase):
    """Tests for Hotel, Customer and Reservation models."""

    def setUp(self):
        """Prepare clean JSON files and baseline entities before each test."""
        os.makedirs(DATA_DIR, exist_ok=True)
        self.hotels_data = [
            {
                "id": "H001",
                "name": "Test Hotel",
                "city": "Chihuahua",
                "total_rooms": 3,
                "available_rooms": 2,
            }
        ]
        self.customers_data = [
            {
                "id": "C001",
                "name": "Cliente Uno",
                "email": "c1@example.com",
                "phone": "111",
            }
        ]
        today = date.today()
        self.reservations_data = [
            {
                "id": "R001",
                "hotel_id": "H001",
                "customer_id": "C001",
                "room_number": 101,
                "check_in": (today + timedelta(days=1)).isoformat(),
                "check_out": (today + timedelta(days=3)).isoformat(),
                "status": "ACTIVE",
            }
        ]

        _safe_save_json(
            os.path.join(DATA_DIR, "hotels.json"),
            self.hotels_data,
        )
        _safe_save_json(
            os.path.join(DATA_DIR, "customers.json"),
            self.customers_data,
        )
        _safe_save_json(
            os.path.join(DATA_DIR, "reservations.json"),
            self.reservations_data,
        )

    def test_load_all_ok(self):
        """Load baseline JSON data for all entities."""
        hotels = Hotel.load_all()
        customers = Customer.load_all()
        reservations = Reservation.load_all()

        self.assertEqual(len(hotels), 1)
        self.assertEqual(len(customers), 1)
        self.assertEqual(len(reservations), 1)
        self.assertEqual(hotels[0].name, "Test Hotel")
        self.assertEqual(customers[0].email, "c1@example.com")
        self.assertEqual(reservations[0].status, "ACTIVE")

    def test_save_and_reload_hotel(self):
        """Append a new hotel, save and reload to verify persistence."""
        hotels = Hotel.load_all()
        hotels.append(
            Hotel(
                id="H002",
                name="Nuevo",
                city="Cuauhtémoc",
                total_rooms=5,
                available_rooms=5,
            )
        )
        Hotel.save_all(hotels)

        reloaded = Hotel.load_all()
        ids = [h.id for h in reloaded]
        self.assertIn("H002", ids)

    def test_hotel_validation_available_not_exceed_total(self):
        """available_rooms must not exceed total_rooms."""
        with self.assertRaises(ValueError):
            Hotel(
                id="HX",
                name="X",
                city="Y",
                total_rooms=2,
                available_rooms=3,
            )

    def test_reservation_invalid_dates(self):
        """check_in must be earlier than check_out."""
        today = date.today()
        with self.assertRaises(ValueError):
            Reservation(
                id="R_BAD",
                hotel_id="H001",
                customer_id="C001",
                room_number=100,
                check_in=(today + timedelta(days=3)).isoformat(),
                check_out=(today + timedelta(days=2)).isoformat(),
                status="ACTIVE",
            )

    def test_reservation_invalid_status(self):
        """Status must be either ACTIVE or CANCELLED."""
        today = date.today()
        with self.assertRaises(ValueError):
            Reservation(
                id="R_BAD_STATUS",
                hotel_id="H001",
                customer_id="C001",
                room_number=100,
                check_in=(today + timedelta(days=1)).isoformat(),
                check_out=(today + timedelta(days=2)).isoformat(),
                status="PENDING",
            )

    def test_load_corrupted_json(self):
        """Reading a corrupted JSON should print an error"""
        path = os.path.join(DATA_DIR, "hotels.json")
        with open(path, "w", encoding="utf-8") as fhl:
            fhl.write("{ this is not valid json }")

        out, hotels = _capture_stdout(Hotel.load_all)
        self.assertEqual(hotels, [])
        self.assertIn("JSON inválido", out)

    def test_reservation_to_from_dict_roundtrip(self):
        """Roundtrip to_dict/from_dict should preserve key fields."""
        today = date.today()
        rsv = Reservation(
            id="R10",
            hotel_id="H001",
            customer_id="C001",
            room_number=105,
            check_in=(today + timedelta(days=1)).isoformat(),
            check_out=(today + timedelta(days=2)).isoformat(),
            status="ACTIVE",
        )
        dct = rsv.to_dict()
        rsv2 = Reservation.from_dict(dct)
        self.assertEqual(rsv2.id, rsv.id)
        self.assertEqual(rsv2.check_in, rsv.check_in)
        self.assertEqual(rsv2.check_out, rsv.check_out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
