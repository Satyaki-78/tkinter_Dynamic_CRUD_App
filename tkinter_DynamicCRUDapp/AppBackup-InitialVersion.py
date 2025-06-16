import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import ctypes
import os
#from CTkMessagebox import CTkMessagebox
from tkcalendar import DateEntry
import threading
#import pandas as pd
#import concurrent.futures

def msgbox(icon, title, msg, parent=None):
        from tkinter import messagebox
        if icon == 'info':
            messagebox.showinfo(title,msg, parent=parent)
        elif icon == 'warn':
            messagebox.showwarning(title,msg, parent=parent)
        else:
            messagebox.showerror(title,msg, parent=parent)

class SQLApp(ctk.CTk):
    
    fields = [
        ["Roll","ctk.CTkEntry","w",],
        ["Name","ctk.CTkEntry","ew"],
        ["Marks","ctk.CTkEntry","w"],
        ["DOB","DateEntry","w"],
    ]
    
    query_fields = [
        "roll",
        "sname",
        "marks",
        "dob"
    ]
    
    def __init__(self):
        super().__init__()
        
        # Make the app DPI-aware for high-resolution displays
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        
        # Set color theme
        ctk.set_appearance_mode("Dark")
        theme_path = os.path.join(os.path.dirname(__file__), "themes", "rime-theme.json")
        ctk.set_default_color_theme(theme_path)
        
        # Centering window dynamically
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = int(screen_width * 0.6)
        window_height = int(screen_height * 0.6)
        center_x = (screen_width - window_width) // 2
        center_y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        
        self.title("SQL APP")
        
        # 2x2 Grid Structure
        self.grid_rowconfigure(0, weight=1)  # First row
        self.grid_rowconfigure(1, weight=2)  # Second row (More space for Treeview)
        
        self.grid_columnconfigure(0, weight=1)  # First column
        self.grid_columnconfigure(1, weight=1)  # Second column
        
        self.initUI_EntryFrame()
        self.initUI_ButtonFrame()
        self.initUI_DataViewFrame()
        
        
    def initUI_EntryFrame(self):
        #Frame 1: Labels & Entry Widgets
        self.entry_frame = ctk.CTkScrollableFrame(self)
        self.entry_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.entry_frame.grid_columnconfigure(1, weight=1)  # Expand entries
        self.add_entry_fields()
    
    def add_entry_fields(self):
        #Using a list to store and work with the widgets
        self.widgets = []
        
        #Dynamically Adding Data Entry Widgets 
        for i, item in enumerate(self.fields):
            label = ctk.CTkLabel(self.entry_frame, text=item[0])
            label.grid(row=i, column=0, padx=5, pady=5, sticky="w")
            #self.widgets.append(label)
            
            widget_func = eval(item[1])
            entry = widget_func(self.entry_frame, font=("Consolas",14))
            entry.grid(row=i, column=1, padx=5, pady=5, sticky=item[2])
            self.widgets.append(entry)
    
    def initUI_ButtonFrame(self):
        #Frame 2: Buttons
        self.button_frame = ctk.CTkFrame(self,)
        self.button_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.button_frame.grid_columnconfigure(0, weight=1)
        
        db_table_btnFrame = ctk.CTkFrame(self.button_frame)
        db_table_btnFrame.grid(row=0, column=0, sticky="nsew")
        db_table_btnFrame.grid_columnconfigure(0,weight=1)
        db_table_btnFrame.grid_columnconfigure(1,weight=1)
        
        self.connectDB_btn = ctk.CTkButton(db_table_btnFrame, text="Connect to Database", command=None)
        self.connectDB_btn.grid(row=0, column=0, padx=5, pady=5, sticky="nse")
        
        self.changeTable_btn = ctk.CTkButton(db_table_btnFrame, text="Change Table")
        self.changeTable_btn.grid(row=0, column=1, padx=5, pady=5, sticky="nsw")
        
        #self.DB_Table_btn = ctk.CTkSegmentedButton(self.button_frame, values=["Connect to Database","Change Table"])
        #self.DB_Table_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ns")
        
        self.displayRec_btn = ctk.CTkButton(self.button_frame, text="Display All Records", command=self.startThread_displayRecords)
        self.displayRec_btn.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        self.addRec_btn = ctk.CTkButton(self.button_frame, text="Add Record", command=self.startThread_addRecord)
        self.addRec_btn.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        
        self.searchRec_btn = ctk.CTkButton(self.button_frame, text="Search Record", command=self.startThread_searchRecord)
        self.searchRec_btn.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        
        self.modifyRec_btn = ctk.CTkButton(self.button_frame, text="Modify Record", command=self.startThread_modifyRecord, state="disabled")
        self.modifyRec_btn.grid(row=4, column=0, padx=5, pady=5, sticky="ew")
        
        self.deleteRec_btn = ctk.CTkButton(self.button_frame, text="Delete Record", command=self.startThread_deleteRecord, state="disabled")
        self.deleteRec_btn.grid(row=5, column=0, padx=5, pady=5, sticky="ew")
        
        self.exit_btn = ctk.CTkButton(self.button_frame, text="Exit", command=self.exitApp)
        self.exit_btn.grid(row=6, column=0, padx=5, pady=5, sticky="ns")
        
    def initUI_DataViewFrame(self):
        #Frame 3: Label & Treeview
        self.data_frame = ctk.CTkFrame(self)
        self.data_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        self.data_frame.grid_rowconfigure(1, weight=1)  # Expand treeview
        self.data_frame.grid_columnconfigure(0, weight=1)  # Expand width
        
        self.dataview_infoLabel = ctk.CTkLabel(
            self.data_frame, text="Info about the data view", 
            bg_color="green", 
            font=("Arial",14)
        )
        self.dataview_infoLabel.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        #Treeview Style
        self.style = ttk.Style()
        self.style.configure("Treeview",font=("Arial",13))
        self.style.configure("Treeview.Heading",font=("Corbel",15,"bold"))
        self.style.map("Treeview",background=[("alternate","lightgray")])
        self.style.map("Treeview",background=[("selected","black")])
        
        columns = []
        for list in self.fields:
            columns.append(list[0])
        
        #Treeview Widget
        self.dataview = ttk.Treeview(self.data_frame, columns=columns, show='headings')
        self.dataview.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        for col in columns:
            self.dataview.heading(col, text=col)
            self.dataview.column(col, anchor="center")
        
        # Scrollbar
        self.scroll_y = ttk.Scrollbar(self.data_frame, orient="vertical", command=self.dataview.yview)
        self.dataview.configure(yscroll=self.scroll_y.set)
        self.scroll_y.grid(row=1, column=1, sticky="ns") #Scrollbar next to Treeview
        
        
    def sqlConnection(self):
        import mysql.connector as sqltor
        try:
            mycon = sqltor.connect(host="localhost",user="root",passwd="ABCD1234",database="pythondb",port="3310")
            return mycon
        except sqltor.Error as e:
            msgbox(self, 'error','Connection Error',f"Error for Database Connection Occured: {e}")
    
        
    def startThread_displayRecords(self):
        try:
            threading.Thread(target=self.thread_displayRecords, args=(self.displayRecords,)).start()
        except Exception as e:
            msgbox('error','Internal Process Error',f"System Error for Display Record Process Occured: {e}")
    
    
    def thread_displayRecords(self, callback):
        con = self.sqlConnection()
        try:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM student;")
            result = cursor.fetchall()
            if result:
                self.after(0, callback, result)
            else:
                self.after(0, msgbox, 'warn', 'Empty Table', f"\nNo existing records !! Table is empty.\n")
        except Exception as e:
            self.after(0, msgbox, 'error', 'Display Record Error', f"Error for 'Display Record' Occured: {e}")
        finally:
            con.close()
    
    
    def displayRecords(self, record):
        #Remove existing rows before inserting
        self.dataview.delete(*self.dataview.get_children())
        
        #Defining colors for odd rows and even rows using tags
        self.dataview.tag_configure("evenrow", background="#E8E8E8")
        self.dataview.tag_configure("oddrow", background="lightgray")
        
        record = [list(row) for row in record]
        
        #Converting the date field to a string since it is originally in datetime.date() format
        import datetime
        for row in record:
            if type(row) is datetime.date:
                row = row.strftime("%Y-%m-%d")
        
        #Inserting data to treeview, and setting colors for alternating rows
        for i, row in enumerate(record): #Using enumerate to track index
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.dataview.insert("","end",values=row,tags=(tag,))
    
    
    def startThread_addRecord(self):
        #Getting the vaules from the widgets, and putting them into a list for dynamic processing
        record = []
        for widget in self.widgets:
            if isinstance(widget, DateEntry):
                record.append(widget.get_date().strftime("%Y-%m-%d"))
            else:
                record.append(widget.get())
        
        try:
            threading.Thread(target=self.thread_addRecord, args=(tuple(record),)).start()
        except Exception as e:
            msgbox('error','Internal Process Error',f"System Error for Add Record Process Occured: {e}")
    
    
    def thread_addRecord(self, record):
        con = self.sqlConnection()
        
        placeholders = ""
        fields = ""
        for i in range(len(self.query_fields)):
            if i > 0:
                placeholders += ", %s"
                fields += ", " + self.query_fields[i]
            else:
                placeholders += "%s"
                fields += self.query_fields[i]
        
        try:
            cursor = con.cursor()
            cursor.execute("SELECT roll from student where roll = %s;",(record[0],))
            result = cursor.fetchone()
            
            if result:
                self.after(0, msgbox, "warn", "Failure", "Cannot Insert Row !!\nA Record of the same Roll already exists.")
            else:
                cursor.execute(f"INSERT INTO student({fields}) VALUES({placeholders});",record)
                con.commit()
                self.after(0, msgbox, "info", "Success", "Record Added Successfully !!")
                
                #Remove existing entries from the widgets, and setting default values
                for widget in self.widgets:
                    widget.delete(0,"end")
        
        except Exception as e:
            msgbox("error", "Add Record Error", f"Error for 'Add Record' Occured: {e}")
            con.rollback()
        finally:
            con.close()
    
    
    def startThread_searchRecord(self):
        roll = self.widgets[0].get()
        try:
            threading.Thread(target=self.thread_searchRecord, args=(roll,)).start()
        except Exception as e:
            msgbox('error','Internal Process Error',f"System Error for Search Record Process Occured: {e}")
    
    
    def thread_searchRecord(self, roll):
        if not roll:
            self.after(0, msgbox, "icon", "Empty Input", "Roll is empty !!\nEnter a roll to proceed.")
            return
        
        con = self.sqlConnection()
        try:
            cursor = con.cursor()
            cursor.execute("SELECT * from student WHERE roll = %s;",(roll,))
            result = cursor.fetchall()
            if result:
                self.after(0, self.DisplayInGUI, result)
                self.after(0, lambda: self.modifyRec_btn.configure(state="enabled"))
                self.after(0, lambda: self.deleteRec_btn.configure(state="enabled"))
                #Using a variable to store the found roll, which is used in modifying & deleting record for this roll
                self.existing_roll = roll
                self.after(0, self.displayRecords, result)
                self.after(0, lambda: self.dataview_infoLabel.configure(text=f"Your requested data for Roll {roll}"))
            else:
                self.after(0, msgbox, "icon", "Not Found", f"No record found for the roll {roll}")
        except Exception as e:
            self.after(0, msgbox, "error", "Search Record Error", f"Error for 'Search Record' Occured: {e}")
        finally:
            con.close()
    
    
    def confirm_modifyRecord(self):
        self.modifyRec_btn.configure(state="disabled")
        from tkinter import messagebox
        response = messagebox.askquestion("Confirmation", "Are you sure you want to update this record ?")
        if response == "yes":
            self.startThread_modifyRecord()
        else:
            self.modifyRec_btn.configure(state="enabled")
    
    
    def startThread_modifyRecord(self):
        
        self.modifyRec_btn.configure(state="disabled")
        record = []
        
        #Using a loop to get the data from the widgets except the Roll Widget
        for widget in self.widgets[1:]:
            
            #If the widget is DateEntry then getting data from it using it's specific functions
            if isinstance(widget, DateEntry):
                record.append(widget.get_date().strftime("%Y-%m-%d"))
            else:
                record.append(widget.get())
        
        try:
            threading.Thread(target=self.thread_modifyRecord, args=(record,)).start()
        except Exception as e:
            msgbox('error','Internal Process Error',f"System Error for Modify Record Process Occured: {e}")


    def thread_modifyRecord(self, record):
        con = self.sqlConnection()
        
        try:
            #Dynamically generating the field placehorder part(field = %s) of SQL query
            field_placeholders = ""
            for index ,item in enumerate(self.query_fields[1:]):
                if index > 0:
                    field_placeholders += ", " + item + "=%s"
                else:
                    field_placeholders += item + "=%s"
            sql = "UPDATE student SET " + field_placeholders + " WHERE roll = %s;"
            
            #Adding the roll parameter value at the last, and converting to tuple to avoid cursor.execute() issues
            values = tuple(record) + (self.existing_roll,)
            
            cursor = con.cursor()
            cursor.execute(sql, values)
            con.commit()
            self.after(0, msgbox, "info", "Successfull", "Record Updated Successfully !!\n(Except Roll No)")
            
        except Exception as e:
            self.after(0, msgbox, "error", "Modify Record Error", f"Error for 'Modify Record' Occured: {e}")
            con.rollback()
            
        finally:
            con.close()
    
    
    def DisplayInGUI(self, record):
        #Remove existing rows before inserting
        self.dataview.delete(*self.dataview.get_children())
        
        #Converting input data to list to avoid tuple modification errors
        record = list(record[0])
        
        #Iterating through all widgets to set text(or value) to them
        import datetime
        for i, field_data in enumerate(record): #Using enumerate to track index
            if type(field_data) is datetime.date:
                self.widgets[i].set_date(field_data.strftime("%d-%m-%Y"))
            else:
                self.widgets[i].delete(0, "end")  # Clear existing text
                self.widgets[i].insert(0, field_data)    
    
    
    #Function to confirm delete record
    def confirm_deleteRecord(self):
        self.deleteRec_btn.configure(state="disabled")
        from tkinter import messagebox
        response = messagebox.askquestion("Confirmation", "Are you sure you want to delete this record ?")
        if response == "yes":
            self.startThread_deleteRecord()
        else:
            self.deleteRec_btn.configure(state="enabled")
    
    
    #Function to initiate the actual task of deleting record
    def startThread_deleteRecord(self):
        try:
            threading.Thread(target=self.thread_deleteRecord, args=(self.existing_roll,)).start()
        except Exception as e:
                msgbox('error','Internal Process Error',f"System Error for Delete Record Process Occured: {e}")
            
    
    #Function performing the task of deleting record
    def thread_deleteRecord(self, roll):
        con = self.sqlConnection()
        try:
            cursor = con.cursor()
            cursor.execute("DELETE FROM student WHERE roll = %s;",(roll,))
            con.commit()
            self.after(0, msgbox, "info", "Successfull", "Record Deleted Successfully !!")
        except Exception as e:
            self.after(0, msgbox, "error", "Delete Record Error", f"Error for 'Delete Record' Occured: {e}")
            con.rollback()
        finally:
            con.close()
    
    
    def exitApp(self):
        print(self.table)
        return
        from tkinter import messagebox
        response = messagebox.askquestion("Confirmation", "Are you sure you want to close the application ?")
        if response == "yes":
            self.destroy()
            
            
if __name__ == "__main__":
    app = SQLApp()
    app.mainloop()