import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import math
from datetime import datetime, timedelta
from pathlib import Path

from customers import CustomerError, CustomerManager, CustomerNotFound
from reservations import (
    Reservation,
    ReservationError,
    ReservationManager,
    ReservationNotFound,
)
from services import (
    AdvisoryService,
    EquipmentRentalService,
    RoomService,
    ServiceError,
    ServiceManager,
    ServiceNotFound,
)

PROJECT_ROOT = Path(__file__).resolve().parent


def asset_path(relative_path):
    asset_relative_path = relative_path.replace("Fj Software/Interfaz/", "Interfaz/")
    return str(PROJECT_ROOT / Path(asset_relative_path))


# --- Constants ---

USER_CREDENTIALS = {
    "Michelle": "213023A",
    "Edwin": "213023A",
    "Sebastian": "213023A",
    "Federico": "213023A",
    "Juan Pablo": "213023A",
}


# --- Application state ---

customer_manager = CustomerManager()
service_manager = ServiceManager()
reservation_manager = ReservationManager(customer_manager, service_manager)
test_data_loaded = False
customer_search_type = "id"
service_search_type = "id"


# --- Functions ---

# --- Login ---

def sign_in():
    username = e_user.get().strip()
    password = e_password.get()

    if USER_CREDENTIALS.get(username) == password:
        w_login.withdraw()
        w_main.deiconify()
        w_main.lift()
        w_main.focus_set()
    else:
        messagebox.showerror(
            "Login Failed",
            "Incorrect username or password.",
            parent=w_login,
        )


# --- Customers ---

def show_customer_search():
    w_customer_search.deiconify()
    w_customer_search.lift()
    w_customer_search.focus_set()


def select_customer_search_type(search_type):
    global customer_search_type

    labels = {
        "id": "Introduce the customer ID",
        "identity": "Introduce the customer's CC",
        "email": "Introduce the customer's email",
        "name": "Introduce the customer's name",
    }
    customer_search_type = search_type
    l_costumer_search_label.config(text=labels[search_type])
    e_costumer_search.delete(0, tk.END)
    e_costumer_search.focus_set()
    tv_costumers.yview_moveto(0)


def update_customer_tree(customers):
    for item in tv_costumers.get_children():
        tv_costumers.delete(item)

    for customer in customers:
        tv_costumers.insert(
            "",
            "end",
            values=(
                f"{customer.identifier:02d}",
                customer.name,
                customer.identity_number,
                customer.email,
                customer.phone_number,
                customer.address,
            ),
        )

    tv_costumers.yview_moveto(0)


def search_customers():
    tv_costumers.yview_moveto(0)
    query = e_costumer_search.get().strip()

    try:
        if not query:
            results = customer_manager.list_customers()
        elif customer_search_type == "id":
            try:
                results = [customer_manager.get_customer_by_id(query)]
            except CustomerNotFound:
                results = []
        elif customer_search_type == "identity":
            customer = customer_manager.find_by_identity_number(query)
            results = [customer] if customer else []
        elif customer_search_type == "email":
            customer = customer_manager.find_by_email(query)
            results = [customer] if customer else []
        else:
            results = customer_manager.find_by_name(query)
    except CustomerError as error:
        messagebox.showerror(
            "Customer Search Failed",
            str(error),
            parent=w_customer_search,
        )
        return

    update_customer_tree(results)

    if not results:
        messagebox.showinfo(
            "No Customers Found",
            "No customers matched that search.",
            parent=w_customer_search,
        )
        return

    w_customer_search.withdraw()
    n_main.select(f_clients)
    w_main.lift()


def register_customer():
    try:
        customer_manager.register_customer(
            name=e_costumer_name.get().strip(),
            identity_number=e_costumer_identity.get().strip(),
            email=e_costumer_mail.get().strip(),
            phone_number=e_costumer_phone_number.get().strip(),
            address=e_costumer_address.get().strip(),
        )
    except CustomerError as error:
        messagebox.showerror(
            "Customer Registration Failed",
            str(error),
            parent=w_main,
        )
        return

    update_customer_tree(customer_manager.list_customers())

    for entry in (
        e_costumer_name,
        e_costumer_identity,
        e_costumer_mail,
        e_costumer_phone_number,
        e_costumer_address,
    ):
        entry.delete(0, tk.END)

    messagebox.showinfo(
        "Customer Registered",
        "The customer was registered successfully.",
        parent=w_main,
    )


# --- Services ---

def update_service_tree(services):
    for item in tv_services.get_children():
        tv_services.delete(item)

    for service in services:
        tv_services.insert(
            "",
            "end",
            values=(
                f"{service.identifier:02d}",
                service.name,
                f"{service.base_rate:.2f}",
                "Available" if service.available else "Unavailable",
                f"{service.calculate_cost():.2f}",
                service.description,
            ),
        )

    tv_services.yview_moveto(0)


def select_service_search_type(search_type):
    global service_search_type

    labels = {
        "id": "Introduce the service ID",
        "name": "Introduce the service name",
    }
    service_search_type = search_type
    l_service_search.config(text=labels[search_type])
    e_service_search.delete(0, tk.END)
    update_service_tree(service_manager.list_services())
    e_service_search.focus_set()


def search_services():
    tv_services.yview_moveto(0)
    query = e_service_search.get().strip()

    try:
        if not query:
            results = service_manager.list_services()
        elif service_search_type == "id":
            try:
                results = [service_manager.get_service_by_id(query)]
            except ServiceNotFound:
                results = []
        else:
            results = service_manager.find_by_name(query)
    except ServiceError as error:
        messagebox.showerror(
            "Service Search Failed",
            str(error),
            parent=w_services_search,
        )
        return

    update_service_tree(results)

    if not results:
        messagebox.showinfo(
            "No Services Found",
            "No services matched that search.",
            parent=w_services_search,
        )
        return

    w_services_search.withdraw()
    n_main.select(f_services)
    w_main.lift()


def delete_service():
    service_id = e_service_delete.get().strip()

    try:
        service = service_manager.delete_service(service_id)
    except ServiceError as error:
        messagebox.showerror(
            "Service Deletion Failed",
            str(error),
            parent=w_services_delete,
        )
        return

    update_service_tree(service_manager.list_services())
    e_service_delete.delete(0, tk.END)
    messagebox.showinfo(
        "Service Deleted",
        f"Service '{service.name}' was deleted successfully.",
        parent=w_services_delete,
    )
    w_services_delete.withdraw()


def reset_inactive_search_results(event):
    selected_tab = event.widget.select()

    if selected_tab != str(f_clients):
        e_costumer_search.delete(0, tk.END)
        update_customer_tree(customer_manager.list_customers())

    if selected_tab != str(f_services):
        e_service_search.delete(0, tk.END)
        update_service_tree(service_manager.list_services())


def parse_positive_float(value, field_name):
    try:
        number = float(value)
    except ValueError as error:
        raise ValueError(f"{field_name} must be a number.") from error

    if not math.isfinite(number) or number <= 0:
        raise ValueError(f"{field_name} must be greater than zero.")

    return number


def parse_integer(value, field_name):
    try:
        return int(value)
    except ValueError as error:
        raise ValueError(f"{field_name} must be a whole number.") from error


def clear_service_form(entries, description_widget, availability):
    for entry in entries:
        if isinstance(entry, ttk.Combobox):
            entry.set("")
        else:
            entry.delete(0, tk.END)

    description_widget.delete("1.0", tk.END)
    availability.set(True)


