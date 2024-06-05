from django.contrib import admin
from .models import Book, UserBookRelation


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_filter = ['price', 'title']
    search_fields = ['title']
    list_display = ['title', 'price']


@admin.register(UserBookRelation)
class UserBookRelationAdmin(admin.ModelAdmin):
    list_filter = ['user', 'book',
                   'like', 'rate']
    search_fields = ['user', 'book', 'rate']
    list_display = ['user', 'book',
                    'like', 'in_bookmarks', 'rate']
