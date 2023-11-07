import tkinter as tk
from tkinter import ttk
from tkinter import Frame
from tkinter import font
from random import randint, uniform
from datetime import datetime, timedelta


# Function to spawn medication addition popup
def open_add_window(medication="", dosage="", frequency="", start_date="", end_date=""):
    entry_frame = ttk.Frame(meds_frame, style="Popup.TFrame")
    entry_frame.place(relx=0.5, rely=0.5, anchor="center")
    entry_frame["padding"] = (10, 10)

    add_window_label = ttk.Label(
        entry_frame, text="Add New Medication", style="PopupTitle.TLabel"
    )

    medication_label = ttk.Label(entry_frame, text="Medication:")
    medication_entry = ttk.Entry(entry_frame)
    medication_entry.insert(0, medication)

    dosage_label = ttk.Label(entry_frame, text="Dosage:")
    dosage_entry = ttk.Entry(entry_frame)
    dosage_entry.insert(0, dosage)

    frequency_label = ttk.Label(entry_frame, text="Frequency:")
    frequency_entry = ttk.Entry(entry_frame)
    frequency_entry.insert(0, frequency)

    start_date_label = ttk.Label(entry_frame, text="Start Date:")
    start_date_entry = ttk.Entry(entry_frame)
    start_date_entry.insert(0, start_date)

    end_date_label = ttk.Label(entry_frame, text="End Date:")
    end_date_entry = ttk.Entry(entry_frame)
    end_date_entry.insert(0, end_date)

    add_window_label.grid(row=0, column=0, columnspan=2, padx=5, pady=10)

    medication_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
    medication_entry.grid(row=1, column=1, padx=5, pady=5)

    dosage_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
    dosage_entry.grid(row=2, column=1, padx=5, pady=5)

    frequency_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
    frequency_entry.grid(row=3, column=1, padx=5, pady=5)

    start_date_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
    start_date_entry.grid(row=4, column=1, padx=5, pady=5)

    end_date_label.grid(row=5, column=0, padx=5, pady=5, sticky="w")
    end_date_entry.grid(row=5, column=1, padx=5, pady=5)

    submit_button = ttk.Button(
        entry_frame,
        text="Submit",
        command=lambda: add_new_entry(
            entry_frame,
            medication_entry.get(),
            dosage_entry.get(),
            frequency_entry.get(),
            start_date_entry.get(),
            end_date_entry.get(),
        ),
    )

    cancel_button = ttk.Button(
        entry_frame, text="Cancel", command=lambda: close_entry_window(entry_frame)
    )

    cancel_button.grid(row=6, column=1, padx=30, pady=10)
    submit_button.grid(row=6, column=0, padx=5, pady=10)


# Function to spawn medication update popup
def open_update_window(
    medication="", dosage="", frequency="", start_date="", end_date=""
):
    entry_frame = ttk.Frame(meds_frame, style="Popup.TFrame")
    entry_frame.place(relx=0.5, rely=0.5, anchor="center")
    entry_frame["padding"] = (10, 10)

    add_window_label = ttk.Label(
        entry_frame, text="Update Medication", style="PopupTitle.TLabel"
    )

    medication_label = ttk.Label(entry_frame, text="Medication:")
    medication_entry = ttk.Entry(entry_frame)
    medication_entry.insert(0, medication)

    dosage_label = ttk.Label(entry_frame, text="Dosage:")
    dosage_entry = ttk.Entry(entry_frame)
    dosage_entry.insert(0, dosage)

    frequency_label = ttk.Label(entry_frame, text="Frequency:")
    frequency_entry = ttk.Entry(entry_frame)
    frequency_entry.insert(0, frequency)

    start_date_label = ttk.Label(entry_frame, text="Start Date:")
    start_date_entry = ttk.Entry(entry_frame)
    start_date_entry.insert(0, start_date)

    end_date_label = ttk.Label(entry_frame, text="End Date:")
    end_date_entry = ttk.Entry(entry_frame)
    end_date_entry.insert(0, end_date)

    add_window_label.grid(row=0, column=0, columnspan=2, padx=5, pady=10)

    medication_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
    medication_entry.grid(row=1, column=1, padx=5, pady=5)

    dosage_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
    dosage_entry.grid(row=2, column=1, padx=5, pady=5)

    frequency_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
    frequency_entry.grid(row=3, column=1, padx=5, pady=5)

    start_date_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
    start_date_entry.grid(row=4, column=1, padx=5, pady=5)

    end_date_label.grid(row=5, column=0, padx=5, pady=5, sticky="w")
    end_date_entry.grid(row=5, column=1, padx=5, pady=5)

    submit_button = ttk.Button(
        entry_frame,
        text="Submit",
        command=lambda: update_entry(
            entry_frame,
            medication_entry.get(),
            dosage_entry.get(),
            frequency_entry.get(),
            start_date_entry.get(),
            end_date_entry.get(),
        ),
    )

    cancel_button = ttk.Button(
        entry_frame, text="Cancel", command=lambda: close_entry_window(entry_frame)
    )

    cancel_button.grid(row=6, column=1, padx=30, pady=10)
    submit_button.grid(row=6, column=0, padx=5, pady=10)


# Function to add a new row to table
def add_new_entry(entry_frame, medication, dosage, frequency, start_date, end_date):
    tree.insert(
        "", "end", values=["", medication, dosage, frequency, start_date, end_date]
    )
    close_entry_window(entry_frame)


# Function to close a particular frame
def close_entry_window(entry_frame):
    entry_frame.destroy()