def register_advisory_service():
    try:
        service = AdvisoryService(
            name=e_Services_Advysory_name.get().strip(),
            description=t_Services_Advysory_Description.get(
                "1.0",
                "end-1c",
            ).strip(),
            base_rate=parse_positive_float(
                e_Services_Advysory_fee.get().strip(),
                "Rate",
            ),
            area=e_Services_Advysory_area.get().strip(),
            advisor=e_Services_Advysory_advisor.get().strip(),
            session_duration=parse_positive_float(
                e_Services_Advysory_duration.get().strip(),
                "Session duration",
            ),
            available=v_Advysory_Availability.get(),
        )
        service_manager.register_service(service)
    except ValueError as error:
        messagebox.showerror(
            "Invalid Advisory Data",
            str(error),
            parent=w_advysory,
        )
        return
    except ServiceError as error:
        messagebox.showerror(
            "Advisory Registration Failed",
            str(error),
            parent=w_advysory,
        )
        return

    update_service_tree(service_manager.list_services())
    clear_service_form(
        (
            e_Services_Advysory_name,
            e_Services_Advysory_fee,
            e_Services_Advysory_advisor,
            e_Services_Advysory_duration,
            e_Services_Advysory_area,
        ),
        t_Services_Advysory_Description,
        v_Advysory_Availability,
    )
    messagebox.showinfo(
        "Advisory Registered",
        "The advisory service was registered successfully.",
        parent=w_advysory,
    )


def register_room_service():
    try:
        service = RoomService(
            name=e_Services_Book_name.get().strip(),
            description=t_Services_Book_Description.get(
                "1.0",
                "end-1c",
            ).strip(),
            base_rate=parse_positive_float(
                e_Services_Book_fee.get().strip(),
                "Rate",
            ),
            capacity=parse_integer(
                e_Services_Book_capacity.get().strip(),
                "Capacity",
            ),
            location=e_Services_Book_location.get().strip(),
            available=v_Book_Availability.get(),
        )
        service_manager.register_service(service)
    except ValueError as error:
        messagebox.showerror(
            "Invalid Booking Data",
            str(error),
            parent=w_book,
        )
        return
    except ServiceError as error:
        messagebox.showerror(
            "Booking Registration Failed",
            str(error),
            parent=w_book,
        )
        return

    update_service_tree(service_manager.list_services())
    clear_service_form(
        (
            e_Services_Book_name,
            e_Services_Book_fee,
            e_Services_Book_capacity,
            e_Services_Book_location,
        ),
        t_Services_Book_Description,
        v_Book_Availability,
    )
    messagebox.showinfo(
        "Booking Service Registered",
        "The room service was registered successfully.",
        parent=w_book,
    )


def register_rental_service():
    try:
        service = EquipmentRentalService(
            name=e_Services_Rent_name.get().strip(),
            description=t_Services_Rent_Description.get(
                "1.0",
                "end-1c",
            ).strip(),
            base_rate=parse_positive_float(
                e_Services_Rent_fee.get().strip(),
                "Rate",
            ),
            equipment_type=cb_Services_Rent_equipment_type.get().strip(),
            brand=cb_Services_Rent_brand.get().strip(),
            available_quantity=parse_integer(
                e_Services_Rent_actual_stock.get().strip(),
                "Available quantity",
            ),
            available=v_Rent_Availability.get(),
        )
        service_manager.register_service(service)
    except ValueError as error:
        messagebox.showerror(
            "Invalid Rental Data",
            str(error),
            parent=w_rent,
        )
        return
    except ServiceError as error:
        messagebox.showerror(
            "Rental Registration Failed",
            str(error),
            parent=w_rent,
        )
        return

    update_service_tree(service_manager.list_services())
    clear_service_form(
        (
            e_Services_Rent_name,
            e_Services_Rent_fee,
            cb_Services_Rent_equipment_type,
            cb_Services_Rent_brand,
            e_Services_Rent_actual_stock,
        ),
        t_Services_Rent_Description,
        v_Rent_Availability,
    )
    messagebox.showinfo(
        "Rental Service Registered",
        "The equipment rental service was registered successfully.",
        parent=w_rent,
    )


# --- Reservations ---

def update_reservation_tree(reservations):
    for item in tv_reservations.get_children():
        tv_reservations.delete(item)

    for reservation in reservations:
        tv_reservations.insert(
            "",
            "end",
            values=(
                f"{reservation.id:02d}",
                reservation.customer.name,
                reservation.service.name,
                reservation.date.strftime("%Y-%m-%d"),
                reservation.customer.phone_number,
                reservation.service.description,
            ),
        )

    tv_reservations.yview_moveto(0)


def register_reservation():
    try:
        customer = customer_manager.get_customer_by_id(
            e_reservations_customer.get().strip()
        )
        service = service_manager.get_service_by_id(
            e_reservations_service.get().strip()
        )
        reservation_date = datetime.strptime(
            "/".join((
                e_reservations_date_part_1.get().strip(),
                e_reservations_date_part_2.get().strip(),
                e_reservations_date_part_3.get().strip(),
            )),
            "%d/%m/%y",
        )
        duration = parse_positive_float(
            e_reservations_duration.get().strip(),
            "Duration",
        )
        reservation = Reservation(
            customer,
            service,
            duration,
            reservation_date,
        )
        reservation.calculate_cost()
        reservation_manager.register_reservation(reservation)
    except ValueError as error:
        messagebox.showerror(
            "Invalid Reservation Data",
            "Enter a valid duration and date in DD/MM/YY format.\n"
            f"{error}",
            parent=w_main,
        )
        return
    except (CustomerError, ServiceError, ReservationError) as error:
        messagebox.showerror(
            "Reservation Registration Failed",
            str(error),
            parent=w_main,
        )
        return

    update_reservation_tree(reservation_manager.list_reservations())
    for entry in (
        e_reservations_customer,
        e_reservations_service,
        e_reservations_date_part_1,
        e_reservations_date_part_2,
        e_reservations_date_part_3,
        e_reservations_duration,
    ):
        entry.delete(0, tk.END)

    messagebox.showinfo(
        "Reservation Registered",
        "The reservation was registered successfully.",
        parent=w_main,
    )


def search_reservations():
    reservation_id = e_reservations_search_id.get().strip()

    try:
        if not reservation_id:
            results = reservation_manager.list_reservations()
        else:
            try:
                results = [reservation_manager.get_by_id(reservation_id)]
            except ReservationNotFound:
                results = []
    except ReservationError as error:
        messagebox.showerror(
            "Reservation Search Failed",
            str(error),
            parent=w_main,
        )
        return

    update_reservation_tree(results)

    if not results:
        messagebox.showinfo(
            "No Reservations Found",
            "No reservations matched that ID.",
            parent=w_main,
        )


# --- Test data ---

