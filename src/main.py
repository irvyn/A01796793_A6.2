from __future__ import annotations

import os
from datetime import date, timedelta

from src.models import (
    Hotel,
    Customer,
    Reservation,
    DATA_DIR,
    find_hotel,
    find_customer,
    find_reservation,
    _safe_save_json,
)


def list_hotels() -> None:
    hotels = Hotel.load_all()
    if not hotels:
        print("No hay hoteles.")
        return
    for h in hotels:
        print(f"- {h.id} | {h.name} | {h.city} | {h.available_rooms}/{h.total_rooms} disponibles")


def list_customers() -> None:
    customers = Customer.load_all()
    if not customers:
        print("No hay clientes.")
        return
    for c in customers:
        print(f"- {c.id} | {c.name} | {c.email} | {c.phone}")


def list_reservations() -> None:
    reservations = Reservation.load_all()
    if not reservations:
        print("No hay reservaciones.")
        return
    for r in reservations:
        print(f"- {r.id} | Hotel={r.hotel_id} | Cliente={r.customer_id} | "
              f"Habitación={r.room_number} | {r.check_in}→{r.check_out} | {r.status}")


def create_hotel() -> None:
    hotels = Hotel.load_all()
    _id = input("ID del hotel (ej. H010): ").strip()
    if find_hotel(hotels, _id):
        print("Error: ya existe un hotel con ese ID.")
        return
    name = input("Nombre: ").strip()
    city = input("Ciudad: ").strip()
    total = int(input("Habitaciones totales: ").strip())
    available = int(input("Habitaciones disponibles: ").strip())
    try:
        hotels.append(Hotel(id=_id, name=name, city=city, total_rooms=total, available_rooms=available))
        Hotel.save_all(hotels)
        print("Hotel creado.")
    except ValueError as exc:
        print(f"Error al crear hotel: {exc}")


def create_customer() -> None:
    customers = Customer.load_all()
    _id = input("ID del cliente (ej. C010): ").strip()
    if find_customer(customers, _id):
        print("Error: ya existe un cliente con ese ID.")
        return
    name = input("Nombre: ").strip()
    email = input("Email: ").strip()
    phone = input("Teléfono: ").strip()
    customers.append(Customer(id=_id, name=name, email=email, phone=phone))
    Customer.save_all(customers)
    print("Cliente creado.")


def create_reservation() -> None:
    hotels = Hotel.load_all()
    customers = Customer.load_all()
    reservations = Reservation.load_all()

    hotel_id = input("Hotel ID: ").strip()
    customer_id = input("Customer ID: ").strip()
    room = int(input("Número de habitación: ").strip())
    check_in = input("Check-in (YYYY-MM-DD): ").strip()
    check_out = input("Check-out (YYYY-MM-DD): ").strip()

    if not find_hotel(hotels, hotel_id):
        print("Error: hotel no existe.")
        return
    if not find_customer(customers, customer_id):
        print("Error: cliente no existe.")
        return

    _id = f"R{100 + len(reservations) + 1:03d}"
    try:
        res = Reservation(
            id=_id,
            hotel_id=hotel_id,
            customer_id=customer_id,
            room_number=room,
            check_in=check_in,
            check_out=check_out,
            status="ACTIVE",
        )
        reservations.append(res)
        Reservation.save_all(reservations)
        print(f"Reserva creada con ID: {res.id}")
    except ValueError as exc:
        print(f"Error al crear reserva: {exc}")


def cancel_reservation() -> None:
    reservations = Reservation.load_all()
    res_id = input("ID de la reserva: ").strip()
    res = find_reservation(reservations, res_id)
    if not res:
        print("No existe esa reserva.")
        return
    if res.status == "CANCELLED":
        print("La reserva ya estaba cancelada.")
        return
    res.status = "CANCELLED"
    Reservation.save_all(reservations)
    print("Reserva cancelada.")


def corrupt_hotels_file() -> None:
    """Útil para grabar evidencia de manejo de errores al leer JSON corrupto."""
    path = os.path.join(DATA_DIR, "hotels.json")
    with open(path, "w", encoding="utf-8") as f:
        f.write("{ this is not valid json }")
    print(f"Se corrompió intencionalmente: {path}")


def menu() -> None:
    options = {
        "1": ("Listar hoteles", list_hotels),
        "2": ("Listar clientes", list_customers),
        "3": ("Listar reservaciones", list_reservations),
        "4": ("Crear hotel", create_hotel),
        "5": ("Crear cliente", create_customer),
        "6": ("Crear reservación", create_reservation),
        "7": ("Cancelar reservación", cancel_reservation),
        "8": ("Corromper hotels.json (para evidencia de errores)", corrupt_hotels_file),
        "0": ("Salir", None),
    }
    while True:
        print("\n=== Sistema de Reservaciones (demo) ===")
        for k, (label, _) in options.items():
            print(f"{k}) {label}")
        choice = input("Elige una opción: ").strip()
        if choice == "0":
            print("Adiós.")
            break
        action = options.get(choice)
        if not action:
            print("Opción inválida.")
            continue
        _, fn = action
        try:
            fn()
        except Exception as exc:
            print(f"Error inesperado: {exc}")


if __name__ == "__main__":
    menu()