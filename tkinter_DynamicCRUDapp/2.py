import mysql.connector as sqltor

def enum_values(data):
    import re
    
    # Decode bytes to string
    if isinstance(data, bytes):
        data = data.decode()
    
    # Extract values inside enum()
    match = re.search(r"enum\((.*?)\)", data)
    if match:
        values = match.group(1)
        return [val.strip().strip("'") for val in values.split(",")]
    else:
        return

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

cursor.execute(query, (table, database))
result = cursor.fetchall()
for item in result:
    print(item)
    #print(item[5], enum_values(item[5]))
    print()
