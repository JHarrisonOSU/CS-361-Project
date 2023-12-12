##########################################################################################################
# Name: Johnathan Harrison
# OSU Email: harrijo9@oregonstate.edu
# Course: CS361
# Assignment: Term Project
##########################################################################################################

import requests
import re
import zmq
import json
import tkinter as tk
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

# Get current date and next day, format to strings
current_date = datetime.today()
current_date_str = current_date.strftime("%d/%m/%Y")
next_day = current_date + timedelta(days=1)
next_day_str = next_day.strftime("%d/%m/%Y")

try:
    # Try to open the file and load the data
    with open("user_data.txt", "r") as file:
        # Load encrpyed save data, send request for decode
        encrypted_str = file.read()

        if encrypted_str != "":
            decrpyt_req = (encrypted_str, key, "decode")
            socket.send_pyobj(decrpyt_req)

            # Convert decrypted save data back to dictionary, load into program
            decrypted_str = socket.recv_string()
            users = json.loads(decrypted_str)
        else:
            users = {}
            # Optionally, write the empty dictionary to the file
            with open("user_data.txt", "w") as file:
                json.dump(users, file)

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
# Generic Functions
###########################################


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
def close_window(frame):
    frame.destroy()


###########################################
# Popup windows
###########################################


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

    first_field_set = False  # Flag to check if the first field is set

    # Populate the form fields and values via iterating through the passed dict
    entries = {}
    num_columns = 2
    for i, (field, value) in enumerate(fields.items()):
        if field in ["Dosage Unit", "Frequency Options"]:
            num_columns = 3
            combobox = ttk.Combobox(entry_frame, width=10, state="readonly")
            combobox.grid(row=i, column=2, padx=0, pady=5, sticky="w")
            if field == "Dosage Unit":
                combobox["values"] = ["mg", "mcg", "mL", "drops"]
            else:  # field == "Frequency Option"
                combobox["values"] = ["Daily", "Weekly", "As Needed"]
            combobox.set(value)
            entries[field] = combobox
        else:
            label = ttk.Label(entry_frame, text=f"{field}:")
            label.grid(row=i + 1, column=0, padx=5, pady=5, sticky="w")

            entry = ttk.Entry(entry_frame)
            entry.insert(0, value)
            entry.grid(row=i + 1, column=1, padx=0, pady=5, sticky="w")

            entries[field] = entry

            # Set focus to the first entry field
            if not first_field_set:
                entry.focus_set()
                first_field_set = True

    # Create a title for the popup form
    window_label = ttk.Label(entry_frame, text=title, style="PopupTitleA.TLabel")
    window_label.grid(
        row=0, column=0, columnspan=num_columns, padx=5, pady=10, sticky="ew"
    )

    # Frame for buttons
    button_frame = ttk.Frame(entry_frame)
    button_frame.grid(
        row=len(fields) + 2, column=0, columnspan=num_columns, pady=10, sticky="ew"
    )

    # Create cancel and submit buttons, attaching the appropriate action command
    submit_button = ttk.Button(
        button_frame, text="Submit", command=lambda: submit_action(entry_frame, entries)
    )
    cancel_button_entry = ttk.Button(
        button_frame, text="Cancel", command=lambda: close_window(entry_frame)
    )

    # Position the buttons in the frame
    submit_button.pack(side="left", padx=10)
    cancel_button_entry.pack(side="right", padx=10)


