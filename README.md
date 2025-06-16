# View the `SQL_DynamicApp.py` file to get the main code for the project.
## The main idea of the project is this (step by step):
- A database connection form opens which connects to any mysql database and the table too.
- After the connection is made the app goes through the metadata of the columns in the table.
- Based on the column data type the application creates tkinter (or customtkinter) fields which suits the column's data type. View the `widgetconfig.json` file to see how it would be done.
- Then normal CRUD operation will happen dynamically as usual.

## The idea has been tested to work by me. I just have to finalize and optimize the project
