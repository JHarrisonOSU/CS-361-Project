##########################################################################################################
# Name: Johnathan Harrison
# OSU Email: harrijo9@oregonstate.edu
# Course: CS361
# Assignment: Term Project
##########################################################################################################

import tkinter as tk
import requests
import zmq
import json
import threading
from tkinter import ttk, Frame, font, messagebox, simpledialog
from random import randint, uniform
from datetime import datetime, timedelta
from typing import Any, Callable
from PIL import Image, ImageTk


#############################################################################################################
# ZMQ Socket Setup
#############################################################################################################

# First create a Context object. This will contain all ZMQ sockets in one process.
context = zmq.Context()
# Next create a socket of type REQ (REQUEST)
socket = context.socket(zmq.REQ)
# Next connect the socket to the server's endpoint
# (server @ localhost port 5555, in this case)
socket.connect("tcp://localhost:5555")


#############################################################################################################
# Globals
#############################################################################################################

active_user = ""
key = "5bb6052bd308f2b5"
medication_data = []

try:
    # Try to open the file and load the data
    with open("user_data.txt", "r") as file:
        # Load encrpyed save data, send request for decode
        encrypted_str = file.read()
        print(encrypted_str)
        decrpyt_req = (encrypted_str, key, "decode")
        print(decrpyt_req)
        socket.send_pyobj(decrpyt_req)

        # Convert decrypted save data back to dictionary, load into program
        decrypted_str = socket.recv_string()
        users = json.loads(decrypted_str)

except FileNotFoundError:
    # If the file does not exist, create an empty dictionary
    users = {}

    # Optionally, write the empty dictionary to the file
    with open("user_data.txt", "w") as file:
        json.dump(users, file)


#############################################################################################################
# Event Driven Functions
#############################################################################################################

###########################################
# Generic
###########################################


# Function to save data on app closure
def on_close():
    with open("user_data.txt", "w") as file:
        save_medication_data()
        data_str = json.dumps(users)
        encrypt_req = (data_str, key, "encode")
        socket.send_pyobj(encrypt_req)

        encrypted_str = socket.recv_string()
        file.write(encrypted_str)

    # Destroy the window after saving the data
    root.destroy()


# Function to center a frame within the screen
def center_app(frame):
    frame.update_idletasks()
    width = frame.winfo_width()
    height = frame.winfo_height()
    screen_width = frame.winfo_screenwidth()
    screen_height = frame.winfo_screenheight()

    # Calculate position x, y
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    root.geometry(f"{width}x{height}+{x}+{y}")


# Function to close a particular frame, called by add_entry and update_entry_submit
def close_window(entry_frame):
    entry_frame.destroy()


# Function to spawn data entry popup window
def open_entry_window(
    title: str, fields: dict[str:Any], submit_action: Callable, container_frame: Frame
):
    # Create a new frame popup form to allow user's to enter/edit data
    entry_frame = ttk.Frame(container_frame, style="Popup.TFrame")
    entry_frame.place(
        relx=0.5,
        rely=0.5,
        anchor="center",  # Position it to center of main window (not sidebar)
    )
    entry_frame["padding"] = (10, 10)

    # Create a title for the popup form
    window_label = ttk.Label(entry_frame, text=title, style="PopupTitle.TLabel")
    window_label.grid(row=0, column=0, columnspan=2, padx=5, pady=10)

    # Populate the form fields and values via iterating through the passed dict
    entries = {}
    for i, (field, value) in enumerate(fields.items()):
        label = ttk.Label(entry_frame, text=f"{field}:")
        entry = ttk.Entry(entry_frame)
        entry.insert(0, value)
        entries[field] = entry

        # Place them into a tk grid
        label.grid(row=i + 1, column=0, padx=5, pady=5, sticky="w")
        entry.grid(row=i + 1, column=1, padx=5, pady=5)

    # Create cancel and submit buttons, attaching the appropriate action command
    submit_button = ttk.Button(
        entry_frame, text="Submit", command=lambda: submit_action(entry_frame, entries)
    )
    cancel_button = ttk.Button(
        entry_frame, text="Cancel", command=lambda: close_window(entry_frame)
    )

    # Position the buttons in the grid
    cancel_button.grid(row=len(fields) + 1, column=1, padx=30, pady=10)
    submit_button.grid(row=len(fields) + 1, column=0, padx=5, pady=10)


