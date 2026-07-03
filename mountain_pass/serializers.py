from rest_framework import serializers
from .models import User, Coords, Level, PerevalAdded, PerevalImage


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'fam', 'name', 'otc', 'phone']

    def to_internal_value(self, data):
        # Проверяем, существует ли пользователь с данным email
        email = data.get('email')
        if not email:
            raise serializers.ValidationError({"email": "Это поле обязательно."})

        # Пытаемся найти пользователя с этим email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Если пользователь не найден, возвращаем данные для создания нового
            return super().to_internal_value(data)

        # Если пользователь найден, возвращаем его
        return {
            'email': user.email,
            'fam': user.fam,
            'name': user.name,
            'otc': user.otc,
            'phone': user.phone,
        }


class CoordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coords
        fields = ['latitude', 'longitude', 'height']


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ['winter', 'summer', 'autumn', 'spring']


class PerevalImageSerializer(serializers.ModelSerializer):
    data = serializers.CharField(write_only=True)

    class Meta:
        model = PerevalImage
        fields = ['id', 'data', 'title']        # Добавьте поле id для удаления

    def to_representation(self, img_data):
        # Здесь мы определяем, как будет выглядеть объект при сериализации
        representation = super().to_representation(img_data)
        representation['data'] = img_data.data.url  # Получаем URL для изображения
        return representation


class PerevalAddedSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    coords = CoordsSerializer()
    level = LevelSerializer()
    images = PerevalImageSerializer(many=True)
    images_to_delete = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False)  # Вспомогательное поле

    class Meta:
        model = PerevalAdded
        # fields = '__all__'
        fields = [
            'beauty_title',
            'title',
            'other_titles',
            'connect',
            'add_time',
            'user',
            'coords',
            'level',
            'images',
            'images_to_delete',         # Поле для удаления изображений по идентификатору
        ]

    # Отладка - проверка какое поле вызывает ошибку
    # def validate(self, data):
    #     # Отладка типа данных
    #     if not isinstance(data.get('user'), dict):
    #         raise serializers.ValidationError(f"user: Ожидался dictionary, получен {type(data.get('user'))}")
    #     if not isinstance(data.get('coords'), dict):
    #         raise serializers.ValidationError(f"coords: Ожидался dictionary, получен {type(data.get('coords'))}")
    #     if not isinstance(data.get('images'), list):
    #         raise serializers.ValidationError(f"images: Ожидался list, получен {type(data.get('images'))}")
    #     if not isinstance(data.get('level'), dict):
    #         raise serializers.ValidationError(f"level: Ожидался dictionary, получен {type(data.get('level'))}")
    #
    #     return data

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        coords_data = validated_data.pop('coords')
        level_data = validated_data.pop('level')
        images_data = validated_data.pop('images')

        # Добавляем пользователя, если его нет
        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults={
                'fam': user_data['fam'],
                'name': user_data['name'],
                'otc': user_data.get('otc'),
                'phone': user_data.get('phone'),
            }
        )

        # Добавляем координаты
        coords = Coords.objects.create(**coords_data)

        # Добавляем уровни сложности
        level = Level.objects.create(**level_data)

         # Добавление записи Перевала
        pereval_added = PerevalAdded.objects.create(user=user, coords=coords, level=level, **validated_data)

        # Обработка изображений
        for image_data in images_data:
            PerevalImage.objects.create(pereval=pereval_added, data=image_data['data'], title=image_data['title'])

        return pereval_added

    def update(self, pereval, validated_data):
        coords_data = validated_data.pop('coords', None)
        level_data = validated_data.pop('level', None)
        images_data = validated_data.pop('images', None)

        pereval.beauty_title = validated_data.get('beauty_title', pereval.beauty_title)
        pereval.title = validated_data.get('title', pereval.title)
        pereval.other_titles = validated_data.get('other_titles', pereval.other_titles)
        pereval.connect = validated_data.get('connect', pereval.connect)

        CoordsSerializer().update(pereval.coords, coords_data)
        LevelSerializer().update(pereval.level, level_data)

        for image_data in images_data:
            image_id = image_data.get('id', None)
            if image_id:
                image_pereval = PerevalImage.objects.get(id=image_id)
                PerevalImageSerializer().update(image_pereval, image_data)
            else:
                PerevalImage.objects.create(pereval=pereval, **image_data)

        # Удаление изображений, если указаны идентификаторы
        images_to_delete = validated_data.pop('images_to_delete', [])
        if images_to_delete:
            for image_id in images_to_delete:
                try:
                    image = PerevalImage.objects.get(id=image_id)
                    image.delete()
                except PerevalImage.DoesNotExist:
                    continue  # Игнорируем, если изображение не найдено

        pereval.save()  # Сохраняем изменения в PerevalAdded
        return pereval


class PerevalDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    coords = CoordsSerializer()
    level = LevelSerializer()
    # Используем source='pereval_images' для получения связанных изображений
    images = PerevalImageSerializer(source='pereval_images', many=True)

    class Meta:
        model = PerevalAdded
        fields = [
            'beauty_title',
            'title',
            'other_titles',
            'connect',
            'add_time',
            'user',
            'coords',
            'level',
            'images',
            'status'  # Также добавим статус модерации
        ]
