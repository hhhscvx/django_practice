from django.test import TestCase
from store.models import Book, UserBookRelation
from store.serializers import BookSerializer
from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg, Min, Max, F
from unittest.mock import patch


class BookSerializerTestCase(TestCase):
    """Тестирование, верно ли работает сериализатор"""

    def test_ok(self):
        self.user1 = User.objects.create(username="username1", first_name="Ivan", last_name="Petrov")
        user2 = User.objects.create(username="username2", first_name="Ivan", last_name="Sidorov")
        user3 = User.objects.create(username="username3", first_name="1", last_name="2")
        self.book1 = Book.objects.create(title='Test_book_1', price=25,
                                    author="author1", discount=4, owner=self.user1)
        book2 = Book.objects.create(title='Test_book_2', price=22, author="author2", owner=user2)

        UserBookRelation.objects.create(book=self.book1, user=self.user1, like=True, rate=2)
        UserBookRelation.objects.create(book=self.book1, user=user2, like=True, rate=5)
        UserBookRelation.objects.create(book=self.book1, user=user3, like=True, rate=5)

        user_book_3 = UserBookRelation.objects.create(book=self.book1, user=user3, like=True)
        user_book_3.rate = 4
        user_book_3.save()

        UserBookRelation.objects.create(book=self.book1, user=self.user1, like=False)
        UserBookRelation.objects.create(book=book2, user=user2, like=True, rate=3)
        UserBookRelation.objects.create(book=book2, user=user3, like=True, rate=4)

        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            in_bookmarks_count=Count(Case(When(userbookrelation__in_bookmarks=True, then=1))),
            price_with_discount=(F('price') - F('discount')),
            min_rate=Min('userbookrelation__rate'),
            max_rate=Max('userbookrelation__rate'),
            owner_name=F('owner__username')
        ).order_by("id")
        data = BookSerializer(books, many=True).data
        expected_data = [
            {
                'id': self.book1.id,
                'title': 'Test_book_1',
                'price': '25.00',
                'author': 'author1',
                'discount': '4.00',
                'price_with_discount': '21.00',
                'annotated_likes': 4,
                'min_rate': 2,
                'max_rate': 5,
                'rating': '4.00',
                'in_bookmarks_count': 0,
                'owner_name': 'username1',
                'readers': [
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Petrov',
                    },
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Sidorov',
                    },
                    {
                        'first_name': '1',
                        'last_name': '2',
                    },
                    {
                        'first_name': '1',
                        'last_name': '2',
                    },
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Petrov',
                    },
                ]
            },
            {
                'id': book2.id,
                'title': 'Test_book_2',
                'price': '22.00',
                'author': 'author2',
                'discount': '0.00',
                'price_with_discount': '22.00',
                'annotated_likes': 2,
                'min_rate': 3,
                'max_rate': 4,
                'rating': '3.50',
                'in_bookmarks_count': 0,
                'owner_name': 'username2',
                'readers': [
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Sidorov',
                    },
                    {
                        'first_name': '1',
                        'last_name': '2',
                    }
                ]
            }
        ]
        print(f'data: {data}')
        print(f'expected_data: {expected_data}')
        self.assertEqual(expected_data, data)


    @patch('store.services.set_rating')
    def test_set_rating_not_called(self, mock_set_rating):
        """Хз как в тестах сделать проверку, в которой was_create не будет равен True"""
        user = User.objects.create(username='vasya')
        book = Book.objects.create(title='Test_set_rating_book', price=25, author='asd', discount=4)
        relation = UserBookRelation(user=user, book=book, rate=3)
        
        relation.rate = 4
        relation.save()

        mock_set_rating.assert_called_once_with(book)

        relation.rate = 3
        relation.save()

        mock_set_rating.assert_not_called()
