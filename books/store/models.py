from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2) # dec_plcs - сколько после запятой
    author = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.title}: {self.price}₽"
