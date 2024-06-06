from rest_framework import serializers
from .models import Book, UserBookRelation


class BookSerializer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    annotated_likes = serializers.IntegerField(read_only=True)
    min_rate = serializers.IntegerField(read_only=True)
    max_rate = serializers.IntegerField(read_only=True)
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    in_bookmarks_count = serializers.IntegerField(read_only=True)
    price_with_discount = serializers.DecimalField(max_digits=7, decimal_places=2, read_only=True)

    class Meta:
        model = Book
        fields = ('id', 'title', 'price', 'author', 'discount', 'price_with_discount',
                  'likes_count', 'annotated_likes', 'min_rate',
                  'max_rate', 'rating', 'in_bookmarks_count',)

    def get_likes_count(self, instance):
        """Количество queryset запросов, где книге поставили лайк"""
        return UserBookRelation.objects.filter(book=instance, like=True).count()


class UserBookRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBookRelation
        fields = ('book', 'like', 'in_bookmarks', 'rate', 'comment')
