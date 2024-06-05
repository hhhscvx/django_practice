from django.test import TestCase
from store.models import Book, UserBookRelation
from store.serializers import BookSerializer
from django.contrib.auth.models import User


class BookSerializerTestCase(TestCase):
    """Тестирование, верно ли работает сериализатор"""

    def test_ok(self):
        user1 = User.objects.create(username="username1")
        user2 = User.objects.create(username="username2")
        user3 = User.objects.create(username="username3")
        book1 = Book.objects.create(title='Test_book_1', price=25, author="author1")
        book2 = Book.objects.create(title='Test_book_2', price=22, author="author2")

        UserBookRelation.objects.create(book=book1, user=user1, like=True)
        UserBookRelation.objects.create(book=book1, user=user2, like=True)
        UserBookRelation.objects.create(book=book1, user=user3, like=True)

        UserBookRelation.objects.create(book=book1, user=user1, like=False)
        UserBookRelation.objects.create(book=book2, user=user2, like=True)
        UserBookRelation.objects.create(book=book2, user=user3, like=True)

        data = BookSerializer([book1, book2], many=True).data
        expected_data = [
            {
                'id': book1.id,
                'title': 'Test_book_1',
                'price': '25.00',
                'author': 'author1',
                'likes_count': 3,
            },
            {
                'id': book2.id,
                'title': 'Test_book_2',
                'price': '22.00',
                'author': 'author2',
                'likes_count': 2,
            }
        ]

        self.assertEqual(expected_data, data)