def add_test_data():
    global test_data_loaded

    if test_data_loaded:
        messagebox.showinfo(
            "Test Data",
            "The sample records have already been added.",
            parent=w_main,
        )
        return

    customer_records = (
        ("Alex Morgan", "TSTCUST0001", "test.customer01@example.com", "3001234501", "Test Address 01"),
        ("Jamie Lee", "TSTCUST0002", "test.customer02@example.com", "3001234502", "Test Address 02"),
        ("Casey Rivera", "TSTCUST0003", "test.customer03@example.com", "3001234503", "Test Address 03"),
        ("Morgan Chen", "TSTCUST0004", "test.customer04@example.com", "3001234504", "Test Address 04"),
        ("Riley Patel", "TSTCUST0005", "test.customer05@example.com", "3001234505", "Test Address 05"),
        ("Avery Kim", "TSTCUST0006", "test.customer06@example.com", "3001234506", "Test Address 06"),
        ("Jordan Smith", "TSTCUST0007", "test.customer07@example.com", "3001234507", "Test Address 07"),
        ("Cameron Diaz", "TSTCUST0008", "test.customer08@example.com", "3001234508", "Test Address 08"),
        ("Drew Wilson", "TSTCUST0009", "test.customer09@example.com", "3001234509", "Test Address 09"),
        ("Skyler Brown", "TSTCUST0010", "test.customer10@example.com", "3001234510", "Test Address 10"),
    )
    service_records = (
        RoomService("Test Room One", "Sample meeting room", 50000, 20, "Floor One"),
        RoomService("Test Room Two", "Sample conference room", 60000, 30, "Floor Two"),
        RoomService("Test Room Three", "Sample training room", 45000, 18, "Floor Three"),
        RoomService("Test Room Four", "Sample classroom", 40000, 25, "Floor Four"),
        EquipmentRentalService(
            "Test Projector Rental",
            "Sample projector rental",
            25000,
            "Projectors",
            "Epson",
            5,
        ),
        EquipmentRentalService(
            "Test Laptop Rental",
            "Sample laptop rental",
            35000,
            "Laptops",
            "Dell",
            8,
        ),
        EquipmentRentalService(
            "Test Camera Rental",
            "Sample camera rental",
            40000,
            "Cameras",
            "Canon",
            3,
        ),
        AdvisoryService(
            "Test Technology Advisory",
            "Sample technology advisory",
            75000,
            "Technology",
            "Alex Morgan",
            1,
        ),
        AdvisoryService(
            "Test Finance Advisory",
            "Sample finance advisory",
            80000,
            "Finance",
            "Jamie Lee",
            1,
        ),
        AdvisoryService(
            "Test Design Advisory",
            "Sample design advisory",
            70000,
            "Design",
            "Casey Rivera",
            1,
        ),
    )

    try:
        customers = [
            customer_manager.register_customer(
                name=name,
                identity_number=identity_number,
                email=email,
                phone_number=phone_number,
                address=address,
            )
            for name, identity_number, email, phone_number, address
            in customer_records
        ]
        services = [
            service_manager.register_service(service)
            for service in service_records
        ]

        for index in range(5):
            reservation = Reservation(
                customers[index],
                services[index],
                1,
                datetime.now() + timedelta(days=index + 1),
            )
            reservation.calculate_cost()
            reservation_manager.register_reservation(reservation)
    except (CustomerError, ServiceError, ReservationError) as error:
        update_customer_tree(customer_manager.list_customers())
        update_service_tree(service_manager.list_services())
        update_reservation_tree(reservation_manager.list_reservations())
        messagebox.showerror(
            "Test Data Failed",
            str(error),
            parent=w_main,
        )
        return

    test_data_loaded = True
    update_customer_tree(customer_manager.list_customers())
    update_service_tree(service_manager.list_services())
    update_reservation_tree(reservation_manager.list_reservations())
    messagebox.showinfo(
        "Test Data Added",
        "Added 10 customers, 10 services, and 5 reservations.",
        parent=w_main,
    )


def add_test_data_hotkey(event):
    if event.char.lower() != "t" or not w_main.winfo_viewable():
        return

    if event.widget.winfo_class() in {
        "Entry",
        "TEntry",
        "Text",
        "TCombobox",
        "Spinbox",
        "TSpinbox",
    }:
        return

    add_test_data()
    return "break"


# --- Window controls ---

def show_service_window(window):
    window.deiconify()
    window.lift()
    window.focus_set()


def close_application():
    w_login.destroy()


def log_out():
    w_main.withdraw()
    w_login.deiconify()
    w_login.lift()
    w_login.focus_set()


# --- Widgets ---

# --- Windows

w_login = tk.Tk()
w_login.title("Login")
w_login.geometry("640x480")
w_login.resizable(False, False)
w_login.configure(background="#f0f0f0")

w_main = tk.Toplevel(w_login)
w_main.title("Main Window")
w_main.geometry("1280x960")
w_main.resizable(False, False)
w_main.configure(background="#f0f0f0")
w_main.withdraw()

# - Searchs

w_customer_search = tk.Toplevel(w_main)
w_customer_search.title("Customer Search")
w_customer_search.geometry("640x480")
w_customer_search.resizable(False, False)
w_customer_search.configure(background="#f0f0f0")
w_customer_search.withdraw()

w_services_search = tk.Toplevel(w_main)
w_services_search.title("Services Search")
w_services_search.geometry("640x480")
w_services_search.resizable(False, False)
w_services_search.configure(background="#f0f0f0")
w_services_search.withdraw()

# - Another Windows

w_advysory = tk.Toplevel(w_main)
w_advysory.title ("New Advysory")
w_advysory.geometry("1024x768")
w_advysory.resizable(False, False)

w_book = tk.Toplevel(w_main)
w_book.title("New Booking")
w_book.geometry("1024x768")
w_book.resizable(False, False)

w_rent = tk.Toplevel(w_main)
w_rent.title("New Rent")
w_rent.geometry("1024x768")
w_rent.resizable(False, False)

w_services_delete = tk.Toplevel(w_main)
w_services_delete.title("Delete a Service")
w_services_delete.geometry("640x480")
w_services_delete.resizable(False, False)
w_services_delete.configure(background="#f0f0f0")
w_services_delete.withdraw()

for w_service in (w_advysory, w_book, w_rent):
    w_service.configure(background="#f0f0f0")
    w_service.withdraw()
    w_service.protocol("WM_DELETE_WINDOW", w_service.withdraw)


w_main.protocol("WM_DELETE_WINDOW", close_application)
w_customer_search.protocol("WM_DELETE_WINDOW", w_customer_search.withdraw)
w_services_search.protocol("WM_DELETE_WINDOW", w_services_search.withdraw)
w_services_delete.protocol("WM_DELETE_WINDOW", w_services_delete.withdraw)


# -- Styles
style = ttk.Style(w_main)
style.theme_use("clam")
style.configure("Background.TLabel", background="#f0f0f0")
style.configure("HomeBackground.TLabel", background="#f0f0f0")
style.configure("TFrame", background="#f0f0f0")
style.configure(
    "TitleBlue.TLabel",
    foreground="#026abb",
    font=("Segoe UI Variable Display", 25, "bold"),
)
style.configure(
    "Costumer.Treeview",
    font=("Segoe UI", 11),
    rowheight=30,
    background="#ffffff",
    fieldbackground="#ffffff",
    foreground="#0430ba",
)
style.configure(
    "Costumer.Treeview.Heading",
    font=("Segoe UI Semibold", 11),
    background="#f5f5f5",
    foreground="#0430ba",
)
style.map(
    "Costumer.Treeview",
    background=[("selected", "#0430ba")],
    foreground=[("selected", "#ffffff")],
)
style.configure("TNotebook", background="#ffffff", borderwidth=0)
style.configure(
    "TNotebook.Tab",
    font=("Segoe UI Semibold", 15),
    foreground="#026abb",
    background="#f5f5f5",
    padding=(18, 8),
)
style.map(
    "TNotebook.Tab",
    foreground=[("selected", "#0430ba"), ("!selected", "#026abb")],
    background=[("selected", "#ffffff"), ("!selected", "#f5f5f5")],
)

# -- Login

#- Images
i_login_background = Image.open(
    asset_path("Fj Software/Interfaz/Login/1x/Login_background.png")
)

i_login_background = i_login_background.resize((477, 480))

img_login_background= ImageTk.PhotoImage(
    i_login_background,
    master=w_login
)

l_login_background = ttk.Label(
    w_login,
    image=img_login_background,
    style="Background.TLabel"
)

l_login_background.image = img_login_background

l_login_background.place(x=-2, y=0)

# - Entrys



