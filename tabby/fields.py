class Field:
    def __init__(self, sql_type, unique=False, notnull=True, default=None, primary_key=False):
        self.sql_type = sql_type
        self.unique = unique
        self.notnull = notnull
        self.default = None
        self.primary_key = primary_key
        
        self.constraints = []
        if unique: self.constraints.apppend("UNIQUE")
        if notnull: self.constraints.append("NOT NULL")
        if primary_key: self.constraints.append("PRIMARY KEY")
        
        if default:
            if isinstance(default, str):
                default = f"\"{default}\""
            self.constraints.append(f"DEFAULT {default}")
    
    def can_set(self, val):
        return True

class StringField(Field):
    def __init__(self, max_length=255, **kwargs):
        self.max_length = max_length
        super().__init__("TEXT", **kwargs)
    
    def can_set(self, val):
        if len(val) > self.max_length:
            return False
        else:
            return True

class IntegerField(Field):
    def __init__(self, **kwargs):
        super().__init__("INTEGER", **kwargs)

class ForeignKey(Field):
    def __init__(self, reference_class, **kwargs):
        self.reference_class = reference_class
        super().__init__("INTEGER", **kwargs)