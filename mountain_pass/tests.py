from django.test import TestCase
from .models import User, Coords, Level, PerevalAdded, PerevalImage
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse

# Create your tests here.


# Тестирование моделей
class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            email='test@example.com',
            fam='Иванов',
            name='Иван',
            otc='Иванович',
            phone='+1234567890'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.fam, 'Иванов')
        self.assertEqual(self.user.name, 'Иван')
        self.assertEqual(self.user.otc, 'Иванович')
        self.assertEqual(self.user.phone, '+1234567890')

class CoordsModelTest(TestCase):
    def setUp(self):
        self.coords = Coords.objects.create(latitude=12.345678, longitude=98.765432, height=100)

    def test_coords_creation(self):
        self.assertEqual(self.coords.latitude, 12.345678)
        self.assertEqual(self.coords.longitude, 98.765432)
        self.assertEqual(self.coords.height, 100)

class LevelModelTest(TestCase):
    def setUp(self):
        self.level = Level.objects.create(winter='1А', summer='2Б', autumn='3А', spring='1Б')

    def test_level_creation(self):
        self.assertEqual(self.level.winter, '1А')
        self.assertEqual(self.level.summer, '2Б')
        self.assertEqual(self.level.autumn, '3А')
        self.assertEqual(self.level.spring, '1Б')

class PerevalAddedModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='test@example.com', fam='Иванов', name='Иван')
        self.coords = Coords.objects.create(latitude=12.345678, longitude=98.765432)
        self.level = Level.objects.create(winter='1А')

        self.pereval = PerevalAdded.objects.create(
            user=self.user,
            coords=self.coords,
            level=self.level,
            title='Тестовый перевал'
        )

    def test_pereval_added_creation(self):
        self.assertEqual(self.pereval.title, 'Тестовый перевал')
        self.assertEqual(self.pereval.user, self.user)
        self.assertEqual(self.pereval.coords, self.coords)
        self.assertEqual(self.pereval.level, self.level)


# Тестирование API
class APITestCase(APITestCase):

    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'fam': 'Иванов',
            'name': 'Иван',
            'otc': 'Иванович',
            'phone': '+1234567890'
        }
        self.user = User.objects.create(**self.user_data)

        self.coords_data = {
            'latitude': 12.345678,
            'longitude': 98.765432,
            'height': 100
        }
        self.level_data = {
            'winter': '1А',
            'summer': '2Б',
            'autumn': '3А',
            'spring': '1Б'
        }

    def test_create_and_retrieve_pereval(self):
        # Создание нового PerevalAdded
        url = reverse('submit_data')

        data = {
            'beauty_title': 'Красивый перевал',
            'title': 'Тестовый перевал',
            'user': {
                'email': self.user_data['email'],
                'fam': self.user_data['fam'],
                'name': self.user_data['name'],
                'otc': self.user_data['otc'],
                'phone': self.user_data['phone']
            },
            'coords': self.coords_data,
            'level': self.level_data,
            'images': [
                {"data": "path/to/image1.jpg", "title": "Седловина"}
            ]
        }

        # Печатаем данные для отладки
        print("Отправляемые данные:", data)

        response = self.client.post(url, data, format='json')

        # Проверка ответа
        print("Ответ:", response.data)

        if response.status_code != status.HTTP_200_OK:
            print("Ошибки валидации:", response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверка, что объект создан в базе данных
        pereval = PerevalAdded.objects.get(title='Тестовый перевал')
        print("Созданный объект:", pereval)
        self.assertIsNotNone(pereval)

        # Проверяем, что данные перевала можно получить
        url = reverse('pereval_detail_update', kwargs={'id': pereval.id})
        response = self.client.get(url)

        # Печатаем ответ для отладки
        print("Ответ от GET:", response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['data']['title'], 'Тестовый перевал')