e_user = ttk.Entry(
    w_login,
    width= 25,
    font=("Segoe UI Semibold",12)

)

e_user.place(
    x=348,
    y=166
)

e_password = ttk.Entry(
    w_login,
    width= 25,
    font=("Segoe UI Semibold",12),
    show="*",

)

e_password .place(
    x=348,
    y=254
)





# - Buttons

i_Sign_In = Image.open(
    asset_path("Fj Software/Interfaz/Login/1x/SigIn_Button.png")
)

i_Sign_In = i_Sign_In.resize(
    (175, 55)
)

img_Sign_In = ImageTk.PhotoImage(
    i_Sign_In,
    master=w_login
)

b_Sign_In = tk.Button(
    w_login,
    image=img_Sign_In,
    borderwidth=0,
    command=sign_in,
)

b_Sign_In.image = img_Sign_In

b_Sign_In.place(
    x=348,
    y=309
)

# --- Main

n_main = ttk.Notebook(w_main)
n_main.pack(fill="both", expand=True)

f_home = ttk.Frame(n_main)
f_clients = ttk.Frame(n_main)
f_services = ttk.Frame(n_main)
f_reservations = ttk.Frame(n_main)

n_main.add(f_home, text="Home")
n_main.add(f_clients, text="Clients")
n_main.add(f_services, text="Services")
n_main.add(f_reservations, text="Reservations")

# -- Home

# - Images

i_Home_background = Image.open(
    asset_path("Fj Software/Interfaz/Home/1x/Home_background.png")
)

i_Home_background = i_Home_background.resize((1279, 848))

img_Home_background= ImageTk.PhotoImage(
    i_Home_background,
    master=f_home
)

l_Home_background= ttk.Label(
    f_home,
    image=img_Home_background,
    style="HomeBackground.TLabel"
)

l_Home_background.image = img_Home_background

l_Home_background.place(x=-2, y=0) 


# - Buttons

i_Clients_Home_button = Image.open(
    asset_path("Fj Software/Interfaz/Home/1x/Clients_Home_button.png")
)

i_Clients_Home_button = i_Clients_Home_button.resize(
    (180, 180)
)

img_Clients_Home_button = ImageTk.PhotoImage(
    i_Clients_Home_button,
    master=f_home
)

b_Clients_Home_button = tk.Button(
    f_home,
    image=img_Clients_Home_button,
    background="#f0f0f0",
    activebackground="#f0f0f0",
    borderwidth=0,
    highlightthickness=0,
    relief="flat",
    overrelief="flat",
    padx=0,
    pady=0,
    command=lambda: n_main.select(f_clients),
)

b_Clients_Home_button.place(
    x=266,
    y=632
)

i_Services_Home_button = Image.open(
    asset_path("Fj Software/Interfaz/Home/1x/Services_Home_Button.png")
)

i_Services_Home_button = i_Services_Home_button.resize(
    (180, 180)
)

img_Services_Home_button = ImageTk.PhotoImage(
    i_Services_Home_button,
    master=f_home
)

b_Services_Home_button = tk.Button(
    f_home,
    image=img_Services_Home_button,
    background="#f0f0f0",
    activebackground="#f0f0f0",
    borderwidth=0,
    highlightthickness=0,
    relief="flat",
    overrelief="flat",
    padx=0,
    pady=0,
    command=lambda: n_main.select(f_services),
)

b_Services_Home_button.place(
    x=576,
    y=632
)

i_Reservations_Home_button = Image.open(
    asset_path("Fj Software/Interfaz/Home/1x/Reservations_Home_Button.png")
)

i_Reservations_Home_button = i_Reservations_Home_button.resize(
    (180, 180)
)

img_Reservations_Home_button = ImageTk.PhotoImage(
    i_Reservations_Home_button,
    master=f_home
)

b_Reservations_Home_button = tk.Button(
    f_home,
    image=img_Reservations_Home_button,
    background="#f0f0f0",
    activebackground="#f0f0f0",
    borderwidth=0,
    highlightthickness=0,
    relief="flat",
    overrelief="flat",
    padx=0,
    pady=0,
    command=lambda: n_main.select(f_reservations),
)

b_Reservations_Home_button.place(
    x=898,
    y=632
)

i_logOut_Home_Button = Image.open(
    asset_path("Fj Software/Interfaz/Home/1x/logOut_Home_Button.png")
)

i_logOut_Home_Button = i_logOut_Home_Button.resize(
    (137, 46)
)

img_logOut_Home_Button = ImageTk.PhotoImage(
    i_logOut_Home_Button,
    master=f_home
)

b_logOut_Home_Button = tk.Button(
    f_home,
    image=img_logOut_Home_Button,
    background="#f0f0f0",
    activebackground="#f0f0f0",
    borderwidth=0,
    highlightthickness=0,
    relief="flat",
    overrelief="flat",
    padx=0,
    pady=0,
    command=log_out,
)

b_logOut_Home_Button.place(
    x=1124,
    y=856
)

# -- Clients

# - Images

i_Costumer_background = Image.open(
    asset_path("Fj Software/Interfaz/Costumer/1x/Costumer_background.png")
)

i_Costumer_background = i_Costumer_background.resize((993, 891))

img_Costumer_background= ImageTk.PhotoImage(
    i_Costumer_background,
    master=f_clients
)

l_Costumer_background= ttk.Label(
    f_clients,
    image=img_Costumer_background,
    style="HomeBackground.TLabel"
)

l_Costumer_background.image = img_Costumer_background

l_Costumer_background.place(x=-2, y=0) 

e_costumer_name = ttk.Entry(
    f_clients,
    width=13,
    font=("Segoe UI Semibold", 12)
)
e_costumer_name.place(
    x=25,
    y=377
)

e_costumer_identity = ttk.Entry(
    f_clients,
    width=13,
    font=("Segoe UI Semibold", 12)
)
e_costumer_identity.place(
    x=181,
    y=377
)

e_costumer_mail = ttk.Entry(
    f_clients,
    width=30,
    font=("Segoe UI Semibold", 12)
)
e_costumer_mail.place(
    x=25,
    y=482
)

e_costumer_phone_number = ttk.Entry(
    f_clients,
    width=30,
    font=("Segoe UI Semibold", 12)
)
e_costumer_phone_number.place(
    x=25,
    y=597
)

e_costumer_address = ttk.Entry(
    f_clients,
    width=30,
    font=("Segoe UI Semibold", 12)
)
e_costumer_address.place(
    x=25,
    y=705
)

tv_costumers = ttk.Treeview(
    f_clients,
    columns=("id", "name", "identity", "email", "phone", "address"),
    show="headings",
    style="Costumer.Treeview",
)

tv_costumers.heading("id", text="ID")
tv_costumers.heading("name", text="Name")
tv_costumers.heading("identity", text="Identity")
tv_costumers.heading("email", text="Email")
tv_costumers.heading("phone", text="Phone Number")
tv_costumers.heading("address", text="Address")

tv_costumers.column("id", width=70, minwidth=70, anchor="center", stretch=False)
tv_costumers.column("name", width=135, minwidth=100, anchor="w", stretch=False)
tv_costumers.column("identity", width=130, minwidth=100, anchor="w", stretch=False)
tv_costumers.column("email", width=190, minwidth=120, anchor="w", stretch=False)
tv_costumers.column("phone", width=145, minwidth=100, anchor="w", stretch=False)
tv_costumers.column("address", width=180, minwidth=120, anchor="w", stretch=True)

tv_costumers.place(
    x=393,
    y=82,
    width=870,
    height=710,
)

# - Buttons

i_Costumer_Register_button = Image.open(
    asset_path("Fj Software/Interfaz/Costumer/1x/Costumer_Register_button.png")
)

