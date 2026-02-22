from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from typing import List, Dict, Any

import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

def _safe_load_json(path: str) -> List[Dict[str, Any]]:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                print(f"Warning: '{path}' vacío. Se asume lista vacía.")
                return []
            data = json.loads(content)
            if isinstance(data, list):
                return data
            print(f"Error: '{path}' no contiene una lista JSON. Se asume lista vacía.")
            return []
    except FileNotFoundError:
        print(f"Warning: '{path}' no encontrado. Se creará al guardar.")
        return []
    except json.JSONDecodeError as exc:
        print(f"Error: JSON inválido en '{path}': {exc}. Se asume lista vacía.")
        return []
    except OSError as exc:
        print(f"Error de E/S al leer '{path}': {exc}. Se asume lista vacía.")
        return []


def _safe_save_json(path: str, data: List[Dict[str, Any]]) -> None:
    """Save a JSON list to *path* with pretty formatting.

    Prints errors but does not raise, to comply with the requirement that
    execution continues despite file errors.
    """
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError as exc:
        print(f"Error de E/S al escribir '{path}': {exc}.")


# ---------------------------- Models ---------------------------- #

@dataclass
class Hotel:
    id: str
    name: str
    city: str
    total_rooms: int
    available_rooms: int

    def __post_init__(self) -> None:
        if self.total_rooms < 0:
            raise ValueError("total_rooms no puede ser negativo")
        if not (0 <= self.available_rooms <= self.total_rooms):
            raise ValueError("available_rooms debe estar entre 0 y total_rooms")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Hotel':
        return cls(**data)

    # ---- Collection I/O ----
    @staticmethod
    def _path() -> str:
        return os.path.join(DATA_DIR, 'hotels.json')

    @classmethod
    def load_all(cls) -> List['Hotel']:
        return [cls.from_dict(d) for d in _safe_load_json(cls._path())]

    @classmethod
    def save_all(cls, hotels: List['Hotel']) -> None:
        _safe_save_json(cls._path(), [h.to_dict() for h in hotels])


@dataclass
class Customer:
    id: str
    name: str
    email: str
    phone: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Customer':
        return cls(**data)

    @staticmethod
    def _path() -> str:
        return os.path.join(DATA_DIR, 'customers.json')

    @classmethod
    def load_all(cls) -> List['Customer']:
        return [cls.from_dict(d) for d in _safe_load_json(cls._path())]

    @classmethod
    def save_all(cls, customers: List['Customer']) -> None:
        _safe_save_json(cls._path(), [c.to_dict() for c in customers])


@dataclass
class Reservation:
    id: str
    hotel_id: str
    customer_id: str
    room_number: int
    check_in: date | str
    check_out: date | str
    status: str = field(default='ACTIVE')  # ACTIVE | CANCELLED

    def __post_init__(self) -> None:
        # Normalize dates if provided as strings
        if isinstance(self.check_in, str):
            self.check_in = _parse_date(self.check_in)
        if isinstance(self.check_out, str):
            self.check_out = _parse_date(self.check_out)
        # Basic validations
        if self.check_in >= self.check_out:
            raise ValueError("check_in debe ser anterior a check_out")
        if self.status not in {"ACTIVE", "CANCELLED"}:
            raise ValueError("status debe ser 'ACTIVE' o 'CANCELLED'")

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Serialize dates to ISO strings
        d['check_in'] = self.check_in.isoformat()
        d['check_out'] = self.check_out.isoformat()
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Reservation':
        return cls(**data)

    @staticmethod
    def _path() -> str:
        return os.path.join(DATA_DIR, 'reservations.json')

    @classmethod
    def load_all(cls) -> List['Reservation']:
        reservations: List['Reservation'] = []
        for d in _safe_load_json(cls._path()):
            try:
                reservations.append(cls.from_dict(d))
            except (ValueError, TypeError) as exc:
                print(f"Error al cargar reserva {d.get('id', '<sin id>')}: {exc}. Se omite.")
        return reservations

    @classmethod
    def save_all(cls, reservations: List['Reservation']) -> None:
        _safe_save_json(cls._path(), [r.to_dict() for r in reservations])


# ------------------------- Helper functions ------------------------- #

def _parse_date(value: str) -> date:
    """Parse an ISO-8601 date string (YYYY-MM-DD) into a date.

    Prints an error and raises ValueError on invalid format.
    """
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError as exc:
        print(f"Error de fecha inválida '{value}': {exc}")
        raise


def find_hotel(hotels: List[Hotel], hotel_id: str) -> Hotel | None:
    return next((h for h in hotels if h.id == hotel_id), None)


def find_customer(customers: List[Customer], customer_id: str) -> Customer | None:
    return next((c for c in customers if c.id == customer_id), None)


def find_reservation(reservations: List[Reservation], reservation_id: str) -> Reservation | None:
    return next((r for r in reservations if r.id == reservation_id), None)