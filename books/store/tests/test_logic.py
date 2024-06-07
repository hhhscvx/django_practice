from django.test import TestCase
from store.models import Book, UserBookRelation
from store.services import set_rating
from django.contrib.auth.models import User

class SetRatingTestCase(TestCase):
    def setUp(self):
        user1 = User.objects.create(username="username1", first_name="Ivan", last_name="Petrov")
        user2 = User.objects.create(username="username2", first_name="Ivan", last_name="Sidorov")
        user3 = User.objects.create(username="username3", first_name="1", last_name="2")
        self.book1 = Book.objects.create(title='Test_book_1', price=25,
                                    author="author1", discount=4, owner=user1)
        book2 = Book.objects.create(title='Test_book_2', price=22, author="author2", owner=user2)

        UserBookRelation.objects.create(book=self.book1, user=user1, like=True, rate=2)
        UserBookRelation.objects.create(book=self.book1, user=user2, like=True, rate=5)
        UserBookRelation.objects.create(book=self.book1, user=user3, like=True, rate=5)

        UserBookRelation.objects.create(book=self.book1, user=user1, like=False)
        UserBookRelation.objects.create(book=book2, user=user2, like=True, rate=3)
        UserBookRelation.objects.create(book=book2, user=user3, like=True, rate=4)

    def test_ok(self):
        set_rating(self.book1)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.rating, 4.00)