i_Costumer_Register_button = i_Costumer_Register_button.resize(
    (264, 55)
)

img_Costumer_Register_button = ImageTk.PhotoImage(
    i_Costumer_Register_button,
    master=f_clients
)

b_Costumer_Register = tk.Button(
    f_clients,
    image=img_Costumer_Register_button,
    background="#0438ba",
    activebackground="#0438ba",
    borderwidth=0,
    highlightthickness=0,
    relief="flat",
    overrelief="flat",
    padx=0,
    pady=0,
    command=register_customer,
)

b_Costumer_Register.place(
    x=33,
    y=790
)

i_Costumer_Search_button = Image.open(
    asset_path("Fj Software/Interfaz/Costumer/1x/Costumer_Search_button.png")
)

i_Costumer_Search_button = i_Costumer_Search_button.resize(
    (183, 55)
)

img_Costumer_Search_button = ImageTk.PhotoImage(
    i_Costumer_Search_button,
    master=f_clients
)

b_Costumer_Search = tk.Button(
    f_clients,
    image=img_Costumer_Search_button,
    background="#f0f0f0",
    activebackground="#f0f0f0",
    borderwidth=0,
    highlightthickness=0,
    relief="flat",
    overrelief="flat",
    padx=0,
    pady=0,
    command=show_customer_search,
)

b_Costumer_Search.place(
    x=711,
    y=810
)

# - Customer Search

i_Costumer_search_background = Image.open(
    asset_path("Fj Software/Interfaz/Costumer/1x/Costumer_Search_background.png")
)

i_Costumer_search_background = i_Costumer_search_background.resize((642, 279))

img_Costumer_search_background= ImageTk.PhotoImage(
    i_Costumer_search_background,
    master=w_customer_search
)

l_Costumer_search_background= ttk.Label(
    w_customer_search,
    image=img_Costumer_search_background,
    style="HomeBackground.TLabel"
)

l_Costumer_search_background.image = img_Costumer_search_background

l_Costumer_search_background.place(x=0, y=0) 


# -- Buttons

i_Costumer_Search_ID_button = Image.open(
    asset_path("Fj Software/Interfaz/Costumer/1x/Costumer_Search_ID.png")
)

i_Costumer_Search_ID_button = i_Costumer_Search_ID_button.resize(
    (296, 86)
)

img_Costumer_Search_ID_button = ImageTk.PhotoImage(
    i_Costumer_Search_ID_button,
    master=w_customer_search
)

b_Costumer_Search_ID = tk.Button(
    w_customer_search,
    image=img_Costumer_Search_ID_button,
    background="#0430ba",
    activebackground="#0430ba",
    borderwidth=0,
    highlightthickness=0,
    relief="flat",
    overrelief="flat",
    padx=0,
    pady=0,
    command=lambda: select_customer_search_type("id"),
)

b_Costumer_Search_ID.place(
    x=39,
    y=78
)

i_Costumer_Search_CC_button = Image.open(
    asset_path("Fj Software/Interfaz/Costumer/1x/Costumer_Search_CC.png")
)
i_Costumer_Search_CC_button = i_Costumer_Search_CC_button.resize(
    (296, 86)
)
img_Costumer_Search_CC_button = ImageTk.PhotoImage(
    i_Costumer_Search_CC_button,
    master=w_customer_search
)
b_Costumer_Search_CC = tk.Button(
    w_customer_search,
    image=img_Costumer_Search_CC_button,
    background="#0430ba",
    activebackground="#0430ba",
    borderwidth=0,
    highlightthickness=0,
    relief="flat",
    overrelief="flat",
    padx=0,
    pady=0,
    command=lambda: select_customer_search_type("identity"),
)
b_Costumer_Search_CC.place(
    x=347,
    y=78
)

i_Costumer_Search_Mail_button = Image.open(
    asset_path("Fj Software/Interfaz/Costumer/1x/Costumer_Search_Mail.png")
)
i_Costumer_Search_Mail_button = i_Costumer_Search_Mail_button.resize(
    (296, 86)
)
img_Costumer_Search_Mail_button = ImageTk.PhotoImage(
    i_Costumer_Search_Mail_button,
    master=w_customer_search
)
b_Costumer_Search_Mail = tk.Button(
    w_customer_search,
    image=img_Costumer_Search_Mail_button,
    background="#0430ba",
    activebackground="#0430ba",
    borderwidth=0,
    highlightthickness=0,
    relief="flat",
    overrelief="flat",
    padx=0,
    pady=0,
    command=lambda: select_customer_search_type("email"),
)
b_Costumer_Search_Mail.place(
    x=39,
    y=176
)

i_Costumer_Search_Name_button = Image.open(
    asset_path("Fj Software/Interfaz/Costumer/1x/Costumer_Search_Name.png")
)
i_Costumer_Search_Name_button = i_Costumer_Search_Name_button.resize(
    (296, 86)
)
img_Costumer_Search_Name_button = ImageTk.PhotoImage(
    i_Costumer_Search_Name_button,
    master=w_customer_search
)
b_Costumer_Search_Name = tk.Button(
    w_customer_search,
    image=img_Costumer_Search_Name_button,
    background="#0430ba",
    activebackground="#0430ba",
    borderwidth=0,
    highlightthickness=0,
    relief="flat",
    overrelief="flat",
    padx=0,
    pady=0,
    command=lambda: select_customer_search_type("name"),
)
b_Costumer_Search_Name.place(
    x=347,
    y=176
)


i_Costumer_Search_Dialogue_button = Image.open(
    asset_path("Fj Software/Interfaz/Costumer/1x/Costumer_Search_Dialogue_button.png")
)

i_Costumer_Search_Dialogue_button = i_Costumer_Search_Dialogue_button.resize(
    (264, 55)
)

img_Costumer_Search_Dialogue_button = ImageTk.PhotoImage(
    i_Costumer_Search_Dialogue_button,
    master=w_customer_search
)

b_Costumer_Search_Dialogue = tk.Button(
    w_customer_search,
    image=img_Costumer_Search_Dialogue_button,
    background="#f0f0f0",
    activebackground="#f0f0f0",
    borderwidth=0,
    highlightthickness=0,
    relief="flat",
    overrelief="flat",
    padx=0,
    pady=0,
    command=search_customers,
)

b_Costumer_Search_Dialogue.place(
    x=190,
    y=401
)

# - Labels

l_costumer_search_label = ttk.Label(
    w_customer_search,
    text="Introduce the customer ID",
    style="TitleBlue.TLabel"
)

l_costumer_search_label.place(x=117,y=295)

# - Entrys

e_costumer_search = ttk.Entry(
    w_customer_search,
    width=30,
    font=("Segoe UI Semibold", 12)
)
e_costumer_search.place(
    x=179,
    y=357
)



# -- Services

# - Images

i_Services_background = Image.open(
    asset_path("Fj Software/Interfaz/Services/1x/Services_Background.png")
)

i_Services_background = i_Services_background.resize((946, 416))

img_Services_background= ImageTk.PhotoImage(
    i_Services_background,
    master=f_services
)

l_Services_background= ttk.Label(
    f_services,
    image=img_Services_background,
    style="HomeBackground.TLabel"
)

l_Services_background.image = img_Services_background

l_Services_background.place(x=21, y=77) 


# - Treeview

tv_services = ttk.Treeview(
    f_services,
    columns=("id", "name", "base_fee", "availability", "cost", "description"),
    show="headings",
    style="Costumer.Treeview",
)

tv_services.heading("id", text="ID")
tv_services.heading("name", text="Name")
tv_services.heading("base_fee", text="Base Fee")
tv_services.heading("availability", text="Availability")
tv_services.heading("cost", text="Cost")
tv_services.heading("description", text="Description")