###########################################
# Login
###########################################


# Function to verify login credentials
def verify_login(username, password):
    global active_user
    # Handle invalid login/no users errors
    if not user_dropdown.get():
        messagebox.showerror(
            "Login Failed", f"You must first create a user account to login."
        )
        return

    if users[username]["password"] == password:
        # messagebox.showinfo("Login Successful", "You are logged in!")
        active_user = username
        load_medication_data()
        login_frame.place_forget()
    else:
        messagebox.showerror("Login Failed", f"Incorrect password for {username}")


# Function to update the user dropdown
def update_user_dropdown(new_user=None):
    user_dropdown["values"] = list(users.keys())
    if new_user:
        user_dropdown.set(new_user)


# Function to handle user creation submission
def submit_create_user(entry_frame, entries):
    username = entries["Username"].get()
    password = entries["Password"].get()

    user_valid = username.isalpha() and 3 <= len(username) <= 20
    pass_valid = 6 <= len(password) <= 20

    # Validate login details
    if username in users:
        messagebox.showerror("Error", "Username already exists!")
        return
    elif not username or not password:
        messagebox.showerror("Error", "Missing username or password!")
        return
    elif not user_valid:
        messagebox.showerror(
            "Error",
            "Invalid username. Can't contain spaces or numbers, and should be 3-20 characters long.",
        )
        return
    elif not pass_valid:
        messagebox.showerror("Error", "Invalid password. Must be 6-20 characters long.")
        return

    # Add user to user database
    users[username] = {"password": password}
    messagebox.showinfo("Success", "User created successfully!")

    # Fix dropdown if currently empty
    if not user_dropdown.get():
        update_user_dropdown(new_user=username)
    else:
        update_user_dropdown()

    close_window(entry_frame)


# Action for the new user button
def show_create_user_popup():
    fields = {"Username": "", "Password": ""}
    open_entry_window("Create User", fields, submit_create_user, main_frame)


# Function to create a login frame
def create_login_frame(parent):
    # Create the frame as a child of the parent frame
    login_frame = tk.Frame(parent)

    # Application title
    title_label = tk.Label(login_frame, text="MedList", font=("Arial", 24, "italic"))
    title_label.pack(pady=10)

    # User selection dropdown
    user_label = tk.Label(login_frame, text="Select User:")
    user_label.pack()
    user_dropdown = ttk.Combobox(login_frame)
    user_dropdown["values"] = list(users.keys())
    if users:
        first_user = next(iter(users))  # Get the first key in the dictionary
        user_dropdown.set(first_user)  # Set the first user as the current value
    user_dropdown.pack(pady=5)

    # Password entry
    password_label = tk.Label(login_frame, text="Password:")
    password_label.pack()
    password_entry = tk.Entry(login_frame, show="*")
    password_entry.pack(pady=5)

    login_button = tk.Button(
        login_frame,
        text="Login",
        command=lambda: verify_login(user_dropdown.get(), password_entry.get()),
    )
    login_button.pack(pady=10)

    # Create new user button
    new_user_button = tk.Button(
        login_frame, text="Create New User", command=show_create_user_popup
    )
    new_user_button.pack(pady=10)

    # Place the login frame inside the parent frame
    login_frame.place(in_=parent, x=0, y=0, relwidth=1, relheight=1)

    return login_frame, user_dropdown


###########################################
# Sidebar
###########################################


