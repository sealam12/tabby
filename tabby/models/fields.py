from tabby.models.field import Field

class StringField(Field):
    def __init__(self, *, max_length=1000, **kwargs):
        super().__init__("TEXT", **kwargs)  # Call the parent class's __init__
        self.max_length = max_length