tv_services.column("id", width=70, minwidth=70, anchor="center", stretch=False)
tv_services.column("name", width=145, minwidth=100, anchor="w", stretch=False)
tv_services.column("base_fee", width=145, minwidth=100, anchor="w", stretch=False)
tv_services.column(
    "availability",
    width=150,
    minwidth=100,
    anchor="w",
    stretch=False,
)
tv_services.column("cost", width=120, minwidth=90, anchor="center", stretch=False)
tv_services.column("description", width=230, minwidth=120, anchor="w", stretch=True)

tv_services.place(
    x=369,
    y=141,
    width=870,
    height=668,
)

# - Buttons

i_Services_Advysory_button = Image.open(
    asset_path("Fj Software/Interfaz/Services/1x/Services_Advysory_button.png")
)

i_Services_Advysory_button = i_Services_Advysory_button.resize(
    (139, 139)
)

img_Services_Advysory_button = ImageTk.PhotoImage(
    i_Services_Advysory_button,
    master=f_services
)

b_Services_Advysory = tk.Button(
    f_services,
    image=img_Services_Advysory_button,
    background="#f0f0f0",
    activebackground="#f0f0f0",
    borderwidth=0,
    highlightthickness=0,
    relief="flat",
    overrelief="flat",
    padx=0,
    pady=0,
    command=lambda: show_service_window(w_advysory)
)

b_Services_Advysory.place(
    x=23,
    y=515
)

i_Services_Book_button = Image.open(
    asset_path("Fj Software/Interfaz/Services/1x/Services_Book_button.png")
)

i_Services_Book_button = i_Services_Book_button.resize(
    (139, 139)
)

img_Services_Book_button = ImageTk.PhotoImage(
    i_Services_Book_button,
    master=f_services
)

b_Services_Book = tk.Button(
    f_services,
    image=img_Services_Book_button,
    background="#f0f0f0",
    activebackground="#f0f0f0",
    borderwidth=0,
    highlightthickness=0,
    relief="flat",
    overrelief="flat",
    padx=0,
    pady=0,
    command=lambda: show_service_window(w_book),
)

b_Services_Book.place(
    x=178,
    y=515
)

i_Services_Rent_button = Image.open(
    asset_path("Fj Software/Interfaz/Services/1x/Services_Rent_button.png")
)

i_Services_Rent_button = i_Services_Rent_button.resize(
    (139, 139)
)

img_Services_Rent_button = ImageTk.PhotoImage(
    i_Services_Rent_button,
    master=f_services
)

b_Services_Rent = tk.Button(
    f_services,
    image=img_Services_Rent_button,
    background="#f0f0f0",
    activebackground="#f0f0f0",
    borderwidth=0,
    highlightthickness=0,
    relief="flat",
    overrelief="flat",
    padx=0,
    pady=0,
    command=lambda: show_service_window(w_rent),
)

b_Services_Rent.place(
    x=23,
    y=670
)

i_Services_Search_button = Image.open(
    asset_path("Fj Software/Interfaz/Services/1x/Services_Search_button.png")
)

i_Services_Search_button = i_Services_Search_button.resize(
    (183, 55)
)

img_Services_Search_button = ImageTk.PhotoImage(
    i_Services_Search_button,
    master=f_services
)

b_Services_Search = tk.Button(
    f_services,
    image=img_Services_Search_button,
    background="#f0f0f0",
    activebackground="#f0f0f0",
    borderwidth=0,
    highlightthickness=0,
    relief="flat",
    overrelief="flat",
    padx=0,
    pady=0,
    command=lambda: show_service_window(w_services_search),
)

b_Services_Search.place(
    x=597,
    y=834
)

i_Services_Delete_button = Image.open(
    asset_path("Fj Software/Interfaz/Services/1x/Services_Delete_button.png")
)

i_Services_Delete_button = i_Services_Delete_button.resize(
    (183, 55)
)

img_Services_Delete_button = ImageTk.PhotoImage(
    i_Services_Delete_button,
    master=f_services
)

b_Services_Delete = tk.Button(
    f_services,
    image=img_Services_Delete_button,
    background="#f0f0f0",
    activebackground="#f0f0f0",
    borderwidth=0,
    highlightthickness=0,
    relief="flat",
    overrelief="flat",
    padx=0,
    pady=0,
    command=lambda: show_service_window(w_services_delete),
)

b_Services_Delete.place(
    x=815,
    y=834
)

# - Advysory

# Images

i_Services_Advysory_background = Image.open(
    asset_path("Fj Software/Interfaz/Services/1x/Service_Advysory_background.png")
)

i_Services_Advysory_background = i_Services_Advysory_background.resize((874, 767))

img_Services_Advysory_background= ImageTk.PhotoImage(
    i_Services_Advysory_background,
    master=w_advysory
)

l_Services_Advysory_background= ttk.Label(
    w_advysory,
    image=img_Services_Advysory_background,
    style="HomeBackground.TLabel"
)

l_Services_Advysory_background.image = img_Services_Advysory_background

l_Services_Advysory_background.place(x=-2, y=0) 

# Entrys

e_Services_Advysory_name = ttk.Entry(
    w_advysory,
    width=20,
    font=("Segoe UI Semibold", 12)
)
e_Services_Advysory_name.place(
    x=527,
    y=301
)


e_Services_Advysory_fee = ttk.Entry(
    w_advysory,
    width=20,
    font=("Segoe UI Semibold", 12)
)
e_Services_Advysory_fee.place(
    x=754,
    y=301
)

t_Services_Advysory_Description = tk.Text(
    w_advysory,
    wrap="word",
    font=("Segoe UI Semibold", 12)
)
t_Services_Advysory_Description.place(
    x=525,
    y=378,
    width=175,
    height=62,
)

v_Advysory_Availability = tk.BooleanVar(master=w_advysory, value=True)
ch_Advysory_Avability = ttk.Checkbutton(
    w_advysory,
    variable=v_Advysory_Availability,
)

ch_Advysory_Avability.place(
    x= 757,
    y=384
)

e_Services_Advysory_advisor = ttk.Entry(
    w_advysory,
    width=20,
    font=("Segoe UI Semibold", 12)
)
e_Services_Advysory_advisor.place(x=527, y=530)

e_Services_Advysory_duration = ttk.Entry(
    w_advysory,
    width=20,
    font=("Segoe UI Semibold", 12)
)
e_Services_Advysory_duration.place(x=754, y=530)

e_Services_Advysory_area = ttk.Entry(
    w_advysory,
    width=20,
    font=("Segoe UI Semibold", 12)
)
e_Services_Advysory_area.place(x=526, y=592)

# Buttons

i_Services_Advysory_Register_button = Image.open(
    asset_path("Fj Software/Interfaz/Services/1x/Service_Advysory_Register_button.png")
)

i_Services_Advysory_Register_button = i_Services_Advysory_Register_button.resize(
    (264, 55)
)

img_Services_Advysory_Register_button = ImageTk.PhotoImage(
    i_Services_Advysory_Register_button,
    master=w_advysory
)

b_Services_Advysory_Register = tk.Button(
    w_advysory,
    image=img_Services_Advysory_Register_button,
    background="#f0f0f0",
    activebackground="#f0f0f0",
    borderwidth=0,
    highlightthickness=0,
    relief="flat",
    overrelief="flat",
    padx=0,
    pady=0,
    command=register_advisory_service,
)

b_Services_Advysory_Register.place(
    x=630,
    y=632
)

# - Book