def delete_confirm_window():
    selected_item = meds_tree.selection()
    if not selected_item:
        return  # No item selected

    confirm_frame = ttk.Frame(meds_frame, style="Popup.TFrame")
    confirm_frame.place(
        relx=0.5,
        rely=0.5,
        anchor="center",  # Position it to center of main window (not sidebar)
        relheight=0.4,
        relwidth=0.55,
    )
    confirm_frame["padding"] = (5, 5)

    # Create a title for the popup frame
    title_txt = "Are you sure you want to delete the following medication?"
    window_label = ttk.Label(
        confirm_frame, text=title_txt, style="PopupTitleB.TLabel", wraplength=450
    )
    window_label.pack(side="top", pady=(5, 10))

    # Warning prompt
    medication_name = meds_tree.item(selected_item, "values")[
        1
    ]  # Assuming the medication name is in the 2nd field
    bold_font = font.Font(family="Helvetica", size=12, weight="bold")
    warning_label = ttk.Label(
        confirm_frame,
        text=f"{medication_name}",
        font=bold_font,
    )
    warning_label.pack(side="top", pady=(0, 0))

    # Frame for buttons
    button_frame = ttk.Frame(confirm_frame)
    button_frame.pack(side="bottom")

    # Create cancel and submit buttons, attaching the appropriate action command
    confirm_button = ttk.Button(
        button_frame, text="Delete", command=lambda: delete_entry_submit(confirm_frame)
    )
    cancel_button = ttk.Button(
        button_frame, text="Cancel", command=lambda: close_window(confirm_frame)
    )

    # Position the buttons in the frame
    confirm_button.pack(side="left", padx=10)
    cancel_button.pack(side="right", padx=10)


###########################################
# Login Functions
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
        login_frame_bg.place_forget()
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


###########################################
# Sidebar Functions
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
    meds_frame.tkraise()


def switch_to_search():
    search_frame.tkraise()


###########################################
# Table load/sort Functions
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
            meds_tree.insert("", "end", values=data_row)


def save_medication_data():
    global medication_data
    global active_user

    medication_data = []

    for item in meds_tree.get_children():
        data_row = [
            meds_tree.item(item, "values")[col]
            for col in range(len(meds_tree["columns"]))
        ]
        medication_data.append(data_row)

    if medication_data:
        users[active_user]["medication_data"] = medication_data
    else:
        users[active_user]["medication_data"] = ""


# Function to save data on app closure
def on_close():
    with open("user_data.txt", "w") as file:
        if active_user != "":
            save_medication_data()
        data_str = json.dumps(users)

        if data_str:
            encrypt_req = (data_str, key, "encode")
            socket.send_pyobj(encrypt_req)

            encrypted_str = socket.recv_string()
            file.write(encrypted_str)

    # Destroy the window after saving the data
    root.destroy()


# Sorting function for table
def sort_by_column(column_name):
    data = [
        (meds_tree.set(item, column_name), item) for item in meds_tree.get_children("")
    ]
    data.sort()
    for i, item in enumerate(data):
        meds_tree.move(item[1], "", i)


###########################################
# Table - Modify Functions
###########################################


