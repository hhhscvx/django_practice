from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from store.models import Book
from store.serializers import BookSerializer


class BookApiTestCase(APITestCase):
    """Тестирование GET-запроса"""
    def test_get(self):
        book1 = Book.objects.create(title='Test_book_1', price=25)
        book2 = Book.objects.create(title='Test_book_2', price=22)

        url = reverse('book-list') # /book/
        response = self.client.get(url)  # get с клиента на url
        
        serializer_data = BookSerializer([book1, book2], many=True).data  # сериализует переданные элементы

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)

        print(f'serializer_data: {serializer_data}')
