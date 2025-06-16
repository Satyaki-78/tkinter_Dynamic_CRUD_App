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
        elif icon == 'error':
            messagebox.showerror(title,msg, parent=parent)


class WidgetConfig(dict):
    def __init__(self, col_dtypes: list):
        #Dictionary to store metadata about widgets
        #Will be used for read, write and validate data from the widgets
        self.widgetconfig = {}
        
        #Variable to store the column data types of a table
        self.col_dtype_list = col_dtypes
        
        self.__jsonData = self.getJSONFileData()
        self.init_self()
        self.getWidgetConfigFromJSON()

    @property
    def widgetConfig(self):
        return self
    
    def getJSONFileData(self):
        import json
        filepath = os.path.join(os.path.dirname(__file__), "widgetconfig.json")
        with open(filepath, 'r') as file:
            return json.load(file)
    
    def init_self(self):
        for _, value in self.__jsonData.items():
            for subkey, _ in value.items():
                self[subkey] = []
        del self['sql_dtype']
    
    def getWidgetConfigFromJSON(self):
        try:
            #1st loop
            for dtype in self.col_dtype_list:
                #2nd loop
                for _, value in self.__jsonData.items():
                    if dtype.upper() in value['sql_dtype']:
                        #3rd loop
                        #Write data to self if dtype is matched
                        for subkey, subvalue in value.items():
                            if subkey != "sql_dtype":
                                self[subkey].append(subvalue)
                        #Stop the 2nd for loop when the data write is done after dtype match
                        break
        #Set config dictionary to None at time of error to prevent invalid processing of the config dict
        except Exception as e:
            self = None


class SQLConfig(dict):
    def __init__(self, sqlcon, table):
        super().__init__()
        #Store the database, table and primary key in a separate variable
        self.con = sqlcon
        self.database = self.con.database
        self.table = table
        
        #Query to get the metadata of a table
        self.__query = "SELECT \
            COLUMN_NAME, ORDINAL_POSITION, IS_NULLABLE, \
            COLUMN_DEFAULT, DATA_TYPE, COLUMN_TYPE, \
            CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION \
            FROM INFORMATION_SCHEMA.COLUMNS \
            WHERE TABLE_NAME = %s \
            AND TABLE_SCHEMA = %s \
            ORDER BY ORDINAL_POSITION;"""
        #Removing spaces from the query to avoid query execution errors
        self.__query = ' '.join(self.__query.split())
        
        self.init_self()
        self.getMetadata()
    
    @property
    def sqlConfig(self):
        return self
    
    def init_self(self):
        self["col_name"] = ""
        self["col_pos"] = 0
        self["is_null"] = "YES"
        self["default"] = None
        self["col_dtype"] = ""
        self["col_type"] = ""
        self["char_max_len"] = 0
        self["num_max_len"] = 0
    
    def getMetadata(self):
        print(self.__query)
        cursor = self.con.cursor()
        cursor.execute(self.__query,(self.table, self.database))
        result = cursor.fetchall()
        result = [tuple(map(lambda x: x.decode() if isinstance(x, bytes) else x, row)) for row in result]
        
        import pandas as pd
        import numpy as np
        df = pd.DataFrame(result, columns=self.keys())
        df = df.replace(np.nan, None)
        
        for col in df.columns:
            self[col] = list(df[col])
        
        del cursor, result, df
        """ for key, value in self.items():
            print(key,":",value) """


class InsertRecord:
    pass

class SearchRecord:
    pass

class CreateRecord:
    pass

class DeleteRecord:
    pass

class DisplayAllRecords:
    pass


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
    
    con = None
    table = ""
    tableList = []
    widgets = []
    
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
        #self.widgets = []
        
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
        
        self.connectDB_btn = ctk.CTkButton(db_table_btnFrame, text="Connect to Database", command=self.open_DBConnectWindow)
        self.connectDB_btn.grid(row=0, column=0, padx=5, pady=5, sticky="nse")
        
        self.changeTable_btn = ctk.CTkButton(db_table_btnFrame, text="Change Table", command=self.changeTable)
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
    
    def open_DBConnectWindow(self):
        dbConWindow = SQLConnectionWindow(self)
        dbConWindow.mainloop()
    
    def changeTable(self):
        window_change_table = ChangeTableWindow(self)
        window_change_table.mainloop()
    
    def createUiConfigDict(self):
        self.__uiconfig = {
            "col_name" : "",
            "col_pos" : 0,
            "is_null" : "YES",
            "default" : None,
            "col_dtype" : "",
            "col_type" : "",
            "char_max_len" : 0,
            "num_max_len" : 0
        }
        
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
        print("Current Database:", self.con.database)
        print("Current Table", self.table)
        return
        from tkinter import messagebox
        response = messagebox.askquestion("Confirmation", "Are you sure you want to close the application ?")
        if response == "yes":
            self.destroy()
    


