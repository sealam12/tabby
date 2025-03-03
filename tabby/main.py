import tabby.models.model as model

m = model.User.get(id=1)
m.username = m.username == "sealy" and "sealy_dev" or "sealy"
m.save()

print(model.User.filter(password="Iloveseals1"))