uiconfig = {
    "col_name" : "",
    "col_pos" : 0,
    "is_null" : "YES",
    "default" : None,
    "col_dtype" : "",
    "col_type" : "",
    "char_max_len" : 0,
    "num_max_len" : 0
}

import mysql.connector as sqltor
import pandas as pd
import numpy as np
import os, json

con = sqltor.connect(host="localhost", user="root", passwd="ABCD1234", port="3310")
cursor = con.cursor()

table = "student"
database = "pythondb"

query = "SELECT \
COLUMN_NAME, ORDINAL_POSITION, IS_NULLABLE, \
COLUMN_DEFAULT, DATA_TYPE, COLUMN_TYPE, \
CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION \
FROM INFORMATION_SCHEMA.COLUMNS \
WHERE TABLE_NAME = %s \
AND TABLE_SCHEMA = %s \
ORDER BY ORDINAL_POSITION;"""

print(query)
print()

cursor.execute(query, (table, database))
result = cursor.fetchall()
result = [tuple(map(lambda x: x.decode() if isinstance(x, bytes) else x, row)) for row in result]

df = pd.DataFrame(result, columns=uiconfig.keys())
df = df.replace(np.nan, None)

print(df)

for col in df.columns:
    uiconfig[col] = list(df[col])

print()

""" for key, value in uiconfig.items():
    print(key, value) """

def setUiConfigJsonFields(self=None):
    uiconfig["widget"] = []
    uiconfig["dtype"] = []
    uiconfig["sql_placeholder"] = []
    uiconfig["widget_state"] = []
    

def getWidgetConfig(col_dtype: list):
    
    filepath = os.path.join(os.path.dirname(__file__), "widgetconfig.json")
    
    with open(filepath, 'r') as file:
        config = json.load(file)
        
    widget_data = []
    for dtype in col_dtype:
        for _, value in config.items():
            if dtype.upper() in value["sql_dtype"]:
                #Store the widget specific info in the uiconfig dict accurately
                uiconfig["widget"].append(value["widget"])
                uiconfig["dtype"].append(value["dtype"])
                uiconfig["sql_placeholder"].append(value["sql_placeholder"])
                uiconfig["widget_state"].append(value["widget_state"])
                break


setUiConfigJsonFields()
getWidgetConfig(uiconfig["col_dtype"])

for key, value in uiconfig.items():
    print(f"{key} : {value}")
    print()


def msgbox(self):
    print("Invalid Widget Entry")

def validate_Widget_Entry(self, widget_pos:int, value:str):
    index = widget_pos
    
    if uiconfig["is_null"][index] == "NO":
        if value == "":
            self.after(0, msgbox, "warn", "Empty Widget Value", f"The widget at serial position {widget_pos} cannot be left empty !!")
    
    if uiconfig["char_max_len"][index] != None:
        pass
    
    if uiconfig["num_max_len"][index] != None:
        pass