# Highlights label on mouse enter if inactive
def on_hover_enter(event):
    if event.widget != active_label:
        event.widget.configure(style="Hover.TLabel")


# Restores previous label highlight on mouse exit
def on_hover_leave(event):
    if event.widget != active_label:
        event.widget.configure(style="Sidebar.TLabel")


# Sets a label as active (always highlighted)
def set_active_label(label):
    global active_label
    if active_label:
        active_label.configure(style="Sidebar.TLabel")
    active_label = label
    active_label.configure(style="Active.TLabel")


def switch_to_home():
    # TODO: Implement the "Home" button functionality here
    pass


def switch_to_schedule():
    # TODO Implement the "View 2" button functionality here
    pass


def switch_to_history():
    # TODO Implement the "View 3" button functionality here
    pass


###########################################
# Medication Table - Loading and Sorting
###########################################


# Function to load medication data from user data dictionary
def load_medication_data():
    global medication_data
    global active_user
    # Assuming user_data is your user data dictionary
    if active_user in users and "medication_data" in users[active_user]:
        medication_data = users[active_user]["medication_data"]

        # Populate the table with data from medication_data
        for data_row in medication_data:
            tree.insert("", "end", values=data_row)


def save_medication_data():
    global medication_data
    global active_user

    for item in tree.get_children():
        data_row = [
            tree.item(item, "values")[col] for col in range(len(tree["columns"]))
        ]
        medication_data.append(data_row)

    users[active_user]["medication_data"] = medication_data


# Sorting function for table
def sort_by_column(column_name):
    data = [(tree.set(item, column_name), item) for item in tree.get_children("")]
    data.sort()
    for i, item in enumerate(data):
        tree.move(item[1], "", i)


###########################################
# Medication Table - Modifying
###########################################


# Function to call open_entry_window in add mode
def add_new_medication():
    # Fields for a new medication entry
    fields = {
        "Medication": "",
        "Dosage": "",
        "Frequency": "",
        "Start Date": "",
        "End Date": "",
    }

    open_entry_window(
        "Add New Medication",
        fields,
        lambda ef, e: add_entry_submit(ef, e),
        meds_frame,
    )


# Function to call open_entry_window in update mode
def edit_selected_medication():
    selected_item = tree.selection()
    if not selected_item:
        return  # No item selected

    values = tree.item(selected_item, "values")
    fields = {
        "Medication": values[1],
        "Dosage": values[2],
        "Frequency": values[3],
        "Start Date": values[4],
        "End Date": values[5],
    }

    open_entry_window(
        "Update Medication",
        fields,
        lambda ef, e: update_entry_submit(ef, e),
        meds_frame,
    )


# Function to spawn data entry popup window
def open_entry_window(
    title: str, fields: dict[str:Any], submit_action: Callable, container_frame: Frame
):
    # Create a new frame popup form to allow user's to enter/edit data
    entry_frame = ttk.Frame(container_frame, style="Popup.TFrame")
    entry_frame.place(
        relx=0.5,
        rely=0.5,
        anchor="center",  # Position it to center of main window (not sidebar)
    )
    entry_frame["padding"] = (10, 10)

    # Create a title for the popup form
    window_label = ttk.Label(entry_frame, text=title, style="PopupTitle.TLabel")
    window_label.grid(row=0, column=0, columnspan=2, padx=5, pady=10)

    # Populate the form fields and values via iterating through the passed dict
    entries = {}
    for i, (field, value) in enumerate(fields.items()):
        label = ttk.Label(entry_frame, text=f"{field}:")
        entry = ttk.Entry(entry_frame)
        entry.insert(0, value)
        entries[field] = entry

        # Place them into a tk grid
        label.grid(row=i + 1, column=0, padx=5, pady=5, sticky="w")
        entry.grid(row=i + 1, column=1, padx=5, pady=5)

    # Create cancel and submit buttons, attaching the appropriate action command
    submit_button = ttk.Button(
        entry_frame, text="Submit", command=lambda: submit_action(entry_frame, entries)
    )
    cancel_button = ttk.Button(
        entry_frame, text="Cancel", command=lambda: close_window(entry_frame)
    )

    # Position the buttons in the grid
    cancel_button.grid(row=len(fields) + 1, column=1, padx=30, pady=10)
    submit_button.grid(row=len(fields) + 1, column=0, padx=5, pady=10)


