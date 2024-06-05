from django.db import models
from django.contrib.auth.models import User


class Book(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)  # dec_plcs - сколько после запятой
    author = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL,  # когда юзер удалится owner будет = null
                              null=True, related_name="my_books")  # user.my_books
    readers = models.ManyToManyField(User, related_name="books",
                                     through="UserBookRelation")  # through - модель отношения между полями

    def __str__(self):
        return f"{self.title}: {self.price}₽"


class UserBookRelation(models.Model):  # лайки, закладки
    RATE_CHOICE = (
        (1, "Bad"),
        (2, "Not good"),
        (3, "Good"),
        (4, "Great"),
        (5, "Perfect"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)
    in_bookmarks = models.BooleanField(default=False)
    rate = models.PositiveSmallIntegerField(choices=RATE_CHOICE, null=True)
    comment = models.CharField(max_length=250, null=True)

    def __str__(self):
        return f"{self.user.username}: {self.book.title}, RATE {self.rate}"
