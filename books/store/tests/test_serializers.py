from django.test import TestCase
from store.models import Book, UserBookRelation
from store.serializers import BookSerializer
from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg, Min, Max, F


class BookSerializerTestCase(TestCase):
    """Тестирование, верно ли работает сериализатор"""

    def test_ok(self):
        user1 = User.objects.create(username="username1")
        user2 = User.objects.create(username="username2")
        user3 = User.objects.create(username="username3")
        book1 = Book.objects.create(title='Test_book_1', price=25, author="author1", discount=4)
        book2 = Book.objects.create(title='Test_book_2', price=22, author="author2")

        UserBookRelation.objects.create(book=book1, user=user1, like=True, rate=2)
        UserBookRelation.objects.create(book=book1, user=user2, like=True, rate=5)
        UserBookRelation.objects.create(book=book1, user=user3, like=True, rate=5)

        UserBookRelation.objects.create(book=book1, user=user1, like=False)
        UserBookRelation.objects.create(book=book2, user=user2, like=True, rate=3)
        UserBookRelation.objects.create(book=book2, user=user3, like=True, rate=4)

        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            in_bookmarks_count=Count(Case(When(userbookrelation__in_bookmarks=True, then=1))),
            price_with_discount=(F('price') - F('discount')),
            rating=Avg('userbookrelation__rate'),
            min_rate=Min('userbookrelation__rate'),
            max_rate=Max('userbookrelation__rate')
        ).order_by("id")
        data = BookSerializer(books, many=True).data
        expected_data = [
            {
                'id': book1.id,
                'title': 'Test_book_1',
                'price': '25.00',
                'author': 'author1',
                'discount': '4.00',
                'price_with_discount': '21.00',
                'likes_count': 3,
                'annotated_likes': 3,
                'min_rate': 2,
                'max_rate': 5,
                'rating': '4.00',
                'in_bookmarks_count': 0,
            },
            {
                'id': book2.id,
                'title': 'Test_book_2',
                'price': '22.00',
                'author': 'author2',
                'discount': '0.00',
                'price_with_discount': '22.00',
                'likes_count': 2,
                'annotated_likes': 2,
                'min_rate': 3,
                'max_rate': 4,
                'rating': '3.50',
                'in_bookmarks_count': 0
            }
        ]
        print(f'data: {data}')
        print(f'expected_data: {expected_data}')
        self.assertEqual(expected_data, data)
