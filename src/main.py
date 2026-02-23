"""Console menu for demo and recording evidence.

Provides minimal operations to list, create, update, delete entities, and
demonstrate error handling with corrupted JSON files. Also adjusts hotel
availability when creating and cancelling reservations to meet Req 2.
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
        info = f"- {cust.id} | {cust.name} | {cust.email} | {cust.phone}"
        print(info)


def list_reservations() -> None:
    """List reservations with key fields."""
    reservations = Reservation.load_all()
    if not reservations:
        print("No hay reservaciones.")
        return
    for res in reservations:
        info = (
            f"- {res.id} | Hotel={res.hotel_id} | Cliente={res.customer_id} | "
            f"Habitación={res.room_number} | {res.check_in}->{res.check_out} "
            f"| {res.status}"
        )
        print(info)


# ---------------------- Show single entity (Display) ---------------------- #

def show_hotel() -> None:
    """Display information for a single hotel."""
    hotels = Hotel.load_all()
    hid = input("ID del hotel: ").strip()
    htl = find_hotel(hotels, hid)
    if not htl:
        print("No existe ese hotel.")
        return
    print("Hotel:")
    print(f"  ID: {htl.id}")
    print(f"  Nombre: {htl.name}")
    print(f"  Ciudad: {htl.city}")
    print(f"  Habitaciones: {htl.total_rooms}")
    print(f"  Disponibles: {htl.available_rooms}")


def show_customer() -> None:
    """Display information for a single customer."""
    customers = Customer.load_all()
    cid = input("ID del cliente: ").strip()
    cust = find_customer(customers, cid)
    if not cust:
        print("No existe ese cliente.")
        return
    print("Cliente:")
    print(f"  ID: {cust.id}")
    print(f"  Nombre: {cust.name}")
    print(f"  Email: {cust.email}")
    print(f"  Teléfono: {cust.phone}")


# ----------------------------- Create entities --------------------------- #

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
    customers.append(Customer(id=cid, name=name, email=email, phone=phone))
    Customer.save_all(customers)
    print("Cliente creado.")


def create_reservation() -> None:
    """Create a reservation with availability validation."""
    hotels = Hotel.load_all()
    customers = Customer.load_all()
    reservations = Reservation.load_all()

    hotel_id = input("Hotel ID: ").strip()
    customer_id = input("Customer ID: ").strip()
    room = int(input("Número de habitación: ").strip())
    check_in = input("Check-in (YYYY-MM-DD): ").strip()
    check_out = input("Check-out (YYYY-MM-DD): ").strip()

    htl = find_hotel(hotels, hotel_id)
    if not htl:
        print("Error: hotel no existe.")
        return
    if not find_customer(customers, customer_id):
        print("Error: cliente no existe.")
        return
    if htl.available_rooms <= 0:
        print("Error: hotel sin disponibilidad.")
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
        # Ajustar disponibilidad del hotel
        htl.available_rooms -= 1
        Hotel.save_all(hotels)
        print(f"Reserva creada con ID: {res.id}")
    except ValueError as exc:
        print(f"Error al crear reserva: {exc}")


# ----------------------------- Update entities --------------------------- #

def update_hotel() -> None:
    """Modify hotel fields; adjusts availability if total changes."""
    hotels = Hotel.load_all()
    hid = input("ID del hotel: ").strip()
    htl = find_hotel(hotels, hid)
    if not htl:
        print("No existe ese hotel.")
        return

    name = input(f"Nombre [{htl.name}]: ").strip()
    city = input(f"Ciudad [{htl.city}]: ").strip()
    total_s = input(f"Habitaciones totales [{htl.total_rooms}]: ").strip()

    if name:
        htl.name = name
    if city:
        htl.city = city
    if total_s:
        try:
            new_total = int(total_s)
            occupied = htl.total_rooms - htl.available_rooms
            if new_total < occupied:
                print(
                    "Error: el nuevo total no puede ser menor a ocupadas "
                    f"({occupied})."
                )
                return
            htl.total_rooms = new_total
            htl.available_rooms = new_total - occupied
        except ValueError:
            print("Total inválido (debe ser entero).")
            return

    Hotel.save_all(hotels)
    print("Hotel actualizado.")


def update_customer() -> None:
    """Modify customer fields."""
    customers = Customer.load_all()
    cid = input("ID del cliente: ").strip()
    cust = find_customer(customers, cid)
    if not cust:
        print("No existe ese cliente.")
        return

    name = input(f"Nombre [{cust.name}]: ").strip()
    email = input(f"Email [{cust.email}]: ").strip()
    phone = input(f"Teléfono [{cust.phone}]: ").strip()

    if name:
        cust.name = name
    if email:
        cust.email = email
    if phone:
        cust.phone = phone

    Customer.save_all(customers)
    print("Cliente actualizado.")


# ----------------------------- Delete entities --------------------------- #

def delete_hotel() -> None:
    """Delete a hotel if it has no ACTIVE reservations."""
    hotels = Hotel.load_all()
    reservations = Reservation.load_all()
    hid = input("ID del hotel: ").strip()
    htl = find_hotel(hotels, hid)
    if not htl:
        print("No existe ese hotel.")
        return

    active = [
        r for r in reservations
        if r.hotel_id == hid and r.status == "ACTIVE"
    ]
    if active:
        print(
            "No se puede eliminar: hay reservaciones ACTIVAS para este hotel."
        )
        return

    hotels = [h for h in hotels if h.id != hid]
    Hotel.save_all(hotels)
    print("Hotel eliminado.")


def delete_customer() -> None:
    """Delete a customer if it has no ACTIVE reservations."""
    customers = Customer.load_all()
    reservations = Reservation.load_all()
    cid = input("ID del cliente: ").strip()
    cust = find_customer(customers, cid)
    if not cust:
        print("No existe ese cliente.")
        return

    active = [
        r for r in reservations
        if r.customer_id == cid and r.status == "ACTIVE"
    ]
    if active:
        print(
            "No se puede eliminar: hay reservaciones ACTIVAS de este cliente."
        )
        return

    customers = [c for c in customers if c.id != cid]
    Customer.save_all(customers)
    print("Cliente eliminado.")


# --------------------------- Cancel reservation --------------------------- #

def cancel_reservation() -> None:
    """Cancel a reservation and restore hotel availability."""
    reservations = Reservation.load_all()
    hotels = Hotel.load_all()

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

    # Ajustar disponibilidad del hotel
    htl = find_hotel(hotels, res.hotel_id)
    if htl:
        if htl.available_rooms < htl.total_rooms:
            htl.available_rooms += 1
            Hotel.save_all(hotels)
        else:
            print("Aviso: disponibilidad ya estaba al máximo.")
    else:
        print("Aviso: hotel de la reserva no existe. No se ajustó stock.")

    print("Reserva cancelada.")


# ------------------------------ Evidence helper --------------------------- #

def corrupt_hotels_file() -> None:
    """Corrupt hotels.json to demonstrate error handling."""
    path = os.path.join(DATA_DIR, "hotels.json")
    with open(path, "w", encoding="utf-8") as fhl:
        fhl.write("{ this is not valid json }")
    print(f"Se corrompió intencionalmente: {path}")


# --------------------------------- Menu loop ------------------------------ #

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
        "8": ("Mostrar hotel (por ID)", show_hotel),
        "9": ("Mostrar cliente (por ID)", show_customer),
        "10": ("Modificar hotel", update_hotel),
        "11": ("Modificar cliente", update_customer),
        "12": ("Eliminar hotel", delete_hotel),
        "13": ("Eliminar cliente", delete_customer),
        "14": (
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
