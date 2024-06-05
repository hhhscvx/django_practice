from django.db import models
from django.contrib.auth.models import User


class Book(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)  # dec_plcs - сколько после запятой
    author = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, # когда юзер удалится owner будет = null
                               null=True)

    def __str__(self):
        return f"{self.title}: {self.price}₽"
