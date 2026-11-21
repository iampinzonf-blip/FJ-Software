
"""
CUSTOMERS MODULE - SOFTWARE FJ
Integrated Customer, Service, and Reservation Management System.
"""

from abc import ABC, abstractmethod
import logging
import re
from itertools import count
from typing import Optional


# =====================================================
# 1. LOGGING AND ERROR CONFIGURATION
# =====================================================

logging.basicConfig(
    filename="software_fj.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8"
)

logger = logging.getLogger("SoftwareFJ.Customers")


# =====================================================
# 2. CUSTOM EXCEPTIONS
# =====================================================

class CustomerError(Exception):
    """General error for the customers module."""


class InvalidCustomerData(CustomerError):
    """Raised when customer data is invalid."""


class CustomerNotFound(CustomerError):
    """Raised when a customer cannot be found."""


class DuplicateCustomer(CustomerError):
    """Raised when a customer is already registered."""


# =====================================================
# 3. ABSTRACT ENTITY CLASS
# =====================================================

class Entity(ABC):

    def __init__(self, identifier):
        self._identifier = identifier

    @property
    def identifier(self):
        return self._identifier

    @abstractmethod
    def validate(self):
        pass


# =====================================================
# 4. CUSTOMER CLASS
# =====================================================

class Customer(Entity):
    _id_sequence = count(1)

    def __init__(
        self,
        name,
        identity_number,
        email,
        phone_number,
        address=""
    ):

        super().__init__(next(self._id_sequence))

        self._name = name
        self._identity_number = identity_number
        self._email = email
        self._phone_number = phone_number
        self._address = address

        self.validate()

    # PROPERTIES FOR ACCESSING ATTRIBUTES

    @property
    def name(self):
        return self._name

    @property
    def identity_number(self):
        return self._identity_number

    @property
    def email(self):
        return self._email

    @property
    def phone_number(self):
        return self._phone_number

    @property
    def address(self):
        return self._address

    # VALIDATION

    def validate(self):

        if not isinstance(self._name, str) or not self._name.strip():
            raise InvalidCustomerData(
                "Name is required."
            )

        name = self._name.strip()

        if len(name) < 2 or not all(
            c.isalpha() or c.isspace() or c in "-'áéíóúÁÉÍÓÚñÑ"
            for c in name
        ):
            raise InvalidCustomerData(
                "Name must contain letters and have at least 2 characters."
            )

        if not isinstance(self._identity_number, str) or not self._identity_number.strip():
            raise InvalidCustomerData(
                "Identity number is required."
            )

        identity_number = self._identity_number.strip()

        if not identity_number.isalnum() or not (5 <= len(identity_number) <= 20):
            raise InvalidCustomerData(
                "Identity number must contain 5 to 20 alphanumeric characters."
            )

        if not isinstance(self._email, str) or not re.fullmatch(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            self._email.strip()
        ):
            raise InvalidCustomerData(
                "Email address is invalid."
            )

        if not isinstance(self._phone_number, str):
            raise InvalidCustomerData(
                "Phone number must be provided as text."
            )

        digits = re.sub(r"\D", "", self._phone_number)

        if not (7 <= len(digits) <= 15):
            raise InvalidCustomerData(
                "Phone number must contain 7 to 15 digits."
            )

        if not isinstance(self._address, str):
            raise InvalidCustomerData(
                "Address must be text."
            )

    # CUSTOMER DESCRIPTION

    def description(self):

        return (
            f"ID: {self.identifier:02d}\n"
            f"Name: {self.name}\n"
            f"Identity: {self.identity_number}\n"
            f"Email: {self.email}\n"
            f"Phone: {self.phone_number}\n"
            f"Address: {self.address}"
        )

    # UPDATE DATA

    def update_data(
        self,
        name=None,
        identity_number=None,
        email=None,
        phone_number=None,
        address=None
    ):

        previous_data = (
            self._name,
            self._identity_number,
            self._email,
            self._phone_number,
            self._address
        )

        try:

            if name is not None:
                self._name = name

            if identity_number is not None:
                self._identity_number = identity_number

            if email is not None:
                self._email = email

            if phone_number is not None:
                self._phone_number = phone_number

            if address is not None:
                self._address = address

            self.validate()

        except Exception:

            (
                self._name,
                self._identity_number,
                self._email,
                self._phone_number,
                self._address
            ) = previous_data

            raise

    def __str__(self):
        return self.description()


# =====================================================
# 5. CUSTOMER MANAGER
# =====================================================

