class Field:
    def __init__(self, sql_type, **kwargs):
        self.sql_type = sql_type
    
    @property
    def value(self):
        return "E"
    
    @value.setter
    def value(self, new_value):
        print("set")