# Function to edit a selected row's data, calls open_update_window on button press
def edit_selected_medication():
    selected_item = tree.selection()
    if not selected_item:
        return  # No item selected
    values = tree.item(selected_item, "values")
    print("Selected item:", selected_item)
    print("Values:", values)  # Print the values being passed
    open_update_window(
        medication=values[1],
        dosage=values[2],
        frequency=values[3],
        start_date=values[4],
        end_date=values[5],
    )


# Function to update a row's data, called by open_update_window on submission
def update_entry(entry_frame, medication, dosage, frequency, start_date, end_date):
    selected_item = tree.selection()

    if not selected_item:
        return  # No item selected

    # Update the selected row with the edited data
    tree.item(
        selected_item, values=["", medication, dosage, frequency, start_date, end_date]
    )

    # Close the entry window
    close_entry_window(entry_frame)


#############################################################################################################
# Main Window
#############################################################################################################

root = tk.Tk()
root.title("MedList")
root.geometry("1200x600")

# Set a minimum window size
root.minsize(width=1200, height=600)

# Create a main frame for the table and sidebar
main_frame = ttk.Frame(root)
main_frame.pack(fill="both", expand=True)


def switch_to_home():
    # TODO: Implement the "Home" button functionality here
    pass


def switch_to_schedule():
    # TODO Implement the "View 2" button functionality here
    pass


def switch_to_history():
    # TODO Implement the "View 3" button functionality here
    pass


#############################################################################################################
# Sidebar
#############################################################################################################


# Define functions to handle hover highliging behavior
def on_hover_enter(event):
    if event.widget != active_label:
        event.widget.configure(style="Hover.TLabel")


def on_hover_leave(event):
    if event.widget != active_label:
        event.widget.configure(style="Sidebar.TLabel")


def set_active_label(label):
    global active_label
    if active_label:
        active_label.configure(style="Sidebar.TLabel")
    active_label = label
    active_label.configure(style="Active.TLabel")


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

# Define a custom style for the sidebar frame
# Background color for sidebar
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

meds_frame.pack(side="left", fill="both", expand=True)

#############################################################################################################
# Table Title + Add button
#############################################################################################################
# TODO
# Create a frame above the table to hold title + button
table_title_frame = ttk.Frame(meds_frame, padding=(10, 5), style="TableTitle.TFrame")
table_title_frame.pack(side="top", fill="x")

# Create a label for titling the table
table_title = ttk.Label(table_title_frame, text="Medications", style="Title.TLabel")

ttk.Style().configure("TableTitle.TFrame", background="white")
ttk.Style().configure(
    "Title.TLabel",
    font=("Helvetica", 23, "bold"),
    padding=(10, 5, 40, 5),
    background="white",
    foreground="black",  # Active label text color
    width=20,
    anchor="w",
)

table_title.pack(side="left", fill="none", expand=True)

# Create a button for adding an entry
add_entry_button = ttk.Button(
    table_title_frame,
    text="Add Medication +",
    style="Add.TButton",
    command=open_add_window,
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


# Create a frame to contain the treeview and scrollbar
tree_frame = ttk.Frame(meds_frame, style="MedsTable.TFrame", padding=(10, 0, 10, 0))
tree_frame.pack(side="top", fill="both")


ttk.Style().configure("MedsTable.TFrame", background="white")

# Create a Treeview widget
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


# Pack the treeview and scrollbar
tree.pack(side="left", fill="both", expand=True)
vsb.pack(side="right", fill="both")


# Define sorting functions
def sort_by_medication():
    data = [(tree.set(item, "Medication"), item) for item in tree.get_children("")]
    data.sort()
    for i, item in enumerate(data):
        tree.move(item[1], "", i)


def sort_by_dosage():
    data = [(tree.set(item, "Dosage"), item) for item in tree.get_children("")]
    data.sort()
    for i, item in enumerate(data):
        tree.move(item[1], "", i)


def sort_by_frequency():
    data = [(tree.set(item, "Frequency"), item) for item in tree.get_children("")]
    data.sort()
    for i, item in enumerate(data):
        tree.move(item[1], "", i)


def sort_by_start_date():
    data = [(tree.set(item, "Start Date"), item) for item in tree.get_children("")]
    data.sort()
    for i, item in enumerate(data):
        tree.move(item[1], "", i)


def sort_by_end_date():
    data = [(tree.set(item, "End Date"), item) for item in tree.get_children("")]
    data.sort()
    for i, item in enumerate(data):
        tree.move(item[1], "", i)


# Associate sorting functions with column headers
tree.heading("Medication", command=sort_by_medication)
tree.heading("Dosage", command=sort_by_dosage)
tree.heading("Frequency", command=sort_by_frequency)
tree.heading("Start Date", command=sort_by_start_date)
tree.heading("End Date", command=sort_by_end_date)


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
# Function to similar data entry
def generate_valid_entry():
    medication = "Medication"  # Replace with a proper noun
    dosage = f"{uniform(0.01, 500):.1f} mg"
    frequency = f"{randint(1, 5)}x / Day"

    start_date = datetime(randint(2022, 2022), randint(1, 12), randint(1, 28))
    end_date = start_date + timedelta(days=randint(1, 365))  # Up to 1 year apart

    return [
        "",
        medication,
        dosage,
        frequency,
        start_date.strftime("%Y/%m/%d"),
        end_date.strftime("%Y/%m/%d"),
    ]


# Insert x generated entries with specified formatting
for _ in range(50):
    entry_data = generate_valid_entry()
    entry_data[1] += f" {_ + 1}"
    tree.insert("", "end", values=entry_data, tags=("editable",))


root.mainloop()
