from rest_framework import serializers
from .models import Book, UserBookRelation
from django.contrib.auth.models import User


class BookReaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class BookSerializer(serializers.ModelSerializer):
    annotated_likes = serializers.IntegerField(read_only=True)
    min_rate = serializers.IntegerField(read_only=True)
    max_rate = serializers.IntegerField(read_only=True)
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    in_bookmarks_count = serializers.IntegerField(read_only=True)
    price_with_discount = serializers.DecimalField(max_digits=7, decimal_places=2, read_only=True)

    owner_name = serializers.CharField(read_only=True)
    readers = BookReaderSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = ('id', 'title', 'price', 'author', 'discount', 
                  'price_with_discount', 'annotated_likes', 'min_rate',
                  'max_rate', 'rating', 'in_bookmarks_count', 'owner_name', 'readers')


class UserBookRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBookRelation
        fields = ('book', 'like', 'in_bookmarks', 'rate', 'comment')
