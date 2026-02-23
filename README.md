# A01796793 – Actividad 6.2
## Reservation System (Python)

Este proyecto implementa un **sistema de reservaciones** que cumple con todos los requisitos de la Actividad 6.2: clases en Python, manejo de archivos, pruebas unitarias, cobertura, PEP8, Flake8 y Pylint.

---

# ✅ Requerimientos cumplidos

## **Req 1 – Clases**
Se implementan en `src/models.py`:

- `Hotel`
- `Customer`
- `Reservation`

Cada clase incluye validaciones y métodos de carga/guardado en archivos JSON.

---

## **Req 2 – Funcionalidad con persistencia**

### 🏨 Hoteles
- Crear hotel → `create_hotel()`
- Eliminar hotel → `delete_hotel()`
- Mostrar información → `show_hotel()`
- Modificar información → `update_hotel()`
- Reservar habitación → `create_reservation()`
- Cancelar reservación → `cancel_reservation()` *(ajusta disponibilidad)*

### 👤 Clientes
- Crear cliente → `create_customer()`
- Eliminar cliente → `delete_customer()`
- Mostrar información → `show_customer()`
- Modificar información → `update_customer()`

### 📅 Reservaciones
- Crear reservación → `create_reservation()`
- Cancelar reservación → `cancel_reservation()`

Toda la lógica está implementada en `src/main.py` usando persistencia en JSON.

---

## **Req 3 – Pruebas unitarias**

En la carpeta `tests/` se incluyen:

- `test_models.py` (pruebas generales)
- `test_negative_cases.py` (más de 5 casos negativos)

Ejecutar con:

```bash
python -m unittest discover -s tests