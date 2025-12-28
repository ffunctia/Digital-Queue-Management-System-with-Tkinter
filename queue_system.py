import tkinter as tk
from tkinter import ttk
from datetime import datetime
import csv
from dataclasses import dataclass, field
from typing import Optional
#global deyisenler
operators = []
current_operator = None #aktiv operator
reportFile = "report.csv"

#dataclass hissesi
@dataclass
class Client:
    queue_no:int
    user:str
    time:str
    operator:str

@dataclass
class Database:
    name:str
    clients: list = field(default_factory=list)
    last_queue_number = 0

    def __post_init__(self):
        self.find_last_queue_number()

    def find_last_queue_number(self):
        try:
            with open(self.name, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                last = None
                for last in reader:
                    pass
                self.last_queue_number = int(last["queue_no"]) if last else 0
        except FileNotFoundError:
            self.last_queue_number = 0

    def update_treeview(self):        
        for item in user_table.get_children():
            user_table.delete(item)

        for client in self.clients:
            row = [client.queue_no, client.user, client.time, client.operator]
            user_table.insert("", "end", values = row)

    def add_new_client(self, name):
        time = datetime.now().strftime("%H:%M:%S")
        self.last_queue_number +=1
        self.clients.append(
            Client(
                self.last_queue_number,
                name,
                time,
                "waiting"
            )
        )

        self.update_treeview()

    def delete_queue(self, no):
        for client in self.clients:
            if(client.queue_no == no):
                self.clients.remove(client)
                break
        self.update_treeview()

    def update_database(self):
        all_rows = []
        for client in self.clients:
            row = []
            row.append(client.queue_no)
            row.append(client.user)
            row.append(client.time)
            row.append("waiting")
            all_rows.append(row)
            
        with open(self.name, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["queue_no", "user", "time", "operator"])
            writer.writerows(all_rows)

    def rtrn_names_no_waiting(self):
        list_of_no_waiting = []
        for clnt in self.clients:
            if(clnt.operator != "waiting"):
                list_of_no_waiting.append(clnt.user)

        return list_of_no_waiting

@dataclass
class Report:
    queue_no: int
    user: str
    time: str
    operator: str
    user_admission_time: Optional[str] = None

    def __post_init__(self):
        self.user_admission_time = datetime.now().strftime("%H:%M:%S") + " - "

    def add_data_to_treeview(self):
        if( self.user_admission_time is not None):
            self.user_admission_time = self.user_admission_time + datetime.now().strftime("%H:%M:%S")
            row = [self.queue_no, self.user, self.time, self.user_admission_time, self.operator]
            report_table.insert("", "end", values = row)
        
    def add_to_report_file(self):
        try:
            with open(reportFile, "r", encoding="utf-8") as f:
                pass
        except FileNotFoundError:
            with open(reportFile, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["queue_no", "user", "time", "user_admission_time", "operator"])

        with open(reportFile, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([self.queue_no, self.user, self.time, self.user_admission_time, self.operator])


    
@dataclass
class Operator:
    name:str
    status:bool
    busy_customer_no:int
    db:Database
    report_row: Optional[Report] = None

    def take_busy_customer(self):
        self.status = True
        name_of_new_customer = "None"
        queue_no_of_new_customer = 0
        
        for clnt in self.db.clients:
            if clnt.operator == "waiting":
                self.busy_customer_no = clnt.queue_no
                clnt.operator = self.name

                name_of_new_customer = clnt.user
                queue_no_of_new_customer = clnt.queue_no 

                self.report_row = Report(
                    clnt.queue_no, 
                    clnt.user, 
                    clnt.time, 
                    self.name
                )
                break
        self.db.update_treeview()

        return name_of_new_customer, queue_no_of_new_customer

    def end_session(self):
        self.db.delete_queue(self.busy_customer_no)

        if( self.report_row is not None):
            self.report_row.add_data_to_treeview()
            self.report_row.add_to_report_file()

        self.status = False
        self.busy_customer_no = 0
        
    
    
#dataclass hissesi bitir

#global database
global database
database = None
#global database bitir

def exit_fullscreen(event):
    main.attributes("-fullscreen", False)

def enter_fullscreen(event):
    main.attributes("-fullscreen", True)

def update_clock():
    txt = "clock: " + datetime.now().strftime("%H:%M:%S")
    clock.config(text = txt)
    main.after(1000, update_clock)

def load_csv(csv_name):
    all_clients_list = []

    operators.clear()
    global current_operator
    current_operator = None

    
    for tab in operator_tabs.tabs():
        operator_tabs.forget(tab)
    
    for item in user_table.get_children():
        user_table.delete(item)

    try:
        with open(csv_name, "r", encoding = "utf-8") as f:
            reader = csv.reader(f)
            next(reader)

            for row in reader:
                user_table.insert("", "end", values = row)
                all_clients_list.append(
                    Client(
                        int(row[0]),
                        row[1],
                        row[2],
                        row[3]
                    )
                )

    except FileNotFoundError:
        print("Database not found.")

    global database
    database = Database( csv_name, all_clients_list )

    db_name_db_section_op.config(
        text = csv_name
    )

    button_remove_queue.config(state = "normal")
    remove_name_entry.config(state = "normal")
    button_new_queue.config(state = "normal")
    new_queue_entry.config(state = "normal")
    add_operator_button.config(state = "normal")
    db_name_db_section_op.config(state = "normal")
    operator_name_entry.config(state = "normal")
    update_database_button.config(state = "normal")

def update_called_names():
    global database
    if database is not None:
        names_that_call = database.rtrn_names_no_waiting()
        txt = "In Session:  " + "  ;".join(names_that_call)
        called_names.config(text = txt)

    else:
        called_names.config(text = "Database is expected")

    main.after(5000, update_called_names)

def read_file_name():
    value = file_name_entry.get()
    print("Entered database name:", value)
    load_csv(value)
    file_name_entry.delete(0, tk.END)

def read_new_name():
    value = new_queue_entry.get()
    print("Entered new queue name: ", value)
    database.add_new_client(value)
    new_queue_entry.delete(0, tk.END)
    visitor_log.config(text = f"Entered new queue name: {value}")

def read_remove_name():
    value = remove_name_entry.get()
    global database
    if database is not None:
        for clnt in database.clients:
            if(clnt.user == value):
                if(clnt.operator == "waiting"):
                    database.delete_queue(clnt.queue_no)
                    visitor_log.config(
                        text = f"Queue was deleted!: {clnt.user}"
                    )
                else:
                    visitor_log.config(
                        text = "Pending users cannot be deleted.!"
                    )
                return
        visitor_log.config(
            text = f"Queue not found!: {value}"
        )
        
    

def save_database():
    global database
    database.update_database()

def make_operator_tab(op: Operator):
    frame = tk.Frame(operator_tabs)
    operator_tabs.add(frame, text=op.name)

    left_bar_mk_op = tk.Frame(frame)
    left_bar_mk_op.pack(side = "left", expand = True)

    right_bar_mk_op = tk.Frame(frame)
    right_bar_mk_op.pack(side = "right", expand = True)
        
    tk.Label(
        left_bar_mk_op, 
        text=f"Operator: {op.name}", 
        font = ("Segoe UI", 16, "bold"),
        fg = "blue"
    ).pack(pady=10)

    status_label = tk.Label(
        left_bar_mk_op, 
        text="Status: FREE", 
        foreground="green",
        font = ("Segoe UI", 16, "bold")
    )
    status_label.pack(pady=10)

    customer_label = tk.Label(
        left_bar_mk_op,
        text = "Customer name: None",
        foreground = "green",
        font = ("Segoe UI", 16, "bold")
    )
    customer_label.pack(pady = 10)

    queue_no_label = tk.Label(
        left_bar_mk_op,
        text = "Queue No: None",
        foreground = "green",
        font = ("Segoe UI", 16, "bold")
    )
    queue_no_label.pack(pady = 10)

    def take_customer():
        nameCustomer, queue_noCustomer = op.take_busy_customer()
        
        status_label.config(
            text = "Status: Busy",
            fg = "red"
        )

        customer_label.config(
            text = f"Customer name: {nameCustomer}",
            fg = "red"
        )

        queue_no_label.config(
            text = f"Queue No: {queue_noCustomer}",
            fg = "red"
        )

        operator_button.config(
            text = "End the session!", 
            command = end_session,
            bg = "red",
            width = 30,
            height = 3,
            font = ("Segoe UI", 16, "bold"),
            fg = "white",
            activebackground="#ff1493",
            activeforeground="white"
        )

    def end_session():
        op.end_session()
        status_label.config(
            text = "Status: FREE",
            foreground = "green"
        )

        customer_label.config(
            text = "Customer name: None",
            fg = "green"
        )

        queue_no_label.config(
            text = "Queue No: None",
            fg = "green"
        )

        operator_button.config(
            text = "Take customer.", 
            command = take_customer,
            bg = "green",
            width = 30,
            height = 3,
            font = ("Segoe UI", 16, "bold"),
            fg = "white",
            activebackground="#54ff9f",
            activeforeground="white"
        )

    operator_button = tk.Button(
        right_bar_mk_op, 
        text="Take customer", 
        command=take_customer,
        width = 30,
        bg = "green",
        height = 3,
        font = ("Segoe UI", 16, "bold"),
        fg = "white",
        activebackground="#54ff9f",
        activeforeground="white"
    )
    operator_button.pack(pady = 5)


def add_operator():
    name = operator_name_entry.get()
    operator_name_entry.delete(0, tk.END)
    op = Operator(name = name, status = False, busy_customer_no = 0, db = database)
    operators.append(op)
    print("New operator added! ", name)
    make_operator_tab(op)

def on_operator_tab_change(event):
    global current_operator
    selected_tab = operator_tabs.select()
    if not selected_tab:
        current_operator = None
        return

    try:
        index = operator_tabs.index(operator_tabs.select())
        if(index < len(operators)):
            current_operator = operators[index]
            print("Active operator:", current_operator.name)

    except tk.TclError:
        pass

def load_report_file_to_tree_view():
    for item in report_table.get_children():
        report_table.delete(item)

    try:
        with open(reportFile, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                report_table.insert("", "end", values=row)

            report_log.config(text = "report.csv was successfully loaded!")
    except FileNotFoundError:
        report_log.config(text = "report.csv could not be loaded!")
        pass

def delete_report_file():
    with open(reportFile, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["queue_no", "user", "time", "user_admission_time", "operator"])

    for item in report_table.get_children():
        report_table.delete(item)

    report_log.config(text = "report.csv was succesfully deleted!")



#test hissesi

#test hissesi bitir

main = tk.Tk()
main.config(bg = "blue")
main.geometry("1200x800")
main.attributes("-fullscreen", True)
main.bind("<Escape>", exit_fullscreen)
main.bind("<F11>", enter_fullscreen)
main.title("Digital Quee System")

footer_frame = tk.Frame(main, bg = "blue")
footer_frame.pack(side = "bottom", fill = "x")
clock = tk.Label(
    footer_frame, 
    font = ("Liberation Mono", 24, "bold"),
    fg = "white",
    bg = "blue",
)
clock.pack(side = "left", pady = 5, padx = 30)
update_clock()

owner_of_software = tk.Label(
    footer_frame,
    text = "© 2025 Fuad Nasirli. All rights reserved",
    font = ("Segoe UI", 12, "underline"),
    fg = "white",
    bg = "blue"
)
owner_of_software.pack(side = "right", pady = 5, padx = 30)

tab_system = ttk.Notebook(main)
tab_system.pack(side = "top", expand = True, fill = "both")

visitor_view = ttk.Frame(tab_system)
user_view = ttk.Frame(tab_system)
operator_view = ttk.Frame(tab_system)
report_view = ttk.Frame(tab_system)

tab_system.add(visitor_view, text = "visitor")
tab_system.add(user_view, text = "user")
tab_system.add(operator_view, text = "operator")
tab_system.add(report_view, text = "report")

#USER VIEW hissesi burada olacaq
top_bar_usr = tk.Frame(
    user_view
)
top_bar_usr.pack(side = "top", fill = "x", pady = 10)

called_names = tk.Label(
    top_bar_usr,
    fg = "blue",
    font = ("Segoe UI", 24, "bold")
)
called_names.pack()
update_called_names()

columns_user_table = ("queue_no", "user", "time", "operator")

user_table_section = tk.Frame(
    user_view
)
user_table_section.pack(
    side = "bottom", 
    expand = True, 
    pady  =10, 
    padx = 10, 
    fill = "both"
)

user_table = ttk.Treeview(
    user_table_section,
    columns = columns_user_table,
    show = "headings"
)
user_table.pack(side = "left", expand = True, fill = "both")

user_table.heading("queue_no", text = "Queue No")
user_table.heading("user", text = "User")
user_table.heading("time", text = "Time")
user_table.heading("operator", text = "Operator")

user_table.column("queue_no", width = 50, anchor = "center")
user_table.column("user", width = 200, anchor = "center")
user_table.column("time", width = 70, anchor = "center")
user_table.column("operator", width = 200, anchor = "center")

scrollbar = ttk.Scrollbar(
    user_table_section,
    orient = "vertical",
    command = user_table.yview
)
user_table.configure(yscrollcommand = scrollbar.set)
scrollbar.pack(side = "right", fill="y")
#USER hissesi burada bitir

#Operator VIEW hissesi burada olacaq
top_bar_op = tk.Frame(operator_view)
top_bar_op.pack(expand = True)

file_section_op = tk.Frame(top_bar_op)
file_section_op.pack(side="left", padx =50) 

db_section_op = tk.Frame(top_bar_op)
db_section_op.pack(side="left", padx = 50)

op_section = tk.Frame(top_bar_op)
op_section.pack(side="left", padx = 50)

tk.Label(
    file_section_op, 
    text="File name:",
    font = ("Segoe UI", 16, "bold"),
    fg = "blue"
).pack(pady = 15)

file_name_entry = tk.Entry(
    file_section_op,
    font = ("Segoe UI", 16, "bold"),
    width = 20
)
file_name_entry.pack(pady = 15)

tk.Button(
    file_section_op, 
    command=read_file_name,
    bg = "blue",
    width = 20,
    height = 1,
    font = ("Segoe UI", 14, "bold"),
    activebackground="#87ceff"
).pack(pady=15)


update_database_button = tk.Button(
    db_section_op, 
    text="Update database!", 
    command=save_database, 
    bg = "green",
    width = 20,
    height = 2,
    font = ("Segoe UI", 14, "bold"),
    fg = "white",
    activebackground="#54ff9f",
    activeforeground="white",
    state = "disabled"
)
update_database_button.pack()

db_name_db_section_op = tk.Label(
    db_section_op,
    text = "Database is expected!",
    fg = "blue",
    font = ("Segoe UI", 16, "bold")
)
db_name_db_section_op.pack(pady = 10)

tk.Label(
    op_section, 
    text="New operator:",
    font = ("Segoe UI", 16, "bold"),
    fg = "blue"    
).pack(pady = 15)

operator_name_entry = tk.Entry(
    op_section,
    font = ("Segoe UI", 16, "bold"),
    width = 20,
    state = "disabled"
)
operator_name_entry.pack(pady = 15)

add_operator_button = tk.Button(
    op_section, 
    command=add_operator,
    bg = "blue",
    width = 20,
    height = 1,
    font = ("Segoe UI", 14, "bold"),
    activebackground="#87ceff",
    state = "disabled"
)
add_operator_button.pack(pady = 15)

operator_tabs = ttk.Notebook(operator_view)
operator_tabs.pack(side="bottom", expand=True, fill="both", padx=10, pady=10)
operator_tabs.bind("<<NotebookTabChanged>>", on_operator_tab_change)

#Operator hissesi burada bitir

#Visitor VIEW hissesi burada olacaq
top_bar_vw = tk.Frame(visitor_view)
top_bar_vw.pack(expand = True)

new_queue_bar_vw = tk.Frame(top_bar_vw)
new_queue_bar_vw.pack(side = "left", expand = True, padx = 40)

tk.Label(
    new_queue_bar_vw, 
    text = "Enter new queue!",
    font = ("Segoe UI", 18, "bold"),
    fg = "blue"
).pack(pady = 10)

new_queue_entry = tk.Entry(
    new_queue_bar_vw, 
    font = ("Segoe UI", 22, "bold"),
    width = 31,
    state = "disabled"
)
new_queue_entry.pack(pady = 10)

button_new_queue = tk.Button(
    new_queue_bar_vw, 
    text = "Confirm the new queue!",
    command = read_new_name,
    bg = "green",
    width = 30,
    height = 3,
    font = ("Segoe UI", 22, "bold"),
    fg = "white",
    activebackground="#54ff9f",
    activeforeground="white",
    state = "disabled"
)
button_new_queue.pack(pady = 10)

rm_queue_bar_vw = tk.Frame(top_bar_vw)
rm_queue_bar_vw.pack(side = "right", expand = True, padx = 40)
tk.Label(
    rm_queue_bar_vw, 
    text = "Enter the queue you want to delete!!",
    font = ("Segoe UI", 18, "bold"),
    fg = "blue"
).pack(pady = 10)

remove_name_entry = tk.Entry(
    rm_queue_bar_vw,
    font = ("Segoe UI", 22, "bold"),
    width = 31,
    state = "disabled"
)
remove_name_entry.pack(pady = 10)

button_remove_queue = tk.Button(
    rm_queue_bar_vw,
    text = "Delete the queue!",
    command = read_remove_name,
    bg = "red",
    width = 30,
    height = 3,
    font = ("Segoe UI", 22, "bold"),
    fg = "white",
    activebackground="#ff1493",
    activeforeground="white",
    state = "disabled"
)
button_remove_queue.pack(pady = 10)

bottom_bar_vw = tk.Frame(visitor_view)
bottom_bar_vw.pack(side = "bottom", fill = "x")

log_bar_vw = tk.Frame(bottom_bar_vw)
log_bar_vw.pack(expand = True)
visitor_log = tk.Label(
    log_bar_vw,
    text = "Transaction pending!",
    font = ("Segoe UI", 24, "bold"),
    fg = "blue",
    anchor = "center"
)
visitor_log.pack()
#Visitor hissesi burada bitir

#report hissesi burada olacaq
top_bar_rp = tk.Frame(report_view)
top_bar_rp.pack(side = "top", fill = "x", pady = (10, 10))

report_log = tk.Label(
    top_bar_rp,
    text = "Transaction Pending!",
    font = ("Segoe UI", 24, "bold"),
    fg = "blue",
    anchor = "center"
)
report_log.pack(side = "left", padx = 15)

btn_bar_rp = tk.Frame(top_bar_rp)
btn_bar_rp.pack(side = "right", padx = 15)

load_report_csv_button = tk.Button(
    btn_bar_rp,
    text = "Load Report.csv!",
    command = load_report_file_to_tree_view,
    bg = "green",
    width = 30,
    height = 3,
    font = ("Segoe UI", 22, "bold"),
    fg = "white",
    activebackground= "#54ff9f",
    activeforeground="white"
)
load_report_csv_button.pack(side = "left", padx = 5)

delete_report_button = tk.Button(
    btn_bar_rp,
    text = "Delete Report.csv!",
    command = delete_report_file,
    bg = "red",
    width = 30,
    height = 3,
    font = ("Segoe UI", 22, "bold"),
    fg = "white",
    activebackground="#ff1493",
    activeforeground="white"
)
delete_report_button.pack(side = "left", padx = 5)

table_area_rp = tk.Frame(report_view)
table_area_rp.pack(side = "top", expand = True, fill = "both")

columns_report_table = ("queue_no", "user", "time", "user_admission_time", "operator")

report_table = ttk.Treeview(
    table_area_rp,
    columns = columns_report_table,
    show = "headings"
)
report_table.pack(side = "left", expand = True, fill = "both", padx = (15, 0), pady = 10)

report_table.heading("queue_no", text = "Queue No")
report_table.heading("user", text = "User")
report_table.heading("time", text = "Time")
report_table.heading("user_admission_time", text = "User Admission Time")
report_table.heading("operator", text = "Operator")

report_table.column("queue_no", width = 50, anchor = "center")
report_table.column("user", width = 150, anchor = "center")
report_table.column("time", width = 70, anchor = "center")
report_table.column("user_admission_time", width = 200, anchor = "center")
report_table.column("operator", width = 150, anchor = "center")

scrollbar = ttk.Scrollbar(
    table_area_rp,
    orient = "vertical",
    command = report_table.yview
)
report_table.configure(yscrollcommand = scrollbar.set)
scrollbar.pack(side = "right", fill="y", padx = (0, 15), pady = 10)

#report hissesi burada bitir

main.mainloop()
