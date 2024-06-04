from django.test import TestCase
from store.models import Book
from store.serializers import BookSerializer


class BookSerializerTestCase(TestCase):
    """Тестирование, верно ли работает сериализатор"""

    def test_ok(self):
        book1 = Book.objects.create(title='Test_book_1', price=25, author="author1")
        book2 = Book.objects.create(title='Test_book_2', price=22, author="author2")

        data = BookSerializer([book1, book2], many=True).data
        expected_data = [
            {
                'id': book1.id,
                'title': 'Test_book_1',
                'price': '25.00',
                'author': 'author1'
            },
            {
                'id': book2.id,
                'title': 'Test_book_2',
                'price': '22.00',
                'author': 'author2'
            }
        ]

        self.assertEqual(expected_data, data)
