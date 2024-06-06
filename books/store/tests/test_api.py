from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg, F
from django.test.utils import CaptureQueriesContext
from django.db import connection

from store.models import Book, UserBookRelation
from store.serializers import BookSerializer
import json


class BookApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="test_username")
        self.book1 = Book.objects.create(title='Test_book_1', price=1444,
                                         author="Author 1", owner=self.user)
        self.book2 = Book.objects.create(title='Test_book_2', price=52,
                                         author="BAuthor 4", owner=self.user)
        self.book3 = Book.objects.create(title='Test_book author1', price=52,
                                         author="Author 2", owner=self.user)

        UserBookRelation.objects.create(book=self.book1, user=self.user, like=True, rate=5)

    def test_get(self):
        """Тестирование GET-запроса"""

        url = reverse('book-list')  # /book/
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(url)  # get с клиента на url
            self.assertEqual(2, len(queries))

        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            rating=Avg('userbookrelation__rate'),
            price_with_discount=(F('price') - F('discount')),
            owner_name=F('owner__username')).order_by("id")
        serializer_data = BookSerializer(books, many=True).data  # сериализует переданные элементы

        # print(f'serializer_data: {serializer_data}')
        # print(f'response.data: {response.data}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(serializer_data[0]['rating'], '5.00')
        self.assertEqual(serializer_data[0]['annotated_likes'], 1)

    def test_get_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'price': 52})  # data - URI

        books = Book.objects.filter(id__in=[self.book2.id, self.book3.id]).annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            rating=Avg('userbookrelation__rate'),
            price_with_discount=(F('price') - F('discount')),
            owner_name=F('owner__username')).order_by("id")
        serializer_data = BookSerializer(books, many=True).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'Author 1'})  # проверяем что ищет в названии и авторе

        books = Book.objects.filter(id__in=[self.book1.id, self.book3.id]).annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            rating=Avg('userbookrelation__rate'),
            price_with_discount=(F('price') - F('discount')),
            owner_name=F('owner__username'))
        serializer_data = BookSerializer(books, many=True).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)

    def test_get_ordering_by_price(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': 'price'})

        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            rating=Avg('userbookrelation__rate'),
            price_with_discount=(F('price') - F('discount')),
            owner_name=F('owner__username')).order_by("price")
        serializer_data = BookSerializer(books, many=True).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)

    def test_get_ordering_by_author(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': 'author'})

        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            rating=Avg('userbookrelation__rate'),
            price_with_discount=(F('price') - F('discount')),
            owner_name=F('owner__username')).order_by("author")
        serializer_data = BookSerializer(books, many=True).data

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
        print(f'response_data: {response.data}')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.all().count(), 4)
        self.assertEqual(self.user,  # проверка что юзер указался в owner
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

        self.assertEqual(self.book1.price, 1444)  # прайс не должен поменяться

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
        print(f'response.data: {response.data}')
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

        self.assertEqual(3, Book.objects.count())  # нихуя не удалилось

    def test_delete_not_owner(self):
        self.user2 = User.objects.create(username="fake_user", is_staff=True)
        self.assertEqual(3, Book.objects.count())

        url = reverse('book-detail', args=(self.book1.id,))

        self.client.force_login(self.user2)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(2, Book.objects.count())  # удалилось


class UserBookRelationApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="test_username")
        self.user2 = User.objects.create(username="test_username2")
        self.book1 = Book.objects.create(title='Test_book_1', price=1444,
                                         author="Author 1", owner=self.user)
        self.book2 = Book.objects.create(title='Test_book_2', price=52,
                                         author="Author 4", owner=self.user)

    def test_like(self):
        url = reverse('userbookrelation-detail',
                      args=(self.book1.id,))  # передали айдишник книги и по id юзера найдем их relation
        data = {"like": True}
        json_data = json.dumps(data)

        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,  # с patch можно просто передать изменения
                                     content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book1)
        self.assertTrue(relation.like)

        data = {"in_bookmarks": True}
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        relation.refresh_from_db()
        self.assertTrue(relation.in_bookmarks)

    def test_rate(self):
        url = reverse('userbookrelation-detail',
                      args=(self.book1.id,))
        data = {"rate": 1}
        json_data = json.dumps(data)

        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book1)
        self.assertEqual(relation.rate, 1)

    def test_rate_wrong(self):
        url = reverse('userbookrelation-detail',
                      args=(self.book1.id,))
        data = {"rate": 6}
        json_data = json.dumps(data)

        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         response.data)  # print(response.data) если тест упал

    def test_comment(self):
        url = reverse('userbookrelation-detail',
                      args=(self.book1.id,))
        data = {"comment": "Grate book! Like it"}
        json_data = json.dumps(data)

        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book1)
        relation.refresh_from_db()
        self.assertEqual(relation.comment, "Grate book! Like it")
