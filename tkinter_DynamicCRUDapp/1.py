import os
import customtkinter as ctk
import tkinter as tk
from tkcalendar import DateEntry

def enum_values(data):
    import re
    
    # Extract values inside enum()
    match = re.search(r"enum\((.*?)\)", data)
    if match:
        values = match.group(1)
        return [val.strip().strip("'") for val in values.split(",")]

def getWidgetFunction(dtype: str):
    import json
    
    try:
        filepath = os.path.join(os.path.dirname(__file__), "widgetconfig.json")
        with open(filepath, 'r') as file:
            config = json.load(file)
        
        for _ , value in config.items():
            if dtype.upper() in value['sql_dtype']:
                return value['widget']
        
    except Exception as e:
        print(f"Error -\n{e}")

#dict = ["char", "int", "date", "enum", "varchar", "enum", "date", "mediumtext", "text", "decimal", "numeric"]

import mysql.connector as sqltor
con = sqltor.connect(host="localhost", user="root", passwd="ABCD1234", port="3310")
cursor = con.cursor()

table = "student"
database = "pythondb"

query = "SELECT \
COLUMN_NAME, ORDINAL_POSITION, IS_NULLABLE, \
COLUMN_DEFAULT, DATA_TYPE, COLUMN_TYPE, \
CHARACTER_MAXIMUM_LENGTH,NUMERIC_PRECISION \
FROM INFORMATION_SCHEMA.COLUMNS \
WHERE TABLE_NAME = %s \
AND TABLE_SCHEMA = %s \
ORDER BY ORDINAL_POSITION;"

print(query)

enumValues = []
dict = []
cursor.execute(query, (table, database))
result = cursor.fetchall()
result = [tuple(map(lambda x: x.decode() if isinstance(x, bytes) else x, row)) for row in result]

for item in result:
    if item[4].upper() == "ENUM":
        dict.append( getWidgetFunction(item[4]) )
        enumValues.append(enum_values(item[5]))
    else:
        dict.append( getWidgetFunction(item[4]) )


for item in dict:
    print(item)

uiconfig = []

root = ctk.CTk()
root.geometry("400x400")

widget_frame = ctk.CTkScrollableFrame(root, label_text="Data Entry Frame", border_color="white")
widget_frame.pack(fill='x')
widget_frame._parent_canvas.pack_propagate(False)

ncols = 0
for col in range(2):
    ncols += 1
    widget_frame.grid_columnconfigure(col)


#widgets = list(map(getWidgetFunction, dict))
widgets = dict
print(widgets)

widget_objs = []
enum_widget_ctr = 0
row_no = 0
col_no = 0
for item in widgets:
    
    if col_no == ncols:
        col_no = 0
        row_no += 1
    
    # Creating the label for the widget
    label = ctk.CTkLabel(widget_frame, text="Prompt to the user:", anchor='w')
    label.grid(row=row_no, column=col_no, padx=5, pady=5, ipadx=5, ipady=5, sticky="new")
    col_no += 1
    
    # Creating the widget
    if item == "ctk.CTkComboBox":
        widget_func = eval(item)
        widget = widget_func(widget_frame, values=enumValues[enum_widget_ctr], state="readonly")
        widget.set(enumValues[enum_widget_ctr][0])
        enum_widget_ctr += 1
    else:
        widget_func = eval(item)
        widget = widget_func(widget_frame)
        
    widget.grid(row=row_no, column=col_no, padx=5, pady=5, ipadx=5, ipady=5, sticky="new")
    
    widget_objs.append(widget)
    
    col_no += 1
    #Increasing counter for accurate column placement of widgets
    #ctr += 1

root.mainloop()


""" with open(filepath, 'r') as file:
    config = json.load(file)
    
    for key, value in config.items():
        temp = []
        temp.append(value['sql_dtype'])
        temp.append(value['widget'])
        uiconfig.append(temp)
    
    for item in uiconfig:
        print(item)
    
    ctr = 0
    for dtype in dict:
        for item in uiconfig:
            if dtype.upper() in item[0]:
                label = tk.Label(widget_frame, text="Prompt to the user a long text to wrap:", anchor='w')
                label.grid(row = ctr, column=0, padx=5, pady=5, ipadx=5, ipady=5, sticky="nsew")
                
                widget_func = eval(item[1])
                widget = widget_func(widget_frame)
                widget.grid(row = ctr, column=2, padx=5, pady=5, ipadx=5, ipady=5, sticky="nsew")
                
                ctr += 1
                
                print(item[1], f"- {dtype}")
                break
        
root.mainloop() """