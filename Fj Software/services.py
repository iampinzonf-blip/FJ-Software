
"""
SERVICES MODULE - SOFTWARE FJ
Integrated Customer, Service, and Reservation Management System.
"""

from abc import abstractmethod
import logging
from itertools import count

from customers import Entity


logger = logging.getLogger("SoftwareFJ.Services")


# CUSTOM EXCEPTIONS

class ServiceError(Exception):
    """General error for the services module."""


class InvalidServiceData(ServiceError):
    """Raised when service data is invalid."""


class ServiceNotFound(ServiceError):
    """Raised when a service cannot be found."""


class ServiceUnavailable(ServiceError):
    """Raised when a service is unavailable."""


class DuplicateService(ServiceError):
    """Raised when attempting to register a duplicate service."""


# ABSTRACT SERVICE CLASS

class Service(Entity):
    _id_sequence = count(1)

    # Base class inherited by the three service types.

    def __init__(self, name, description, base_rate, available=True):
        super().__init__(next(self._id_sequence))

        self._name = name
        self._description = description
        self._base_rate = base_rate
        self._available = available

        self.validate()

    # Properties for accessing the encapsulated attributes.

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def base_rate(self):
        return self._base_rate

    @property
    def available(self):
        return self._available

    def validate(self):
        # Validates the general service data.

        if not isinstance(self._name, str) or not self._name.strip():
            raise InvalidServiceData(
                "Service name is invalid."
            )

        if not isinstance(self._description, str) or not self._description.strip():
            raise InvalidServiceData(
                "Service description is invalid."
            )

        if (
            not isinstance(self._base_rate, (int, float))
            or isinstance(self._base_rate, bool)
            or self._base_rate <= 0
        ):
            raise InvalidServiceData(
                "The rate must be a number greater than zero."
            )

        if not isinstance(self._available, bool):
            raise InvalidServiceData(
                "Availability must be true or false."
            )

    # These methods must be implemented by each specialized service.

    @abstractmethod
    def calculate_cost(self, quantity=1, discount=0, tax=0):
        pass

    @abstractmethod
    def describe_service(self):
        pass

    @abstractmethod
    def validate_parameters(self):
        pass


# ROOM SERVICE

class RoomService(Service):

    def __init__(
        self,
        name,
        description,
        base_rate,
        capacity,
        location,
        available=True
    ):
        super().__init__(name, description, base_rate, available)

        self._capacity = capacity
        self._location = location

        self.validate_parameters()

    @property
    def capacity(self):
        return self._capacity

    @property
    def location(self):
        return self._location

    def validate_parameters(self):
        # Validates the room capacity and location.

        if (
            not isinstance(self._capacity, int)
            or isinstance(self._capacity, bool)
            or self._capacity <= 0
        ):
            raise InvalidServiceData(
                "Capacity must be an integer greater than zero."
            )

        if not isinstance(self._location, str) or not self._location.strip():
            raise InvalidServiceData(
                "Room location is invalid."
            )

    def calculate_cost(self, quantity=1, discount=0, tax=0):
        # Calculates the price based on hours, discount, and tax.

        if (
            not isinstance(quantity, (int, float))
            or isinstance(quantity, bool)
            or quantity <= 0
        ):
            raise InvalidServiceData(
                "The number of hours must be greater than zero."
            )

        if (
            not isinstance(discount, (int, float))
            or isinstance(discount, bool)
            or not 0 <= discount <= 100
        ):
            raise InvalidServiceData(
                "Discount must be between 0 and 100."
            )

        if (
            not isinstance(tax, (int, float))
            or isinstance(tax, bool)
            or not 0 <= tax <= 100
        ):
            raise InvalidServiceData(
                "Tax must be between 0 and 100."
            )

        subtotal = self._base_rate * quantity
        total = subtotal - (subtotal * discount / 100)
        total = total + (total * tax / 100)

        return round(total, 2)

    def describe_service(self):
        # Returns the full room information.

        return (
            f"Service: {self._name}\n"
            f"Description: {self._description}\n"
            f"Hourly rate: ${self._base_rate}\n"
            f"Capacity: {self._capacity} people\n"
            f"Location: {self._location}\n"
            f"Available: {self._available}"
        )


