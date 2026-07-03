from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateAPIView
from rest_framework.views import APIView

from .models import PerevalAdded
from .serializers import PerevalAddedSerializer, PerevalDetailSerializer


# Обработка POST-запроса для создания записи
class PerevalCreateView(CreateAPIView):
    serializer_class = PerevalAddedSerializer

    def post(self, request, *args, **kwargs):
        serializer = PerevalAddedSerializer(data=request.data)
        if serializer.is_valid():
            try:
                pereval_added = serializer.save()
                return Response({
                    "status": 200,
                    "message": "успех",
                    "id": pereval_added.id
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    "status": 500,
                    "message": f"Ошибка при выполнении операции: {str(e)}",
                    "id": None
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                "status": 400,
                "message": "Bad Request (не корректные данные)",
                "errors": serializer.errors,  # Отслеживаем ошибки сериализатора
                "id": None
            }, status=status.HTTP_400_BAD_REQUEST)


# Обработка GET и PATCH-запросов для получения и редактирования записи
class PerevalDetailUpdateView(RetrieveUpdateAPIView):
    serializer_class = PerevalAddedSerializer
    lookup_field = 'id'     # Указываем правильное поле для поиска, т.к. по умолчанию lookup_field является pk

    def get_queryset(self):
        # Получаем id из URL параметров
        pereval_id = self.kwargs.get('id')

        # Если id передан, фильтруем по нему, иначе возвращаем все объекты
        if pereval_id:
            return PerevalAdded.objects.filter(id=pereval_id)
        return PerevalAdded.objects.all()

    def get_object(self):
        # Переопределяем get_object, чтобы управлять поведением, когда объект не найден
        queryset = self.get_queryset()
        filter_kwargs = {self.lookup_field: self.kwargs[self.lookup_field]}
        try:
            return queryset.get(**filter_kwargs)
        except PerevalAdded.DoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        pereval = self.get_object()  # Используем наш переопределенный метод
        if pereval is None:
            return Response({
                "status": 404,
                "message": "Перевал не найден.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = PerevalDetailSerializer(pereval)  # Используем другой сериализатор для GET запроса
        return Response({
            "status": 200,
            "message": "успех",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        pereval = self.get_object()
        if pereval is None:  # Проверка, существует ли объект для PATCH
            return Response({
                "status": 404,
                "message": "Перевал не найден.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        # Проверяем статус
        if pereval.status != 'new':
            return Response({
                "state": 0,
                "message": "Редактирование доступно только для записей со статусом 'new'."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Получаем сериализатор с данными запроса
        serializer = self.get_serializer(pereval, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "state": 1,
            "message": "Запись успешно отредактирована."
        }, status=status.HTTP_200_OK)


# Обработка GET-запроса для получения записи (в данном случае по email)
class PerevalListByEmailView(ListAPIView):
    serializer_class = PerevalDetailSerializer

    def get_queryset(self):
        email = self.request.query_params.get('user__email', None)  # Получаем email из параметров запроса
        if email:
            return PerevalAdded.objects.filter(user__email=email)
        return PerevalAdded.objects.none()  # Возвращаем пустой queryset, если email не указан

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Проверяем, найден ли хотя бы один объект
        if not queryset.exists():
            return Response({
                "status": 404,
                "message": "Email не найден или записи отсутствуют",
                "data": []
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": 200,
            "message": "успех",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


# Главная страница
def index(request):
    return render(request, 'index.html')