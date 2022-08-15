from tortoise import fields, models


class User(models.Model):
    id = fields.UUIDField(pk=True)
    first_name = fields.CharField(max_length=50)
    last_name = fields.CharField(max_length=75)
    email = fields.CharField(max_length=125, unique=True)
    password = fields.CharField(max_length=330)
    data_of_birth = fields.DateField()
    is_active = fields.BooleanField(default=True)