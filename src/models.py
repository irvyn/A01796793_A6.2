"""
Models for a minimal reservation system.

This module defines three dataclasses: Hotel, Customer, and Reservation.
Each class includes serialization helpers (to_dict / from_dict) and
class-level utilities to load/save collections from JSON files in the
`data/` directory with robust error handling (execution continues on
errors).
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from typing import List, Dict, Any
import json
import os


DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
)


def _safe_load_json(path: str) -> List[Dict[str, Any]]:
    """
    Load a JSON list from *path*.

    Returns an empty list if the file does not exist, is empty,
    or contains invalid JSON. Prints the error but does not stop
    execution.
    """
    try:
        with open(path, "r", encoding="utf-8") as fobj:
            content = fobj.read().strip()
            if not content:
                print(f"Warning: '{path}' vacío. Se asume lista vacía.")
                return []
            data = json.loads(content)
            if isinstance(data, list):
                return data
            print(
                "Error: "
                f"'{path}' no contiene una lista JSON. "
                "Se asume lista vacía."
            )
            return []
    except FileNotFoundError:
        print(f"Warning: '{path}' no encontrado. Se creará al guardar.")
        return []
    except json.JSONDecodeError as exc:
        print(
            "Error: "
            f"JSON inválido en '{path}': {exc}. "
            "Se asume lista vacía."
        )
        return []
    except OSError as exc:
        print(
            f"Error de E/S al leer '{path}': {exc}. "
            "Se asume lista vacía."
        )
        return []


def _safe_save_json(path: str, data: List[Dict[str, Any]]) -> None:
    """
    Save a JSON list to *path* with pretty formatting.

    Does not crash on I/O errors; prints an error and continues.
    """
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fobj:
            json.dump(data, fobj, ensure_ascii=False, indent=2)
    except OSError as exc:
        print(f"Error de E/S al escribir '{path}': {exc}.")


# --------------------------------------------------------------------------- #
#                                   MODELS                                    #
# --------------------------------------------------------------------------- #

@dataclass
class Hotel:
    """Represents a hotel with its basic capacity information."""

    id: str
    name: str
    city: str
    total_rooms: int
    available_rooms: int

    def __post_init__(self) -> None:
        """Validate capacity constraints."""
        if self.total_rooms < 0:
            raise ValueError("total_rooms no puede ser negativo")
        if not 0 <= self.available_rooms <= self.total_rooms:
            raise ValueError(
                "available_rooms debe estar entre 0 y total_rooms"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize hotel to dict."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Hotel":
        """Deserialize hotel from dict."""
        return cls(**data)

    @staticmethod
    def _path() -> str:
        """Return JSON path for hotels."""
        return os.path.join(DATA_DIR, "hotels.json")

    @classmethod
    def load_all(cls) -> List["Hotel"]:
        """Load all hotels from persistent file."""
        return [cls.from_dict(dct) for dct in _safe_load_json(cls._path())]

    @classmethod
    def save_all(cls, hotels: List["Hotel"]) -> None:
        """Save all hotels to persistent file."""
        _safe_save_json(cls._path(), [htl.to_dict() for htl in hotels])


@dataclass
class Customer:
    """Represents a customer."""

    id: str
    name: str
    email: str
    phone: str

    def to_dict(self) -> Dict[str, Any]:
        """Serialize customer to dict."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Customer":
        """Deserialize customer from dict."""
        return cls(**data)

    @staticmethod
    def _path() -> str:
        """Return JSON path for customers."""
        return os.path.join(DATA_DIR, "customers.json")

    @classmethod
    def load_all(cls) -> List["Customer"]:
        """Load all customers from persistent file."""
        return [cls.from_dict(dct) for dct in _safe_load_json(cls._path())]

    @classmethod
    def save_all(cls, customers: List["Customer"]) -> None:
        """Save all customers to persistent file."""
        _safe_save_json(cls._path(), [cust.to_dict() for cust in customers])


@dataclass
class Reservation:
    """Represents a reservation linking a customer and a hotel."""

    id: str
    hotel_id: str
    customer_id: str
    room_number: int
    check_in: date | str
    check_out: date | str
    status: str = field(default="ACTIVE")  # ACTIVE | CANCELLED

    def __post_init__(self) -> None:
        """Normalize dates and validate rules."""
        if isinstance(self.check_in, str):
            self.check_in = _parse_date(self.check_in)
        if isinstance(self.check_out, str):
            self.check_out = _parse_date(self.check_out)
        if self.check_in >= self.check_out:
            raise ValueError("check_in debe ser anterior a check_out")
        if self.status not in {"ACTIVE", "CANCELLED"}:
            raise ValueError("status debe ser 'ACTIVE' o 'CANCELLED'")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize reservation to dict with ISO date strings."""
        dct = asdict(self)
        dct["check_in"] = self.check_in.isoformat()
        dct["check_out"] = self.check_out.isoformat()
        return dct

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Reservation":
        """Deserialize reservation from dict."""
        return cls(**data)

    @staticmethod
    def _path() -> str:
        """Return JSON path for reservations."""
        return os.path.join(DATA_DIR, "reservations.json")

    @classmethod
    def load_all(cls) -> List["Reservation"]:
        """
        Load all reservations, skipping malformed entries and printing
        the error.
        """
        reservations: List["Reservation"] = []
        for dct in _safe_load_json(cls._path()):
            try:
                reservations.append(cls.from_dict(dct))
            except (ValueError, TypeError) as exc:
                rid = dct.get("id", "<sin id>")
                print(
                    f"Error al cargar reserva {rid}: {exc}. "
                    "Se omite."
                )
        return reservations

    @classmethod
    def save_all(cls, reservations: List["Reservation"]) -> None:
        """Save all reservations to persistent file."""
        _safe_save_json(cls._path(), [res.to_dict() for res in reservations])


# --------------------------------------------------------------------------- #
#                                 HELPERS                                     #
# --------------------------------------------------------------------------- #

def _parse_date(value: str) -> date:
    """
    Parse ISO date string (YYYY-MM-DD) into date object.
    Raises ValueError for invalid format.
    """
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        print(f"Error de fecha inválida '{value}': {exc}")
        raise


def find_hotel(hotels: List[Hotel], hotel_id: str) -> Hotel | None:
    """Return hotel matching the given ID, or None."""
    return next((htl for htl in hotels if htl.id == hotel_id), None)


def find_customer(
    customers: List[Customer],
    customer_id: str
) -> Customer | None:
    """Return customer matching the given ID, or None."""
    return next((c for c in customers if c.id == customer_id), None)


def find_reservation(
    reservations: List[Reservation],
    reservation_id: str
) -> Reservation | None:
    """Return reservation matching the given ID, or None."""
    return next(
        (
            res
            for res in reservations
            if res.id == reservation_id
        ),
        None,
    )
