import math
from datetime import datetime
from itertools import count

from customers import Customer, CustomerNotFound, CustomerManager
from services import (
    ServiceManager,
    Service,
    ServiceUnavailable,
    ServiceNotFound,
)


class ReservationError(Exception):
    """General error for the reservations module."""


class InvalidReservationData(ReservationError):
    """Raised when reservation data is invalid."""


class ReservationNotFound(ReservationError):
    """Raised when a reservation cannot be found."""


class DuplicateReservation(ReservationError):
    """Raised when a reservation with the same ID already exists."""


class CustomerNotRegistered(ReservationError):
    """Raised when a reservation customer is not registered."""


class ServiceNotRegistered(ReservationError):
    """Raised when a reservation service is not registered."""


class Reservation:
    VALID_STATUSES = {"Pending", "Confirmed", "Canceled"}
    _id_sequence = count(1)

    def __init__(self, customer, service, duration, reservation_date):
        self.id = next(self._id_sequence)
        self.customer = customer
        self.service = service
        self.duration = duration
        self.date = reservation_date
        self.status = "Pending"
        self.total_cost = 0
        self.validate()

    def validate(self):
        if (
            not isinstance(self.id, int)
            or isinstance(self.id, bool)
            or self.id <= 0
        ):
            raise InvalidReservationData(
                "Reservation ID must be a positive integer."
            )

        if not isinstance(self.customer, Customer):
            raise InvalidReservationData(
                "Customer must be a registered Customer object."
            )

        if not isinstance(self.service, Service):
            raise InvalidReservationData(
                "Service must be a registered Service object."
            )

        if (
            not isinstance(self.duration, (int, float))
            or isinstance(self.duration, bool)
            or self.duration <= 0
            or (
                isinstance(self.duration, float)
                and not math.isfinite(self.duration)
            )
        ):
            raise InvalidReservationData(
                "Duration must be a number greater than zero."
            )

        if not isinstance(self.date, datetime):
            raise InvalidReservationData(
                "Reservation date must include a valid date and time."
            )

        if (
            not isinstance(self.status, str)
            or self.status not in self.VALID_STATUSES
        ):
            raise InvalidReservationData("Reservation status is invalid.")

        if (
            not isinstance(self.total_cost, (int, float))
            or isinstance(self.total_cost, bool)
            or self.total_cost < 0
            or (
                isinstance(self.total_cost, float)
                and not math.isfinite(self.total_cost)
            )
        ):
            raise InvalidReservationData(
                "Total cost must be a number greater than or equal to zero."
            )

    def display_info(self):
        return (
            f"Reservation [{self.id:02d}] | Customer: {self.customer.name} | "
            f"Service: {self.service.name} | Status: {self.status} | "
            f"Date: {self.date:%Y-%m-%d %H:%M} | Cost: ${self.total_cost}"
        )

    def confirm(self):
        self.status = "Confirmed"
        return f"Reservation {self.id:02d} confirmed for {self.customer.name}"

    def cancel(self):
        self.status = "Canceled"
        return f"Reservation {self.id:02d} canceled for {self.customer.name}"

    def calculate_cost(self):
        total_cost = self.service.calculate_cost(self.duration)
        if (
            not isinstance(total_cost, (int, float))
            or isinstance(total_cost, bool)
            or total_cost < 0
            or (
                isinstance(total_cost, float)
                and not math.isfinite(total_cost)
            )
        ):
            raise InvalidReservationData(
                "The service returned an invalid total cost."
            )

        self.total_cost = total_cost
        return f"Total cost: ${self.total_cost:g}"


class ReservationManager:
    def __init__(self, customer_manager, service_manager):
        if not isinstance(customer_manager, CustomerManager):
            raise InvalidReservationData(
                "Provide a valid CustomerManager."
            )
        if not isinstance(service_manager, ServiceManager):
            raise InvalidReservationData(
                "Provide a valid ServiceManager."
            )

        self._customer_manager = customer_manager
        self._service_manager = service_manager
        self._reservations = []

    def register_reservation(self, reservation):
        if not isinstance(reservation, Reservation):
            raise InvalidReservationData(
                "The object being registered is not a valid reservation."
            )

        reservation.validate()

        try:
            registered_customer = self._customer_manager.get_customer_by_id(
                reservation.customer.identifier
            )
        except CustomerNotFound as error:
            raise CustomerNotRegistered(
                "Cannot register a reservation for a customer that does not exist."
            ) from error

        if registered_customer is not reservation.customer:
            raise CustomerNotRegistered(
                "Reservation must use the Customer object registered with the manager."
            )

        try:
            registered_service = self._service_manager.get_service_by_id(
                reservation.service.identifier
            )
        except ServiceNotFound as error:
            raise ServiceNotRegistered(
                "Cannot register a reservation for a service that does not exist."
            ) from error

        if registered_service is not reservation.service:
            raise ServiceNotRegistered(
                "Reservation must use the Service object registered with the manager."
            )

        if not reservation.service.available:
            raise ServiceUnavailable(
                f"Service '{reservation.service.name}' is unavailable."
            )

        if any(existing.id == reservation.id for existing in self._reservations):
            raise DuplicateReservation(
                f"A reservation with ID {reservation.id} already exists."
            )

        self._reservations.append(reservation)
        return reservation

    def list_reservations(self):
        return list(self._reservations)

    def get_by_id(self, reservation_id):
        if isinstance(reservation_id, str) and reservation_id.strip().isdecimal():
            reservation_id = int(reservation_id.strip())

        if (
            not isinstance(reservation_id, int)
            or isinstance(reservation_id, bool)
            or reservation_id <= 0
        ):
            raise InvalidReservationData(
                "Search ID must be a positive integer."
            )

        for reservation in self._reservations:
            if reservation.id == reservation_id:
                return reservation

        raise ReservationNotFound(
            f"No reservation was found with ID {reservation_id}."
        )

if __name__ == "__main__":
    from services import RoomService

    customer_manager = CustomerManager()
    customer = customer_manager.register_customer(
        name="Ana Perez",
        identity_number="1001001001",
        email="ana@example.com",
        phone_number="3001234567",
    )
    service_manager = ServiceManager()
    service = service_manager.register_service(
        RoomService(
            "Room A",
            "Meeting room",
            50000,
            20,
            "Second floor",
        )
    )
    manager = ReservationManager(customer_manager, service_manager)
    reservation = Reservation(
        customer,
        service,
        2,
        datetime(2026, 12, 1, 10, 0),
    )
    manager.register_reservation(reservation)

    print(reservation.display_info())
    print(reservation.confirm())
    print(reservation.calculate_cost())
    print(reservation.display_info())
    print(reservation.cancel())
    print(reservation.display_info())
