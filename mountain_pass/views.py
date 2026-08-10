from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from django.db import transaction

from .models import PerevalAdded, User, Image
from .serializers import PerevalAddedSerializer


def index(request):
    """Главная страница"""
    return render(request, 'index.html')


class PerevalCreateView(APIView):
    """POST /api/v1/submitData - создание новой записи"""
    
    def post(self, request):
        try:
            data = request.data
            
            # Получаем или создаём пользователя
            user_data = data.get('user')
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'fam': user_data['fam'],
                    'name': user_data['name'],
                    'otc': user_data['otc'],
                    'phone': user_data['phone']
                }
            )
            
            coords = data.get('coords')
            level = data.get('level', {})
            
            with transaction.atomic():
                pereval = PerevalAdded.objects.create(
                    beauty_title=data.get('beauty_title'),
                    title=data.get('title'),
                    other_titles=data.get('other_titles'),
                    connect=data.get('connect'),
                    user=user,
                    latitude=coords.get('latitude'),
                    longitude=coords.get('longitude'),
                    height=coords.get('height'),
                    winter=level.get('winter'),
                    summer=level.get('summer'),
                    autumn=level.get('autumn'),
                    spring=level.get('spring'),
                    status='new'
                )
                
                # Добавляем фотографии
                images = data.get('images', [])
                for image_data in images:
                    Image.objects.create(
                        pereval=pereval,
                        image=image_data.get('data'),
                        title=image_data.get('title')
                    )
            
            return Response({
                "status": 200,
                "message": "Данные успешно добавлены",
                "id": pereval.id
            }, status=status.HTTP_200_OK)
            
        except KeyError as e:
            return Response({
                "status": 400,
                "message": f"Отсутствует обязательное поле: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": 500,
                "message": f"Ошибка сервера: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PerevalDetailUpdateView(APIView):
    """
    GET /api/v1/submitData/<id> - получить запись по ID
    PATCH /api/v1/submitData/<id> - редактировать запись
    """
    
    def get(self, request, id):
        try:
            pereval = PerevalAdded.objects.get(id=id)
            serializer = PerevalAddedSerializer(pereval)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PerevalAdded.DoesNotExist:
            return Response(
                {"error": f"Перевал с id {id} не найден"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def patch(self, request, id):
        try:
            pereval = PerevalAdded.objects.get(id=id)
            
            if pereval.status != 'new':
                return Response({
                    "state": 0,
                    "message": f"Редактирование возможно только для объектов со статусом 'new'. "
                              f"Текущий статус: '{pereval.status}'"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            data = request.data.copy()
            
            with transaction.atomic():
                pereval.beauty_title = data.get('beauty_title', pereval.beauty_title)
                pereval.title = data.get('title', pereval.title)
                pereval.other_titles = data.get('other_titles', pereval.other_titles)
                pereval.connect = data.get('connect', pereval.connect)
                pereval.add_time = data.get('add_time', pereval.add_time)
                
                if 'coords' in data:
                    coords = data['coords']
                    pereval.latitude = coords.get('latitude', pereval.latitude)
                    pereval.longitude = coords.get('longitude', pereval.longitude)
                    pereval.height = coords.get('height', pereval.height)
                
                if 'level' in data:
                    level = data['level']
                    pereval.winter = level.get('winter', pereval.winter)
                    pereval.summer = level.get('summer', pereval.summer)
                    pereval.autumn = level.get('autumn', pereval.autumn)
                    pereval.spring = level.get('spring', pereval.spring)
                
                pereval.save()
                
                if 'images_to_delete' in data:
                    images_to_delete = data['images_to_delete']
                    Image.objects.filter(id__in=images_to_delete, pereval=pereval).delete()
                
                if 'images' in data:
                    for image_data in data['images']:
                        if 'data' in image_data and 'title' in image_data:
                            Image.objects.create(
                                pereval=pereval,
                                image=image_data['data'],
                                title=image_data['title']
                            )
            
            return Response({
                "state": 1,
                "message": "Запись успешно отредактирована"
            }, status=status.HTTP_200_OK)
            
        except PerevalAdded.DoesNotExist:
            return Response({
                "state": 0,
                "message": f"Перевал с id {id} не найден"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "state": 0,
                "message": f"Ошибка при редактировании: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PerevalListByEmailView(APIView):
    """GET /api/v1/submitData/?user__email=<email> - список перевалов пользователя"""
    
    def get(self, request):
        try:
            email = request.query_params.get('user__email')
            
            if not email:
                return Response(
                    {"error": "Параметр 'user__email' обязателен"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            users = User.objects.filter(email=email)
            
            if not users.exists():
                return Response({
                    "count": 0,
                    "results": [],
                    "message": f"Пользователь с email '{email}' не найден"
                }, status=status.HTTP_200_OK)
            
            perevals = PerevalAdded.objects.filter(user__in=users)
            serializer = PerevalAddedSerializer(perevals, many=True)
            
            return Response({
                "count": perevals.count(),
                "results": serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