class SQLConnectionWindow(ctk.CTk):
    
    con = None
    
    def __init__(self, master):
        super().__init__()
        self.master = master
        width = int(self.master._current_width * 0.5)
        self_x = (self.master._current_width - width) // 2
        center_x = self.master.winfo_x() + self_x
        self.geometry(f"{width}x{self.master._current_height}+{center_x}+{self.master.winfo_y()}")
        
        for i in range(4):
            self.grid_columnconfigure(i, weight=1)
        
        self.initUI()
        
    
    def initUI(self):
        #Basic connection frame
        self.frame1 = ctk.CTkFrame(self,border_color="green",border_width=2)
        self.frame1.pack(fill="x", ipadx=5, ipady=5, pady=10)
        
        for col in range(4):
            self.frame1.grid_columnconfigure(col, weight=1)
        
        #Host Label
        self.host_label = ctk.CTkLabel(self.frame1, text="Host:")
        self.host_label.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        #Host Entry
        self.host_entry = ctk.CTkEntry(self.frame1)
        self.host_entry.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        #User Label
        self.user_label = ctk.CTkLabel(self.frame1, text="User:")
        self.user_label.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        #User Entry
        self.user_entry = ctk.CTkEntry(self.frame1)
        self.user_entry.grid(row=0, column=3, padx=5, pady=5, sticky="nsew")
        
        #Password Label
        self.pswd_label = ctk.CTkLabel(self.frame1, text="Port:")
        self.pswd_label.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        #Port Entry
        self.port_entry = ctk.CTkEntry(self.frame1)
        self.port_entry.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        
        
        #Port Label
        self.port_label = ctk.CTkLabel(self.frame1, text="Password:")
        self.port_label.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")
        #Password Entry
        self.pswd_entry = ctk.CTkEntry(self.frame1)
        self.pswd_entry.grid(row=1, column=3, padx=5, pady=5, sticky="nsew")
        
        """Additional Connection String Parameters Input"""
        #Label
        self.additionalParams_label = ctk.CTkLabel(self.frame1, text="Additional Connection Parameters:")
        self.additionalParams_label.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        #Entry Widget
        self.additionalParams_entry = ctk.CTkEntry(self.frame1)
        self.additionalParams_entry.grid(row=2, column=2, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        #Server Connect Button
        self.connectSQLServer_btn = ctk.CTkButton(self.frame1, text="Connect to SQL Server", command=self.initialConnect)
        self.connectSQLServer_btn.grid(row=3, column=0, columnspan=4, padx=5, pady=5, sticky="ew")
        
        #Database selection frame
        self.frame2 = ctk.CTkFrame(self,border_color="green",border_width=2)
        self.frame2.pack(fill="x", ipadx=5, ipady=0, pady=10)
        
        for col in range(3):
            self.frame2.grid_columnconfigure(col, weight=1)
        
        #Daatbase label
        self.db_label = ctk.CTkLabel(self.frame2, text="Database:")
        self.db_label.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        #Database Combo Box
        self.db_combobox = ctk.CTkComboBox(self.frame2, state="readonly", values=[""])
        self.db_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="nsw")
        
        #Select Database Button
        self.selectDB_btn = ctk.CTkButton(self.frame2, text="Select", state="disabled", command=self.setDatabase)
        self.selectDB_btn.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        
        #Table selection frame
        self.frame3 = ctk.CTkFrame(self,border_color="green",border_width=2)
        self.frame3.pack(fill="x", ipadx=5, ipady=0, pady=10)
        
        for col in range(3):
            self.frame3.grid_columnconfigure(col, weight=1)
        
        #Table label
        self.table_label = ctk.CTkLabel(self.frame3, text="Table:")
        self.table_label.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        #Table Combo Box
        self.table_combobox = ctk.CTkComboBox(self.frame3, state="readonly", values=[""])
        self.table_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="nsw")
        
        #Select Table Button
        self.selectTable_btn = ctk.CTkButton(self.frame3, text="Select", state="disabled", command=self.useInitialTable)
        self.selectTable_btn.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        
        #Final Connect Button
        self.connect_btn = ctk.CTkButton(self, text="Connect", state="disabled", command=self.connect)
        self.connect_btn.pack(pady=15)
        
    
    def initialConnect(self):
        import mysql.connector as sqltor
        try:
            host = self.host_entry.get()
            user = self.user_entry.get()
            port = int(self.port_entry.get())
            pswd = self.pswd_entry.get()
            params = self.additionalParams_entry.get()
            kwargs = eval(f"dict({params})") if params else {}
            
            self.con = sqltor.connect(host=host, user=user, port=port, passwd=pswd, **kwargs)
            
            if self.con.is_connected():
                self.selectDB_btn.configure(state="normal")
                
                cursor = self.con.cursor()
                cursor.execute("SHOW DATABASES;")
                result = cursor.fetchall()
                if result:
                    dbList = []
                    for item in result:
                        dbList.append(item[0])
                    self.db_combobox.configure(values=dbList)
                else:
                    self.selectDB_btn.configure(command= lambda: msgbox('warn', 'Not Found', "No databases were found in this connection !!"))
        
        except Exception as e:
            print(e)
            msgbox("error", "Failure", f"Failed to Connect\n\nError - {e}", self)
    
    def setDatabase(self):
        try:
            database = self.db_combobox.get()
            self.con.database = database
            
            cursor = self.con.cursor()
            cursor.execute(f"SHOW TABLES FROM {database};")
            result = cursor.fetchall()
            if result:
                self.tableList = []
                for item in result:
                    self.tableList.append(item[0])
                self.table_combobox.configure(values=self.tableList)
                self.selectTable_btn.configure(state="normal")
            else:
                self.selectDB_btn.configure(command= lambda: msgbox('warn', 'Not Found', f"No tables were found in database {database} !!"))
                
        except Exception as e:
            msgbox("error", "Error", f"Database Selection Error - {e}", self)
        
    
    def useInitialTable(self):
        self.table = self.table_combobox.get()
        if self.table != "":
            self.connect_btn.configure(state="normal")
            self.master.table = self.table
    
    def connect(self):
        self.master.con = self.con
        self.master.tableList = self.tableList
        self.destroy()
    

