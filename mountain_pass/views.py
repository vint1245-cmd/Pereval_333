from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from .models import PerevalAdded
from .serializers import PerevalAddedSerializer, PerevalDetailSerializer


class PerevalAddedViewSet(viewsets.ModelViewSet):
    queryset = PerevalAdded.objects.all()
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_serializer_class(self):
        """
        Используем разные сериализаторы для разных действий:
        - Detail и Status используют PerevalDetailSerializer (read-only)
        - Create и Update используют PerevalAddedSerializer
        """
        if self.action in ['retrieve', 'status', 'my_submits']:
            return PerevalDetailSerializer
        return PerevalAddedSerializer

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH: Редактирование перевала
        Проверяем статус перед редактированием
        """
        instance = self.get_object()
        
        # Проверка статуса
        if instance.status != 'new':
            return Response(
                {
                    'message': 'Редактирование возможно только для объектов со статусом "new".',
                    'current_status': instance.status,
                    'id': instance.id
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """
        GET /api/v1/submitData/{id}/status/
        
        Возвращает статус модерации конкретного перевала
        """
        try:
            obj = self.get_object()
        except PerevalAdded.DoesNotExist:
            raise NotFound(
                detail={
                    'message': 'Объект с указанным ID не найден.'
                }
            )
        
        serializer = self.get_serializer(obj)
        return Response({
            'id': obj.id,
            'status': obj.status,
            'title': obj.title,
            'beauty_title': obj.beauty_title,
            'add_time': obj.add_time,
            'user_email': obj.user.email
        })

    @action(detail=False, methods=['get'])
    def my_submits(self, request):
        """
        GET /api/v1/submitData/my_submits/?user__email=example@mail.com
        
        Возвращает все перевалы, отправленные пользователем, со статусами модерации
        """
        email = request.query_params.get('user__email')
        
        if not email:
            return Response(
                {
                    'message': 'Параметр "user__email" обязателен.',
                    'example': '/api/v1/submitData/my_submits/?user__email=tourist@example.com'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Получаем все перевалы пользователя, отсортированные по времени (новые первыми)
        queryset = self.get_queryset().filter(
            user__email=email
        ).order_by('-add_time')
        
        if not queryset.exists():
            return Response(
                {
                    'message': 'Перевалы для указанного email не найдены.',
                    'email': email,
                    'count': 0,
                    'results': []
                },
                status=status.HTTP_200_OK
            )
        
        serializer = self.get_serializer(queryset, many=True)
        
        # Возвращаем сводную информацию по статусам
        status_counts = {
            'new': queryset.filter(status='new').count(),
            'pending': queryset.filter(status='pending').count(),
            'accepted': queryset.filter(status='accepted').count(),
            'rejected': queryset.filter(status='rejected').count(),
        }
        
        return Response({
            'count': queryset.count(),
            'email': email,
            'status_summary': status_counts,
            'results': serializer.data
        })
