from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from store.models import Book
from store.serializers import BookSerializer


class BookApiTestCase(APITestCase):
    def setUp(self):
        self.book1 = Book.objects.create(title='Test_book_1', price=1444, author="Author 1")
        self.book2 = Book.objects.create(title='Test_book_2', price=52, author="BAuthor 4")
        self.book3 = Book.objects.create(title='Test_book author1', price=52, author="Author 2")

    def test_get(self):
        """Тестирование GET-запроса"""

        url = reverse('book-list') # /book/
        response = self.client.get(url)  # get с клиента на url
        
        serializer_data = BookSerializer([self.book1, self.book2, self.book3], many=True).data  # сериализует переданные элементы

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)

        print(f'serializer_data: {serializer_data}')

    def test_get_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'price': 52}) # data - URI

        serializer_data = BookSerializer([self.book2, self.book3], many=True).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'Author 1'}) # проверяем что ищет в названии и авторе
        
        serializer_data = BookSerializer([self.book1, self.book3], many=True).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)

    def test_get_ordering_by_price(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': 'price'})
        
        serializer_data = BookSerializer([self.book2, self.book3, self.book1], many=True).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)

    def test_get_ordering_by_author(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': 'author'})
        
        serializer_data = BookSerializer([self.book1, self.book3, self.book2], many=True).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)