i_Services_Book_background = Image.open(
    asset_path("Fj Software/Interfaz/Services/1x/Service_Book_background.png")
)
i_Services_Book_background = i_Services_Book_background.resize((874, 767))
img_Services_Book_background = ImageTk.PhotoImage(
    i_Services_Book_background,
    master=w_book
)
l_Services_Book_background = ttk.Label(
    w_book,
    image=img_Services_Book_background,
    style="HomeBackground.TLabel"
)
l_Services_Book_background.image = img_Services_Book_background
l_Services_Book_background.place(x=-2, y=0)

e_Services_Book_name = ttk.Entry(
    w_book,
    width=20,
    font=("Segoe UI Semibold", 12)
)
e_Services_Book_name.place(x=527, y=301)

e_Services_Book_fee = ttk.Entry(
    w_book,
    width=20,
    font=("Segoe UI Semibold", 12)
)
e_Services_Book_fee.place(x=754, y=301)

t_Services_Book_Description = tk.Text(
    w_book,
    wrap="word",
    font=("Segoe UI Semibold", 12)
)
t_Services_Book_Description.place(
    x=525,
    y=378,
    width=175,
    height=62,
)

v_Book_Availability = tk.BooleanVar(master=w_book, value=True)
ch_Book_Availability = ttk.Checkbutton(
    w_book,
    variable=v_Book_Availability,
)
ch_Book_Availability.place(x=757, y=384)

e_Services_Book_capacity = ttk.Entry(
    w_book,
    width=20,
    font=("Segoe UI Semibold", 12)
)
e_Services_Book_capacity.place(x=527, y=530)

e_Services_Book_location = ttk.Entry(
    w_book,
    width=20,
    font=("Segoe UI Semibold", 12)
)
e_Services_Book_location.place(x=754, y=530)

i_Services_Book_Register_button = Image.open(
    asset_path("Fj Software/Interfaz/Services/1x/Service_Book_Register_button.png")
)
i_Services_Book_Register_button = i_Services_Book_Register_button.resize(
    (264, 55)
)
img_Services_Book_Register_button = ImageTk.PhotoImage(
    i_Services_Book_Register_button,
    master=w_book
)
b_Services_Book_Register = tk.Button(
    w_book,
    image=img_Services_Book_Register_button,
    background="#f0f0f0",
    activebackground="#f0f0f0",
    borderwidth=0,
    highlightthickness=0,
    relief="flat",
    overrelief="flat",
    padx=0,
    pady=0,
    command=register_room_service,
)
b_Services_Book_Register.place(x=630, y=632)

# - Rent

i_Services_Rent_background = Image.open(
    asset_path("Fj Software/Interfaz/Services/1x/Service_Rent_background.png")
)
i_Services_Rent_background = i_Services_Rent_background.resize((874, 767))
img_Services_Rent_background = ImageTk.PhotoImage(
    i_Services_Rent_background,
    master=w_rent
)
l_Services_Rent_background = ttk.Label(
    w_rent,
    image=img_Services_Rent_background,
    style="HomeBackground.TLabel"
)
l_Services_Rent_background.image = img_Services_Rent_background
l_Services_Rent_background.place(x=-2, y=0)

e_Services_Rent_name = ttk.Entry(
    w_rent,
    width=20,
    font=("Segoe UI Semibold", 12)
)
e_Services_Rent_name.place(x=527, y=251)

e_Services_Rent_fee = ttk.Entry(
    w_rent,
    width=20,
    font=("Segoe UI Semibold", 12)
)
e_Services_Rent_fee.place(x=754, y=251)

t_Services_Rent_Description = tk.Text(
    w_rent,
    wrap="word",
    font=("Segoe UI Semibold", 12)
)
t_Services_Rent_Description.place(
    x=525,
    y=328,
    width=175,
    height=62,
)

v_Rent_Availability = tk.BooleanVar(master=w_rent, value=True)
ch_Rent_Availability = ttk.Checkbutton(
    w_rent,
    variable=v_Rent_Availability,
)
ch_Rent_Availability.place(x=757, y=334)

cb_Services_Rent_equipment_type = ttk.Combobox(
    w_rent,
    values=(
        "Servers",
        "Laptops",
        "Desktop Computers",
        "Monitors",
        "Projectors",
        "Printers",
        "Cameras",
        "Audio Equipment",
        "Networking Equipment",
        "Tablets",
    ),
    state="readonly",
    width=20,
    font=("Segoe UI Semibold", 12),
)
cb_Services_Rent_equipment_type.place(x=527, y=477)

cb_Services_Rent_brand = ttk.Combobox(
    w_rent,
    values=(
        "Dell",
        "HP",
        "Lenovo",
        "Apple",
        "ASUS",
        "Acer",
        "Microsoft",
        "Samsung",
        "Canon",
        "Epson",
        "Sony",
        "Cisco",
        "HPE",
        "IBM",
        "Other",
    ),
    state="readonly",
    width=20,
    font=("Segoe UI Semibold", 12),
)
cb_Services_Rent_brand.place(x=754, y=477)

e_Services_Rent_actual_stock = ttk.Entry(
    w_rent,
    width=20,
    font=("Segoe UI Semibold", 12)
)
e_Services_Rent_actual_stock.place(x=527, y=560)

i_Services_Rent_Register_button = Image.open(
    asset_path("Fj Software/Interfaz/Services/1x/Service_Rent_Register_button.png")
)
i_Services_Rent_Register_button = i_Services_Rent_Register_button.resize(
    (264, 55)
)
img_Services_Rent_Register_button = ImageTk.PhotoImage(
    i_Services_Rent_Register_button,
    master=w_rent
)
b_Services_Rent_Register = tk.Button(
    w_rent,
    image=img_Services_Rent_Register_button,
    background="#f0f0f0",
    activebackground="#f0f0f0",
    borderwidth=0,
    highlightthickness=0,
    relief="flat",
    overrelief="flat",
    padx=0,
    pady=0,
    command=register_rental_service,
)
b_Services_Rent_Register.place(x=630, y=632)


# - Search for a Service

i_Services_Search_background = Image.open(
    asset_path("Fj Software/Interfaz/Services/1x/Services_Search_background.png")
)
i_Services_Search_background = i_Services_Search_background.resize((640, 219))
img_Services_Search_background = ImageTk.PhotoImage(
    i_Services_Search_background,
    master=w_services_search
)
l_Services_Search_background = ttk.Label(
    w_services_search,
    image=img_Services_Search_background,
    style="HomeBackground.TLabel"
)
l_Services_Search_background.image = img_Services_Search_background
l_Services_Search_background.place(x=0, y=0)

i_Services_Search_ID = Image.open(
    asset_path("Fj Software/Interfaz/Services/1x/Services_Search_ID.png")
)
i_Services_Search_ID = i_Services_Search_ID.resize((296, 86))
img_Services_Search_ID = ImageTk.PhotoImage(
    i_Services_Search_ID,
    master=w_services_search
)
b_Services_Search_ID = tk.Button(
    w_services_search,
    image=img_Services_Search_ID,
    background="#0430ba",
    activebackground="#0430ba",
    borderwidth=0,
    highlightthickness=0,
    relief="flat",
    overrelief="flat",
    padx=0,
    pady=0,
    command=lambda: select_service_search_type("id"),
)
b_Services_Search_ID.place(x=23, y=87)

i_Services_Search_name = Image.open(
    asset_path("Fj Software/Interfaz/Services/1x/Services_Search_name.png")
)
i_Services_Search_name = i_Services_Search_name.resize((296, 86))
img_Services_Search_name = ImageTk.PhotoImage(
    i_Services_Search_name,
    master=w_services_search
)
b_Services_Search_name = tk.Button(
    w_services_search,
    image=img_Services_Search_name,
    background="#0430ba",
    activebackground="#0430ba",
    borderwidth=0,
    highlightthickness=0,
    relief="flat",
    overrelief="flat",
    padx=0,
    pady=0,
    command=lambda: select_service_search_type("name"),
)
b_Services_Search_name.place(x=347, y=87)