# Function to add a new row to table, called by open_entry_window()
def add_entry_submit(entry_frame, entries):
    medication = entries["Medication"].get()
    dosage = entries["Dosage"].get()
    frequency = entries["Frequency"].get()
    start_date = entries["Start Date"].get()
    end_date = entries["End Date"].get()

    tree.insert(
        "", "end", values=["", medication, dosage, frequency, start_date, end_date]
    )
    close_window(entry_frame)


# Function to update a row's data, called by open_entry_window on submit
def update_entry_submit(entry_frame, entries):
    selected_item = tree.selection()
    if not selected_item:
        return  # No item selected

    medication = entries["Medication"].get()
    dosage = entries["Dosage"].get()
    frequency = entries["Frequency"].get()
    start_date = entries["Start Date"].get()
    end_date = entries["End Date"].get()

    tree.item(
        selected_item, values=["", medication, dosage, frequency, start_date, end_date]
    )
    close_window(entry_frame)


#############################################################################################################
# Main Window
#############################################################################################################

root = tk.Tk()
root.title("MedList")
root.geometry("1200x600")

# Set a minimum window size
root.minsize(width=1200, height=600)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

root.bind("<Map>", lambda event: center_app(root))
root.protocol("WM_DELETE_WINDOW", on_close)

# Create a main frame for the table and sidebar
main_frame = ttk.Frame(root)
main_frame.pack(fill="both", expand=True)


#############################################################################################################
# Sidebar
#############################################################################################################


# Create the sidebar frame
sidebar_frame = ttk.Frame(main_frame, width=200, style="Sidebar.TFrame")


# Add labels as buttons in the sidebar for navigation
app_name_label = ttk.Label(sidebar_frame, text="MedList", style="AppName.TLabel")
home_button = ttk.Label(sidebar_frame, text="Home", style="Sidebar.TLabel")
schedule_button = ttk.Label(
    sidebar_frame, text="Medication Schedule", style="Sidebar.TLabel"
)
history_button = ttk.Label(
    sidebar_frame, text="Medication History", style="Sidebar.TLabel"
)

# Pack the sidebar elements into the grid
app_name_label.grid(row=0, padx=0, pady=0)
home_button.grid(row=1, padx=10, pady=1, sticky="w")
schedule_button.grid(row=2, padx=10, pady=1, sticky="w")
history_button.grid(row=3, padx=10, pady=1, sticky="w")

# Bind events for mouse hover actions
home_button.bind("<Enter>", on_hover_enter)
schedule_button.bind("<Enter>", on_hover_enter)
history_button.bind("<Enter>", on_hover_enter)

home_button.bind("<Leave>", on_hover_leave)
schedule_button.bind("<Leave>", on_hover_leave)
history_button.bind("<Leave>", on_hover_leave)

# Style for the sidebar frame
ttk.Style().configure("Sidebar.TFrame", background="#333")
# Sidebar header style
ttk.Style().configure(
    "AppName.TLabel",
    font=("Arial", 35, "italic", "bold"),
    background="#333",
    foreground="white",
    width=10,
    anchor="center",
)
# Default style for sidebar labels
ttk.Style().configure(
    "Sidebar.TLabel",
    font=("Helvetica", 15, "bold"),
    padding=(10, 5, 40, 5),
    background="#333",
    foreground="white",
    width=20,
    anchor="w",
)
# Style for sidebar labels on hover
ttk.Style().configure(
    "Hover.TLabel",
    font=("Helvetica", 15, "bold"),
    padding=(10, 5, 40, 5),
    background="#444",
    foreground="white",
    width=20,
    anchor="w",
)
# Active page sidebar label style
ttk.Style().configure(
    "Active.TLabel",
    font=("Helvetica", 15, "bold"),
    padding=(10, 5, 40, 5),
    background="#444",  # Active label background color
    foreground="white",  # Active label text color
    width=20,
    anchor="w",
)