# EQUIPMENT RENTAL SERVICE

class EquipmentRentalService(Service):

    def __init__(
        self,
        name,
        description,
        base_rate,
        equipment_type,
        brand,
        available_quantity,
        available=True
    ):
        super().__init__(name, description, base_rate, available)

        self._equipment_type = equipment_type
        self._brand = brand
        self._available_quantity = available_quantity

        self.validate_parameters()

    @property
    def equipment_type(self):
        return self._equipment_type

    @property
    def brand(self):
        return self._brand

    @property
    def available_quantity(self):
        return self._available_quantity

    def validate_parameters(self):
        # Validates the equipment data.

        if (
            not isinstance(self._equipment_type, str)
            or not self._equipment_type.strip()
        ):
            raise InvalidServiceData(
                "Equipment type is invalid."
            )

        if not isinstance(self._brand, str) or not self._brand.strip():
            raise InvalidServiceData(
                "Equipment brand is invalid."
            )

        if (
            not isinstance(self._available_quantity, int)
            or isinstance(self._available_quantity, bool)
            or self._available_quantity < 0
        ):
            raise InvalidServiceData(
                "Available quantity must be an integer greater than or equal to zero."
            )

    def calculate_cost(self, quantity=1, discount=0, tax=0):
        # Calculates the rental cost based on the number of days.

        if (
            not isinstance(quantity, (int, float))
            or isinstance(quantity, bool)
            or quantity <= 0
        ):
            raise InvalidServiceData(
                "The number of days must be greater than zero."
            )

        if (
            not isinstance(discount, (int, float))
            or isinstance(discount, bool)
            or not 0 <= discount <= 100
        ):
            raise InvalidServiceData(
                "Discount must be between 0 and 100."
            )

        if (
            not isinstance(tax, (int, float))
            or isinstance(tax, bool)
            or not 0 <= tax <= 100
        ):
            raise InvalidServiceData(
                "Tax must be between 0 and 100."
            )

        subtotal = self._base_rate * quantity
        total = subtotal - (subtotal * discount / 100)
        total = total + (total * tax / 100)

        return round(total, 2)

    def describe_service(self):
        # Returns information about the equipment available for rent.

        return (
            f"Service: {self._name}\n"
            f"Description: {self._description}\n"
            f"Daily rate: ${self._base_rate}\n"
            f"Equipment type: {self._equipment_type}\n"
            f"Brand: {self._brand}\n"
            f"Available quantity: {self._available_quantity}\n"
            f"Available: {self._available}"
        )


# ADVISORY SERVICE