i_Services_Search_Search_button = Image.open(
    asset_path("Fj Software/Interfaz/Services/1x/Services_Search_Search_button.png")
)
img_Services_Search_Search_button = ImageTk.PhotoImage(
    i_Services_Search_Search_button,
    master=w_services_search
)
b_Services_Search_Search = tk.Button(
    w_services_search,
    image=img_Services_Search_Search_button,
    background="#f0f0f0",
    activebackground="#f0f0f0",
    borderwidth=0,
    highlightthickness=0,
    relief="flat",
    overrelief="flat",
    padx=0,
    pady=0,
    command=search_services,
)
b_Services_Search_Search.place(x=192, y=345)

l_service_search = ttk.Label(
    w_services_search,
    text="Introduce the service ID",
    style="TitleBlue.TLabel"
)
l_service_search.place(x=117, y=234)

e_service_search = ttk.Entry(
    w_services_search,
    width=30,
    font=("Segoe UI Semibold", 12)
)
e_service_search.place(x=179, y=308, height=30)

# - Delete a Service

i_Services_Delete_background = Image.open(
    asset_path("Fj Software/Interfaz/Services/1x/Services_Delete_background.png")
)
i_Services_Delete_background = i_Services_Delete_background.resize((640, 168))
img_Services_Delete_background = ImageTk.PhotoImage(
    i_Services_Delete_background,
    master=w_services_delete
)
l_Services_Delete_background = ttk.Label(
    w_services_delete,
    image=img_Services_Delete_background,
    style="HomeBackground.TLabel"
)
l_Services_Delete_background.image = img_Services_Delete_background
l_Services_Delete_background.place(x=0, y=0)

i_Services_Delete_Delete_button = Image.open(
    asset_path("Fj Software/Interfaz/Services/1x/Services_Delete_Delete_button.png")
)
img_Services_Delete_Delete_button = ImageTk.PhotoImage(
    i_Services_Delete_Delete_button,
    master=w_services_delete
)
b_Services_Delete_Delete = tk.Button(
    w_services_delete,
    image=img_Services_Delete_Delete_button,
    background="#f0f0f0",
    activebackground="#f0f0f0",
    borderwidth=0,
    highlightthickness=0,
    relief="flat",
    overrelief="flat",
    padx=0,
    pady=0,
    command=delete_service,
)
b_Services_Delete_Delete.place(x=227, y=351)

l_service_delete = ttk.Label(
    w_services_delete,
    text="Introduce the Service ID",
    style="TitleBlue.TLabel"
)
l_service_delete.place(x=117, y=220)

e_service_delete = ttk.Entry(
    w_services_delete,
    width=30,
    font=("Segoe UI Semibold", 12)
)
e_service_delete.place(x=179, y=284)

# --- Reservations

i_Reservations_background = Image.open(
    asset_path("Fj Software/Interfaz/Reservations/1x/Reservations_background.png")
)
i_Reservations_background = i_Reservations_background.resize((939, 904))
img_Reservations_background = ImageTk.PhotoImage(
    i_Reservations_background,
    master=f_reservations
)
l_Reservations_background = ttk.Label(
    f_reservations,
    image=img_Reservations_background,
    style="HomeBackground.TLabel"
)
l_Reservations_background.image = img_Reservations_background
l_Reservations_background.place(x=-15, y=13)

tv_reservations = ttk.Treeview(
    f_reservations,
    columns=(
        "id",
        "customer",
        "service",
        "date",
        "customer_phone",
        "service_description",
    ),
    show="headings",
    style="Costumer.Treeview",
)

tv_reservations.heading("id", text="ID")
tv_reservations.heading("customer", text="Customer")
tv_reservations.heading("service", text="Service")
tv_reservations.heading("date", text="Date")
tv_reservations.heading("customer_phone", text="Customer Phone Number")
tv_reservations.heading("service_description", text="Service Description")

tv_reservations.column("id", width=70, minwidth=60, anchor="center", stretch=False)
tv_reservations.column("customer", width=100, minwidth=85, anchor="w", stretch=False)
tv_reservations.column("service", width=105, minwidth=85, anchor="w", stretch=False)
tv_reservations.column("date", width=110, minwidth=100, anchor="center", stretch=False)
tv_reservations.column(
    "customer_phone",
    width=180,
    minwidth=110,
    anchor="center",
    stretch=False,
)
tv_reservations.column(
    "service_description",
    width=258,
    minwidth=130,
    anchor="w",
    stretch=False,
)

tv_reservations.place(
    x=409,
    y=144,
    width=823,
    height=783,
)

e_reservations_customer = ttk.Entry(
    f_reservations,
    font=("Segoe UI Semibold", 12),
)
e_reservations_customer.place(x=42, y=270, width=208, height=26)

e_reservations_service = ttk.Entry(
    f_reservations,
    font=("Segoe UI Semibold", 12),
)
e_reservations_service.place(x=38, y=350, width=208, height=26)

e_reservations_date_part_1 = ttk.Entry(
    f_reservations,
    font=("Segoe UI Semibold", 12),
)
e_reservations_date_part_1.place(x=38, y=430, width=29, height=26)

e_reservations_date_part_2 = ttk.Entry(
    f_reservations,
    font=("Segoe UI Semibold", 12),
)
e_reservations_date_part_2.place(x=77, y=430, width=29, height=26)

e_reservations_date_part_3 = ttk.Entry(
    f_reservations,
    font=("Segoe UI Semibold", 12),
)
e_reservations_date_part_3.place(x=117, y=430, width=29, height=26)

e_reservations_duration = ttk.Entry(
    f_reservations,
    font=("Segoe UI Semibold", 12),
)
e_reservations_duration.place(x=38, y=510, width=208, height=26)

i_Reservations_Register_button = Image.open(
    asset_path("Fj Software/Interfaz/Reservations/1x/Reservations_Register_Buttons.png")
)
img_Reservations_Register_button = ImageTk.PhotoImage(
    i_Reservations_Register_button,
    master=f_reservations,
)
b_Reservations_Register = tk.Button(
    f_reservations,
    image=img_Reservations_Register_button,
    background="#026abb",
    activebackground="#026abb",
    borderwidth=0,
    highlightthickness=0,
    relief="flat",
    overrelief="flat",
    padx=0,
    pady=0,
    command=register_reservation,
)
b_Reservations_Register.place(x=75, y=548)

e_reservations_search_id = ttk.Entry(
    f_reservations,
    font=("Segoe UI Semibold", 12),
)
e_reservations_search_id.place(x=63, y=763, width=206, height=26)

i_Reservations_Search_button = Image.open(
    asset_path("Fj Software/Interfaz/Reservations/1x/Reservations_Search_button.png")
)
img_Reservations_Search_button = ImageTk.PhotoImage(
    i_Reservations_Search_button,
    master=f_reservations,
)
b_Reservations_Search = tk.Button(
    f_reservations,
    image=img_Reservations_Search_button,
    background="#0430ba",
    activebackground="#0430ba",
    borderwidth=0,
    highlightthickness=0,
    relief="flat",
    overrelief="flat",
    padx=0,
    pady=0,
    command=search_reservations,
)
b_Reservations_Search.place(x=35, y=831)

w_login.bind_all("<KeyPress>", add_test_data_hotkey)
n_main.bind("<<NotebookTabChanged>>", reset_inactive_search_results)

w_login.mainloop()