class CustomerManager:

    def __init__(self):
        self._customers = []

    # FIND BY ID

    def _find_by_id(self, identifier):
        if isinstance(identifier, str) and identifier.strip().isdecimal():
            identifier = int(identifier.strip())

        for customer in self._customers:

            if customer.identifier == identifier:
                return customer

        raise CustomerNotFound(
            f"No customer exists with ID: {identifier}"
        )

    # REGISTER CUSTOMER

    def register_customer(
        self,
        name,
        identity_number,
        email,
        phone_number,
        address=""
    ):

        try:

            new_customer = Customer(
                name,
                identity_number,
                email,
                phone_number,
                address
            )

            for customer in self._customers:

                if customer.identity_number.lower() == new_customer.identity_number.lower():
                    raise DuplicateCustomer(
                        "A customer with that identity number already exists."
                    )

                if customer.email.lower() == new_customer.email.lower():
                    raise DuplicateCustomer(
                        "A customer with that email already exists."
                    )

            self._customers.append(new_customer)

            logger.info(
                "Customer registered: %02d",
                new_customer.identifier
            )

            return new_customer

        except CustomerError as error:

            logger.warning(
                "Error registering customer: %s",
                error
            )

            raise

        except Exception as error:

            logger.exception(
                "Unexpected error while registering customer."
            )

            raise CustomerError(
                "An error occurred while registering the customer."
            ) from error

    # LIST CUSTOMERS

    def list_customers(self):

        return list(self._customers)

    # GET CUSTOMER BY ID

    def get_customer_by_id(self, identifier):

        try:

            return self._find_by_id(identifier)

        except CustomerNotFound as error:

            logger.warning(
                "Lookup failed: %s",
                error
            )

            raise

    # FIND BY IDENTITY NUMBER

    def find_by_identity_number(self, identity_number):

        for customer in self._customers:

            if customer.identity_number.lower() == str(identity_number).strip().lower():
                return customer

        return None

    # FIND BY EMAIL

    def find_by_email(self, email):

        for customer in self._customers:

            if customer.email.lower() == str(email).strip().lower():
                return customer

        return None

    # FIND BY NAME

    def find_by_name(self, name):

        if not isinstance(name, str) or not name.strip():
            raise InvalidCustomerData(
                "Provide a valid name to search for."
            )

        query = name.strip().casefold()

        return [
            customer for customer in self._customers
            if query in customer.name.casefold()
        ]

    # UPDATE CUSTOMER

    def update_customer(self, identifier, **new_data):

        allowed_fields = {
            "name",
            "identity_number",
            "email",
            "phone_number",
            "address"
        }

        try:

            customer = self._find_by_id(identifier)

            unknown_fields = set(new_data) - allowed_fields

            if unknown_fields:
                raise InvalidCustomerData(
                    "Fields not allowed: " +
                    ", ".join(sorted(unknown_fields))
                )

            new_identity_number = new_data.get(
                "identity_number",
                customer.identity_number
            )

            new_email = new_data.get(
                "email",
                customer.email
            )

            for other in self._customers:

                if other.identifier != identifier:

                    if other.identity_number.lower() == str(new_identity_number).lower():
                        raise DuplicateCustomer(
                            "The identity number already belongs to another customer."
                        )

                    if other.email.lower() == str(new_email).lower():
                        raise DuplicateCustomer(
                            "The email already belongs to another customer."
                        )

            customer.update_data(**new_data)

            logger.info(
                "Customer updated: %s",
                identifier
            )

            return customer

        except CustomerError as error:

            logger.warning(
                "Error updating customer: %s",
                error
            )

            raise

        except Exception as error:

            logger.exception(
                "Unexpected error while updating customer."
            )

            raise CustomerError(
                "An error occurred while updating the customer."
            ) from error

    # DELETE CUSTOMER

    def delete_customer(self, identifier):

        try:

            customer = self._find_by_id(identifier)

            self._customers.remove(customer)

            logger.info(
                "Customer deleted: %s",
                identifier
            )

            return True

        except CustomerNotFound as error:

            logger.warning(
                "Error deleting customer: %s",
                error
            )

            raise

        except Exception as error:

            logger.exception(
                "Unexpected error while deleting customer."
            )

            raise CustomerError(
                "An error occurred while deleting the customer."
            ) from error


# =====================================================
# 6. CUSTOMER MODULE TESTS
# =====================================================

if __name__ == "__main__":

    manager = CustomerManager()

    print("\n===== SOFTWARE FJ SYSTEM =====")
    print("CUSTOMER MANAGEMENT MODULE")

    try:

        # REGISTER

        customer = manager.register_customer(
            name="Laura Gomez",
            identity_number="1020304050",
            email="laura@gmail.com",
            phone_number="3001234567",
            address="Sogamoso"
        )

        print("\nCUSTOMER REGISTERED:")
        print(customer)

        # LIST

        print("\nCUSTOMER LIST:")

        for registered_customer in manager.list_customers():
            print(registered_customer)

        # GET

        print("\nGET CUSTOMER:")

        found_customer = manager.get_customer_by_id(
            customer.identifier
        )

        print(found_customer)

        # UPDATE

        print("\nUPDATE CUSTOMER:")

        updated_customer = manager.update_customer(
            customer.identifier,
            phone_number="3117654321"
        )

        print(updated_customer)

        # FIND BY IDENTITY NUMBER

        print("\nFIND BY IDENTITY NUMBER:")

        result = manager.find_by_identity_number("1020304050")

        if result:
            print(result)
        else:
            print("Customer not found.")

        # DELETE

        print("\nDELETE CUSTOMER:")

        deleted = manager.delete_customer(
            customer.identifier
        )

        print("Customer deleted:", deleted)

    except CustomerError as error:

        print("Handled error:", error)

    # VALIDATION TEST

    print("\nINVALID DATA TEST:")

    try:

        manager.register_customer(
            name="",
            identity_number="123",
            email="invalid-email",
            phone_number="123",
            address=""
        )

    except CustomerError as error:

        print("Validation successful:", error)

    print("\nPROCESS FINISHED.")
    print("Check the software_fj.log file.")