# Initialize the active label to the home_button
active_label = home_button
home_button.configure(style="Active.TLabel")

# Pack the sidebar into the main frame
sidebar_frame.pack(side="left", fill="y")

#############################################################################################################
# Medications View (Home)
#############################################################################################################
# Create a frame for the home page (Medication list) and let it fill the remaining space
meds_frame = ttk.Frame(main_frame, style="MedsFrame.TFrame")
ttk.Style().configure("MedsFrame.TFrame", background="white")

# Use the pack geometry manager to position meds frame within main_frame
meds_frame.pack(side="left", fill="both", expand=True)


#############################################################################################################
# Table Title + Add button
#############################################################################################################

# Create a frame above the table to hold title + button
table_title_frame = ttk.Frame(meds_frame, padding=(10, 5), style="TableTitle.TFrame")
table_title_frame.pack(side="top", fill="x")

# Create a label for titling the table
table_title = ttk.Label(table_title_frame, text="Medications", style="Title.TLabel")

ttk.Style().configure("TableTitle.TFrame", background="white")
ttk.Style().configure(
    "Title.TLabel",
    font=("Helvetica", 23, "bold"),
    padding=(5, 5, 40, 5),
    background="white",
    foreground="black",  # Active label text color
    width=20,
    anchor="w",
)

table_title.pack(side="left", fill="none", expand=False)

# Fields for a new medication entry
new_medication_fields = {
    "Medication": "",
    "Dosage": "",
    "Frequency": "",
    "Start Date": "",
    "End Date": "",
}

# Create a button for adding an entry
add_entry_button = ttk.Button(
    table_title_frame,
    text="Add Medication +",
    style="Add.TButton",
    command=add_new_medication,
    padding=(50, 5),
)

# Style the add button
ttk.Style().configure("Add.TButton", font=("Helvetica", 15, "bold"), padding=(50, 5))

add_entry_button.pack(side="right", fill="none")

#############################################################################################################
# Add/Edit/Delete Popups
#############################################################################################################

# Define a custom style for the popup frames
ttk.Style().configure("Popup.TFrame", borderwidth=5, relief="ridge")

# Design a title style for the popup frames

ttk.Style().configure(
    "PopupTitle.TLabel",
    font=("Helvetica", 23, "bold"),
    padding=(10, 5, 10, 5),
    foreground="black",  # Active label text color
    width=20,
    anchor="center",
)

# Design a field label style for the popup frames

#############################################################################################################
# Table
#############################################################################################################


# Define a generic sorting function
def sort_by_column(column_name):
    data = [(tree.set(item, column_name), item) for item in tree.get_children("")]
    data.sort()
    for i, item in enumerate(data):
        tree.move(item[1], "", i)


# Create a frame to contain the treeview and scrollbar
tree_frame = ttk.Frame(meds_frame, style="MedsTable.TFrame", padding=(10, 0, 10, 0))
tree_frame.pack(side="top", fill="both")


ttk.Style().configure("MedsTable.TFrame", background="white")


# Create a Treeview widget (a table)
tree = ttk.Treeview(
    tree_frame,
    columns=("Select", "Medication", "Dosage", "Frequency", "Start Date", "End Date"),
    show="headings",
    selectmode="extended",
    height=15,
    style="Treeview",
)

# Configure the style for the treeview
ttk.Style().configure(
    "Treeview",
    background="white",
    fieldbackground="white",
    foreground="black",
    rowheight=30,
    font=("Helvetica", 12),
    anchor="w",
    selectbackground="#444",
    padding=(5, 0, 5, 0),
)