class ChangeTableWindow(ctk.CTk):
    def __init__(self, master):
        super().__init__()
        self.master = master
        
        master_x = self.master.winfo_x()
        master_y = self.master.winfo_y()
        self_x = master_x + (self.master.winfo_width() - self.winfo_width()) // 2
        self_y = master_y + (self.master.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{self_x}+{self_y}")
        
        self.label = ctk.CTkLabel(self, text="Select Table:")
        self.label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.table_comboBox = ctk.CTkComboBox(self, state="readonly", values=self.master.tableList)
        self.table_comboBox.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        #Display the current table as the combo box value
        self.table_comboBox.set(self.master.table)
        
        self.selectTable_btn = ctk.CTkButton(self, text="Select", command=self.selectTable)
        self.selectTable_btn.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
    def selectTable(self):
        self.master.table = self.table_comboBox.get()
        self.destroy()


if __name__ == "__main__":
    #app = SQLApp()
    #app.mainloop()
    dict = ["char", "int", "date", "enum", "varchar", "enum", "date", "mediumtext", "text", "decimal", "numeric"]
    o = WidgetConfig(dict)
    print("Widget Config from JSON")
    config = o.widgetConfig
    for key, value in config.items():
        print(key,":",value)
        print()
    
    import mysql.connector as sqltor
    con = sqltor.connect(host="localhost", user="root", passwd="ABCD1234", port="3310")
    con.database = "pythondb"
    table = "student"
    s = SQLConfig(con, table)
    print(s.sqlConfig)