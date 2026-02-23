"""Console menu for demo and recording evidence.

Provides minimal operations to list and create entities, and to
demonstrate error handling with corrupted JSON files.
"""
from __future__ import annotations

import os

from src.models import (
    Hotel,
    Customer,
    Reservation,
    DATA_DIR,
    find_hotel,
    find_customer,
    find_reservation,
)


def list_hotels() -> None:
    """List hotels with availability."""
    hotels = Hotel.load_all()
    if not hotels:
        print("No hay hoteles.")
        return
    for htl in hotels:
        info = (
            f"- {htl.id} | {htl.name} | {htl.city} | "
            f"{htl.available_rooms}/{htl.total_rooms} disponibles"
        )
        print(info)


def list_customers() -> None:
    """List customers."""
    customers = Customer.load_all()
    if not customers:
        print("No hay clientes.")
        return
    for cust in customers:
        info = (
            f"- {cust.id} | {cust.name} | {cust.email} | "
            f"{cust.phone}"
        )
        print(info)


def list_reservations() -> None:
    """List reservations with key fields."""
    reservations = Reservation.load_all()
    if not reservations:
        print("No hay reservaciones.")
        return
    for res in reservations:
        info = (
            f"- {res.id} | Hotel={res.hotel_id} | "
            f"Cliente={res.customer_id} | "
            f"Habitación={res.room_number} | "
            f"{res.check_in}→{res.check_out} | {res.status}"
        )
        print(info)


def create_hotel() -> None:
    """Create a hotel (simple input prompts)."""
    hotels = Hotel.load_all()
    hid = input("ID del hotel (ej. H010): ").strip()
    if find_hotel(hotels, hid):
        print("Error: ya existe un hotel con ese ID.")
        return
    name = input("Nombre: ").strip()
    city = input("Ciudad: ").strip()
    total = int(input("Habitaciones totales: ").strip())
    available = int(input("Habitaciones disponibles: ").strip())
    try:
        hotels.append(
            Hotel(
                id=hid,
                name=name,
                city=city,
                total_rooms=total,
                available_rooms=available,
            )
        )
        Hotel.save_all(hotels)
        print("Hotel creado.")
    except ValueError as exc:
        print(f"Error al crear hotel: {exc}")


def create_customer() -> None:
    """Create a customer."""
    customers = Customer.load_all()
    cid = input("ID del cliente (ej. C010): ").strip()
    if find_customer(customers, cid):
        print("Error: ya existe un cliente con ese ID.")
        return
    name = input("Nombre: ").strip()
    email = input("Email: ").strip()
    phone = input("Teléfono: ").strip()
    customers.append(
        Customer(id=cid, name=name, email=email, phone=phone)
    )
    Customer.save_all(customers)
    print("Cliente creado.")


def create_reservation() -> None:
    """Create a reservation (without availability logic)."""
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

    new_id = f"R{100 + len(reservations) + 1:03d}"
    try:
        res = Reservation(
            id=new_id,
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
    """Cancel a reservation by id."""
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
    """Corrupt hotels.json to demonstrate error handling."""
    path = os.path.join(DATA_DIR, "hotels.json")
    with open(path, "w", encoding="utf-8") as fhl:
        fhl.write("{ this is not valid json }")
    print(f"Se corrompió intencionalmente: {path}")


def menu() -> None:
    """Loop over console options for the demo."""
    options = {
        "1": ("Listar hoteles", list_hotels),
        "2": ("Listar clientes", list_customers),
        "3": ("Listar reservaciones", list_reservations),
        "4": ("Crear hotel", create_hotel),
        "5": ("Crear cliente", create_customer),
        "6": ("Crear reservación", create_reservation),
        "7": ("Cancelar reservación", cancel_reservation),
        "8": (
            "Corromper hotels.json (para evidencia de errores)",
            corrupt_hotels_file,
        ),
        "0": ("Salir", None),
    }
    while True:
        print("\n=== Sistema de Reservaciones (demo) ===")
        for key, (label, _) in options.items():
            print(f"{key}) {label}")
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
        except Exception as exc:  # pylint: disable=broad-exception-caught
            # Mantener ejecución siempre en la demo.
            # Se imprime el error y el menú continúa.
            print(f"Error inesperado: {exc}")


if __name__ == "__main__":
    menu()
