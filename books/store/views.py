from django.shortcuts import render
from django.db.models import Count, Case, When, Avg, F

from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import UpdateModelMixin
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated

from .permissions import IsOwnerOrStaffOrReadOnly
from .models import Book, UserBookRelation
from .serializers import BookSerializer, UserBookRelationSerializer


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all().annotate(  # annotate это весь запрос + поле annotated_likes
        annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
        rating=Avg('userbookrelation__rate'),
        price_with_discount=(F('price') - F('discount')),).order_by("id")
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    permission_classes = [IsOwnerOrStaffOrReadOnly]
    filterset_fields = ['price']
    search_fields = ['title', 'author']
    ordering_fields = ['price', 'author']

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class UserBookRelationViewSet(UpdateModelMixin, GenericViewSet):
    queryset = UserBookRelation.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserBookRelationSerializer
    lookup_field = 'book'  # так просто /book/<pk>, а щас /book/<book>

    def get_object(self):  # переопределяем метод получения объекта
        obj, created = UserBookRelation.objects.get_or_create(user=self.request.user,
                                                              book_id=self.kwargs["book"])  # обращаемся из lookup_field
        print(f'was created: {created}')
        return obj  # получили объект relation, получив айдишник book


def auth(request):
    return render(request, 'oauth.html')