def add_new_medication():
    global current_date
    global next_day

    # Fields for a new medication entry
    fields = {
        "Medication": "",
        "Dosage": "",
        "Dosage Unit": "mg",  # Default
        "Frequency": "",
        "Frequency Options": "Daily",  # Default
        "Start Date": f"{current_date_str}",
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
    selected_item = meds_tree.selection()
    if not selected_item:
        return  # No item selected

    values = meds_tree.item(selected_item, "values")

    # Dosage and unit are separated by a space
    dosage, dosage_unit = values[2].split(
        maxsplit=1
    )  # splits into two parts at the first space
    frequency, frequency_option = values[3].split(maxsplit=1)  # same for frequency

    fields = {
        "Medication": values[1],
        "Dosage": dosage,
        "Dosage Unit": dosage_unit,
        "Frequency": frequency,
        "Frequency Options": frequency_option,
        "Start Date": values[4],
        "End Date": values[5],
    }

    open_entry_window(
        "Update Medication",
        fields,
        lambda ef, e: update_entry_submit(ef, e),
        meds_frame,
    )


# Function to add a new row to table, called by open_entry_window()
def add_entry_submit(entry_frame, entries):
    medication = entries["Medication"].get()
    dosage = entries["Dosage"].get() + " " + entries["Dosage Unit"].get()
    frequency = entries["Frequency"].get() + " " + entries["Frequency Options"].get()
    start_date = entries["Start Date"].get()
    end_date = entries["End Date"].get()

    meds_tree.insert(
        "", "end", values=["", medication, dosage, frequency, start_date, end_date]
    )
    close_window(entry_frame)


# Function to update a row's data, called by open_entry_window on submit
def update_entry_submit(entry_frame, entries):
    selected_item = meds_tree.selection()
    if not selected_item:
        return  # No item selected

    medication = entries["Medication"].get()
    dosage = entries["Dosage"].get() + " " + entries["Dosage Unit"].get()
    frequency = entries["Frequency"].get() + " " + entries["Frequency Options"].get()
    start_date = entries["Start Date"].get()
    end_date = entries["End Date"].get()

    meds_tree.item(
        selected_item, values=["", medication, dosage, frequency, start_date, end_date]
    )
    close_window(entry_frame)


def delete_entry_submit(confirm_frame):
    selected_item = meds_tree.selection()
    if not selected_item:
        return  # No item selected
    else:
        # Logic to delete the selected item from the meds_tree
        meds_tree.delete(selected_item)

    # Close the confirmation window
    close_window(confirm_frame)


###########################################
# Search API Functions
###########################################


def search_medications():
    query = search_entry.get().strip()
    url = f"https://api.fda.gov/drug/label.json?search=openfda.brand_name:{query}&limit=40"
    print("url")
    response = requests.get(url)
    data = response.json()

    # Clear previous search results
    results_treeview.delete(
        *results_treeview.get_children()
    )  

    if "results" in data:
        added_medications = set()
        for item in data["results"]:
            brand_name = item.get("openfda", {}).get("brand_name", [None])[0]
            if brand_name and brand_name not in added_medications:
                results_treeview.insert("", tk.END, values=[brand_name])
                added_medications.add(brand_name)
    else:
        results_treeview.insert("", tk.END, values=["No results found"])


def lookup_medication_details():
    selected_item = results_treeview.selection()
    if not selected_item:
        return

    med_name = results_treeview.item(selected_item[0], "values")[0].replace(" ", "+")
    url = f'https://api.fda.gov/drug/label.json?search=openfda.brand_name:"{med_name}"&limit=1'
    response = requests.get(url)
    data = response.json()

    data_str = format_medication_data(data)
    details_text.config(state=tk.NORMAL)
    details_text.delete(1.0, tk.END)
    details_text.insert(tk.END, data_str)
    details_text.config(state=tk.DISABLED)


def extract_properties(data, props):
    result = data.get("results", [{}])[0]
    return {
        prop.replace("_", " ").title(): result.get(prop, [""])[0]
        for prop in props
        if prop in result
    }


def format_medication_data(data):
    data_str = ""
    desired_props = [
        "purpose",
        "indications_and_usage",
        "warnings",
        "dosage_and_administration",
    ]
    props_dictionary = extract_properties(data, desired_props)

    for prop, value in props_dictionary.items():
        formatted_prop = prop.replace("_", " ").upper()
        formatted_text = re.sub(r"(?<=\)\s|\.\s)([A-Z]|\d)", r"\n\n\1", value)
        data_str += f"\n{formatted_prop}:\n{formatted_text}\n"
    return data_str


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
search_button = ttk.Label(sidebar_frame, text="Medication Info", style="Sidebar.TLabel")

# Pack the sidebar elements into the grid
app_name_label.grid(row=0, padx=0, pady=0)
home_button.grid(row=1, padx=10, pady=1, sticky="w")
search_button.grid(row=2, padx=10, pady=1, sticky="w")
# history_button.grid(row=3, padx=10, pady=1, sticky="w")

# Bind events for mouse hover actions
home_button.bind("<Enter>", on_hover_enter)
search_button.bind("<Enter>", on_hover_enter)

home_button.bind("<Leave>", on_hover_leave)
search_button.bind("<Leave>", on_hover_leave)

# Bind click events to the labels using lambda functions
# Bind click events to the labels using lambda functions
home_button.bind(
    "<Button-1>", lambda e: (set_active_label(home_button), switch_to_home())
)
search_button.bind(
    "<Button-1>", lambda e: (set_active_label(search_button), switch_to_search())
)


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
    background="#008756",
    foreground="white",
    width=20,
    anchor="w",
)
# Active page sidebar label style
ttk.Style().configure(
    "Active.TLabel",
    font=("Helvetica", 15, "bold"),
    padding=(10, 5, 40, 5),
    background="#04B173",  # Active label background color
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
meds_table_title_frame = ttk.Frame(
    meds_frame, padding=(10, 5), style="TableTitle.TFrame"
)
meds_table_title_frame.pack(side="top", fill="x")

# Create a label for titling the table
meds_table_title = ttk.Label(
    meds_table_title_frame, text="Medications", style="MedsTitle.TLabel"
)

ttk.Style().configure("MedsTableTitle.TFrame", background="white")
ttk.Style().configure(
    "MedsTitle.TLabel",
    font=("Helvetica", 23, "bold"),
    padding=(5, 5, 40, 5),
    foreground="black",  # Active label text color
    width=20,
    anchor="w",
)

meds_table_title.pack(side="left", fill="none", expand=False)

# Create a button for adding an entry
add_entry_button = ttk.Button(
    meds_table_title_frame,
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
    "PopupTitleA.TLabel",
    font=("Helvetica", 23, "bold"),
    padding=(10, 5, 10, 5),
    foreground="black",  # Active label text color
    width=20,
    anchor="center",
)

ttk.Style().configure(
    "PopupTitleB.TLabel",
    font=("Helvetica", 15, "bold"),
    padding=(10, 5, 10, 5),
    foreground="black",  # Active label text color
    anchor="center",
)

# Design a field label style for the popup frames

#############################################################################################################
# Table Display
#############################################################################################################


# Create a frame to contain the treeview and scrollbar
tree_frame = ttk.Frame(meds_frame, style="MedsTable.TFrame", padding=(10, 0, 10, 0))
tree_frame.pack(side="top", fill="both")


ttk.Style().configure("MedsTable.TFrame", background="white")


# Create a Treeview widget (a table)
meds_tree = ttk.Treeview(
    tree_frame,
    columns=("Select", "Medication", "Dosage", "Frequency", "Start Date", "End Date"),
    show="headings",
    selectmode="extended",
    height=15,
    style="Treeview",
)

# Style treeview
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
meds_tree.heading("Select", text="", anchor="w")
meds_tree.heading("Medication", text="Medication", anchor="w")
meds_tree.heading("Dosage", text="Dosage", anchor="w")
meds_tree.heading("Frequency", text="Frequency", anchor="w")
meds_tree.heading("Start Date", text="Start Date", anchor="w")
meds_tree.heading("End Date", text="End Date", anchor="w")

# Configure column widthsmin
meds_tree.column("Select", width=30, minwidth=30, stretch=False)
meds_tree.column("Medication", width=150, minwidth=150)
meds_tree.column("Dosage", width=100, minwidth=100)
meds_tree.column("Frequency", width=100, minwidth=100)
meds_tree.column("Start Date", width=100, minwidth=100)
meds_tree.column("End Date", width=100, minwidth=100)

# Create a vertical scrollbar and attach it to the table
vsb = ttk.Scrollbar(
    tree_frame,
    orient="vertical",
    command=meds_tree.yview,
    style="Custom.Vertical.TScrollbar",
)
meds_tree.configure(yscrollcommand=vsb.set)


# Associate sorting functions with column headers
meds_tree.heading("Medication", command=lambda: sort_by_column("Medication"))
meds_tree.heading("Dosage", command=lambda: sort_by_column("Dosage"))
meds_tree.heading("Frequency", command=lambda: sort_by_column("Frequency"))
meds_tree.heading("Start Date", command=lambda: sort_by_column("Start Date"))
meds_tree.heading("End Date", command=lambda: sort_by_column("End Date"))

# Pack the treeview and scrollbar
meds_tree.pack(side="left", fill="both", expand=True)
vsb.pack(side="right", fill="both")

#############################################################################################################
# Table Bottom Buttons
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
edit_button.pack(side="left")


# Create "Delete Selected Medication" button
delete_button = ttk.Button(
    table_bottom_frame,
    text="Delete Selected Medication",
    command=delete_confirm_window,
    style="Delete.TButton",
)


ttk.Style().configure("Delete.TButton", font=("Helvetica", 14, "bold"), padding=(50, 5))
delete_button.pack(side="right")

#############################################################################################################
# Medication Search Frame
#############################################################################################################

search_frame = ttk.Frame(main_frame, style="SearchFrame.TFrame")
ttk.Style().configure(style="SearchFrame.TFrame")

search_frame.place(
    in_=meds_frame, relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1
)

# Create, configure and pack title frame within search frame
search_table_title_frame = ttk.Frame(
    search_frame, padding=(10, 5), style="SearchTableTitle.TFrame"
)
ttk.Style().configure("SearchTableTitle.TFrame")
search_table_title_frame.pack(side="top", fill="x")

# Create, style and pack title label
search_table_title = ttk.Label(
    search_table_title_frame, text="Medication Search", style="SearchTitle.TLabel"
)
ttk.Style().configure(
    "SearchTitle.TLabel",
    font=("Helvetica", 23, "bold"),
    padding=(5, 5, 20, 5),
    foreground="black",  # Active label text color
    width=20,
    anchor="w",
)
search_table_title.pack(side="left", fill="none", expand=False)


# Create, style and pack search button
search_entry_button = ttk.Button(
    search_table_title_frame,
    text="Search",
    style="Search.TButton",
    command=search_medications,
)
ttk.Style().configure("Search.TButton", font=("Helvetica", 13, "bold"), padding=(25, 5))
search_entry_button.pack(side="right", fill="none", expand=False)

# Search entry - TTK Entry
search_entry = ttk.Entry(search_table_title_frame, style="SearchEntry.TEntry", width=50)
ttk.Style().configure(
    "SearchEntry.TEntry", font=("Helvetica", 13, "bold"), padding=(13, 5)
)
search_entry.pack(side="right", expand=True, padx=10)

# Create and pack results treeview
results_treeview = ttk.Treeview(
    search_frame, columns=("Medication"), show="headings", height=10
)
results_treeview.heading("Medication", text="Medication")
results_treeview.pack(side="top", expand=True, fill="both", padx=10, pady=10)

# Create, style and pack lookup button
lookup_button = ttk.Button(
    search_frame,
    style="Details.TButton",
    text="Lookup Selected Medication Details",
    command=lookup_medication_details,
)
# Style and pack button
ttk.Style().configure(
    "Details.TButton", font=("Helvetica", 13, "bold"), padding=(25, 5)
)
lookup_button.pack(side="top", pady=20, padx=20)

# Create and pack details text widget
details_text = tk.Text(search_frame, height=20, wrap="word")
details_text.pack(side="top", fill="both", expand=True, padx=10, pady=10)

# Raise meds frame to ensure its home page of app
meds_frame.tkraise()


#############################################################################################################
# Login Frame
#############################################################################################################


# Create the frame as a child of the main frame and contain all other login elements
login_frame_bg = ttk.Frame(main_frame, style="LoginBackground.TFrame")
ttk.Style().configure("LoginBackground.TFrame", background="#04B173")

# Create a child frame to overlay the background
login_frame = ttk.Frame(login_frame_bg, style="Login.TFrame")
ttk.Style().configure("Login.TFrame")

login_frame_bg.place(
    in_=main_frame, relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1
)
login_frame.place(
    in_=login_frame_bg,
    relx=0.5,
    rely=0.5,
    anchor="center",
    relwidth=0.3,
    relheight=0.95,
)

# Application title
title_label = ttk.Label(
    login_frame, text="MedList", font=("Arial", 48, "italic", "bold")
)
title_label.pack(pady=10)

# User selection dropdown
user_label = ttk.Label(login_frame, text="Select User:", font=("Arial", 11, "bold"))
user_label.pack()

user_dropdown = ttk.Combobox(login_frame)
user_dropdown["values"] = list(users.keys())
if users:
    first_user = next(iter(users))  # Get the first key in the dictionary
    user_dropdown.set(first_user)  # Set the first user as the current value
user_dropdown.pack(pady=5)

# Password entry
password_label = ttk.Label(login_frame, text="Password:", font=("Arial", 11, "bold"))
password_label.pack()
password_entry = ttk.Entry(login_frame, show="*")
password_entry.pack(pady=5)
login_button = ttk.Button(
    login_frame,
    text="Login",
    command=lambda: verify_login(user_dropdown.get(), password_entry.get()),
)
login_button.pack(pady=10)

# Create new user button
new_user_button = ttk.Button(
    login_frame, text="Create New User", command=show_create_user_popup
)
new_user_button.pack(pady=10)

# Place the login frame inside the parent frame


#############################################################################################################
# Main Loop
#############################################################################################################
root.mainloop()