class AdvisoryService(Service):

    def __init__(
        self,
        name,
        description,
        base_rate,
        area,
        advisor,
        session_duration,
        available=True
    ):
        super().__init__(name, description, base_rate, available)

        self._area = area
        self._advisor = advisor
        self._session_duration = session_duration

        self.validate_parameters()

    @property
    def area(self):
        return self._area

    @property
    def advisor(self):
        return self._advisor

    @property
    def session_duration(self):
        return self._session_duration

    def validate_parameters(self):
        # Validates the advisory area, advisor, and session duration.

        if not isinstance(self._area, str) or not self._area.strip():
            raise InvalidServiceData(
                "Advisory area is invalid."
            )

        if not isinstance(self._advisor, str) or not self._advisor.strip():
            raise InvalidServiceData(
                "Advisor name is invalid."
            )

        if (
            not isinstance(self._session_duration, (int, float))
            or isinstance(self._session_duration, bool)
            or self._session_duration <= 0
        ):
            raise InvalidServiceData(
                "Session duration must be greater than zero."
            )

    def calculate_cost(self, quantity=1, discount=0, tax=0):
        # Calculates the cost based on the number of sessions.

        if (
            not isinstance(quantity, (int, float))
            or isinstance(quantity, bool)
            or quantity <= 0
        ):
            raise InvalidServiceData(
                "The number of sessions must be greater than zero."
            )

        if (
            not isinstance(discount, (int, float))
            or isinstance(discount, bool)
            or not 0 <= discount <= 100
        ):
            raise InvalidServiceData(
                "Discount must be between 0 and 100."
            )

        if (
            not isinstance(tax, (int, float))
            or isinstance(tax, bool)
            or not 0 <= tax <= 100
        ):
            raise InvalidServiceData(
                "Tax must be between 0 and 100."
            )

        subtotal = self._base_rate * quantity
        total = subtotal - (subtotal * discount / 100)
        total = total + (total * tax / 100)

        return round(total, 2)

    def describe_service(self):
        # Returns the advisory information.

        return (
            f"Service: {self._name}\n"
            f"Description: {self._description}\n"
            f"Rate per session: ${self._base_rate}\n"
            f"Area: {self._area}\n"
            f"Advisor: {self._advisor}\n"
            f"Session duration: {self._session_duration} hours\n"
            f"Available: {self._available}"
        )


# SERVICE MANAGER

class ServiceManager:

    def __init__(self):
        self._services = []

    def register_service(self, service):
        # Validates the object and prevents duplicates.

        if not isinstance(service, Service):
            raise InvalidServiceData(
                "The object being registered is not a valid service."
            )

        service.validate()
        service.validate_parameters()

        for existing in self._services:
            if (
                type(existing) == type(service)
                and existing.name.casefold() == service.name.casefold()
            ):
                raise DuplicateService(
                    "A service of this type with that name already exists."
                )

        self._services.append(service)

        logger.info(
            "Service registered: %s | ID: %02d",
            service.name,
            service.identifier
        )

        return service

    def list_services(self):
        # Returns a copy of the list to protect the internal list.
        return list(self._services)

    def get_service_by_id(self, identifier):
        # Finds a service by its unique identifier.
        if isinstance(identifier, str) and identifier.strip().isdecimal():
            identifier = int(identifier.strip())

        for service in self._services:
            if service.identifier == identifier:
                return service

        raise ServiceNotFound(
            f"Service with ID {identifier} was not found."
        )

    def find_by_name(self, name):
        # Finds partial matches in service names.

        if not isinstance(name, str) or not name.strip():
            raise InvalidServiceData(
                "Provide a valid name to search for."
            )

        results = [
            service for service in self._services
            if name.casefold() in service.name.casefold()
        ]

        return results

    def delete_service(self, identifier):
        # Retrieves and deletes the service.

        service = self.get_service_by_id(identifier)

        self._services.remove(service)

        logger.info(
            "Service deleted: %s | ID: %02d",
            service.name,
            service.identifier
        )

        return service


# MODULE TESTS

if __name__ == "__main__":
    # This block only runs when the file is executed directly.

    manager = ServiceManager()

    try:
        room = RoomService(
            "Main room",
            "Meeting room",
            50000,
            20,
            "Second floor"
        )

        equipment = EquipmentRentalService(
            "Laptop rental",
            "Office equipment",
            40000,
            "Computer",
            "HP",
            5
        )

        advisory = AdvisoryService(
            "IT advisory",
            "IT guidance",
            80000,
            "IT",
            "Carlos Perez",
            2
        )

        manager.register_service(room)
        manager.register_service(equipment)
        manager.register_service(advisory)

        print("\nREGISTERED SERVICES")
        print("--------------------")

        for service in manager.list_services():
            print(service.describe_service())

            print(
                "Sample cost:",
                service.calculate_cost(2, 10, 19)
            )

            print("--------------------")

    except ServiceError as error:
        # Catches custom errors and logs them.

        logger.exception("Error during service tests.")
        print("Error:", error)