# Style selected rows
ttk.Style().map(
    "Treeview", background=[("selected", "#BFBFBF")], foreground=[("selected", "black")]
)

# Configure the headers style
ttk.Style().configure(
    "Treeview.Heading",
    background="white",
    foreground="black",
    font=("Helvetica", 14, "bold"),
    padding=(5, 5),
)

# Define column headers
tree.heading("Select", text="", anchor="w")
tree.heading("Medication", text="Medication", anchor="w")
tree.heading("Dosage", text="Dosage", anchor="w")
tree.heading("Frequency", text="Frequency", anchor="w")
tree.heading("Start Date", text="Start Date", anchor="w")
tree.heading("End Date", text="End Date", anchor="w")

# Configure column widthsmin
tree.column("Select", width=30, minwidth=30, stretch=False)
tree.column("Medication", width=150, minwidth=150)
tree.column("Dosage", width=100, minwidth=100)
tree.column("Frequency", width=100, minwidth=100)
tree.column("Start Date", width=100, minwidth=100)
tree.column("End Date", width=100, minwidth=100)

# Create a vertical scrollbar and attach it to the table
vsb = ttk.Scrollbar(
    tree_frame,
    orient="vertical",
    command=tree.yview,
    style="Custom.Vertical.TScrollbar",
)
tree.configure(yscrollcommand=vsb.set)


# Associate sorting functions with column headers
tree.heading("Medication", command=lambda: sort_by_column("Medication"))
tree.heading("Dosage", command=lambda: sort_by_column("Dosage"))
tree.heading("Frequency", command=lambda: sort_by_column("Frequency"))
tree.heading("Start Date", command=lambda: sort_by_column("Start Date"))
tree.heading("End Date", command=lambda: sort_by_column("End Date"))

# Pack the treeview and scrollbar
tree.pack(side="left", fill="both", expand=True)
vsb.pack(side="right", fill="both")

#############################################################################################################
# Bottom Buttons
#############################################################################################################


# Create "Edit Selected Medication" button
table_bottom_frame = ttk.Frame(meds_frame, padding=(15, 5))
table_bottom_frame.pack(side="top", fill="x")

edit_button = ttk.Button(
    table_bottom_frame,
    text="Edit Selected Medication",
    command=edit_selected_medication,
    style="Edit.TButton",
)


ttk.Style().configure("Edit.TButton", font=("Helvetica", 14, "bold"), padding=(50, 5))
edit_button.pack(side="left", fill="none")


#############################################################################################################
# Sample Data Generation
#############################################################################################################


# def int_to_base26(num):
#     string = ""
#     while num > 0:
#         num, remainder = divmod(num - 1, 26)
#         string = chr(65 + remainder) + string
#     return string


# # Function to simulate data entry
# def generate_valid_entry(index):
#     medication = f"Medication {int_to_base26(index)}"
#     dosage = f"{uniform(0.01, 500):.1f} mg"
#     frequency = f"{randint(1, 5)}x / Day"

#     start_date = datetime(randint(2022, 2022), randint(1, 12), randint(1, 28))
#     end_date = start_date + timedelta(days=randint(1, 365))  # Up to 1 year apart

#     return [
#         "",
#         medication,
#         dosage,
#         frequency,
#         start_date.strftime("%Y/%m/%d"),
#         end_date.strftime("%Y/%m/%d"),
#     ]


# # Insert x generated entries with specified formatting
# for i in range(1, 51):  # Starting from 1 to avoid empty medication name
#     entry_data = generate_valid_entry(i)
#     tree.insert("", "end", values=entry_data, tags=("editable",))


#############################################################################################################
# Login Frame
#############################################################################################################

login_frame, user_dropdown = create_login_frame(main_frame)

# Start with login frame
login_frame.tkraise()

#############################################################################################################
# Main Loop
#############################################################################################################
root.mainloop()
