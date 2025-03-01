import model

model.User.create_table()
m = model.User.get(id=1)
m.username = "sealy"
m.save()