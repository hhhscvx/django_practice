from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
import json
from decimal import Decimal

from store.models import Book
from store.serializers import BookSerializer


class BookApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="test_username")
        self.book1 = Book.objects.create(title='Test_book_1', price=1444,
                                         author="Author 1", owner=self.user)
        self.book2 = Book.objects.create(title='Test_book_2', price=52,
                                         author="BAuthor 4", owner=self.user)
        self.book3 = Book.objects.create(title='Test_book author1', price=52,
                                         author="Author 2", owner=self.user)

    def test_get(self):
        """Тестирование GET-запроса"""

        url = reverse('book-list')  # /book/
        response = self.client.get(url)  # get с клиента на url

        serializer_data = BookSerializer([self.book1, self.book2, self.book3],
                                         many=True).data  # сериализует переданные элементы

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)

        print(f'serializer_data: {serializer_data}')

    def test_get_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'price': 52})  # data - URI

        serializer_data = BookSerializer([self.book2, self.book3], many=True).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'Author 1'})  # проверяем что ищет в названии и авторе

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

    def test_create(self):
        self.assertEqual(Book.objects.all().count(), 3)
        url = reverse('book-list')

        data = {"title": "Путь Джедая",
                "price": 1500,
                "author": "Максим Дорофеев"}
        json_data = json.dumps(data)

        self.client.force_login(self.user)
        response = self.client.post(url,
                                    data=json_data, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.all().count(), 4)
        self.assertEqual(self.user, # проверка что юзер указался в owner
                          Book.objects.last().owner)

    def test_update(self):
        url = reverse('book-detail', args=(self.book1.id,))

        data = {"title": self.book1.title,
                "price": 675,
                "author": self.book1.author}
        json_data = json.dumps(data)

        self.client.force_login(self.user)
        response = self.client.put(url,
                                   data=json_data, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.book1.refresh_from_db()

        self.assertEqual(self.book1.price, 675)

    def test_update_not_owner(self):
        self.user2 = User.objects.create(username="fake_user",)
        url = reverse('book-detail', args=(self.book1.id,))

        data = {"title": self.book1.title,
                "price": 675,
                "author": self.book1.author}
        json_data = json.dumps(data)

        self.client.force_login(self.user2)
        response = self.client.put(url,
                                   data=json_data, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.book1.refresh_from_db()

        self.assertEqual(self.book1.price, 1444) # прайс не должен поменяться

    def test_update_not_owner_but_staff(self):
        self.user2 = User.objects.create(username="fake_user", is_staff=True)
        url = reverse('book-detail', args=(self.book1.id,))

        data = {"title": self.book1.title,
                "price": 675,
                "author": self.book1.author}
        json_data = json.dumps(data)

        self.client.force_login(self.user2)
        response = self.client.put(url,
                                   data=json_data, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.book1.refresh_from_db()

        self.assertEqual(self.book1.price, 675)

    def test_delete(self):
        self.assertEqual(3, Book.objects.count())

        url = reverse('book-detail', args=(self.book1.id,))

        self.client.force_login(self.user)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(2, Book.objects.count())

    def test_delete_not_owner(self):
        self.user2 = User.objects.create(username="fake_user")
        self.assertEqual(3, Book.objects.count())

        url = reverse('book-detail', args=(self.book1.id,))

        self.client.force_login(self.user2)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(3, Book.objects.count()) # нихуя не удалилось

    def test_delete_not_owner(self):
        self.user2 = User.objects.create(username="fake_user", is_staff=True)
        self.assertEqual(3, Book.objects.count())

        url = reverse('book-detail', args=(self.book1.id,))

        self.client.force_login(self.user2)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(2, Book.objects.count()) # удалилось
