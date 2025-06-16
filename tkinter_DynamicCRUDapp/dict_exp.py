class UiConfig(dict):
    def __init__(self, database=None, table=None):
        super().__init__()
        
        self.uiconfig = {"configkey" : "configvalue"}
        
        #Store the database and table in a separate variable
        self.database = database
        self.table = table
        
        self["key1"] = "value1"
        
        self.getMetadata()
    
    def getMetadata(self):
        pass

obj = UiConfig()
print(obj)
obj["key2"] = "value2"
print(obj)
print(obj.uiconfig)