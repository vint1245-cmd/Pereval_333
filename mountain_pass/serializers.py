from rest_framework import serializers
from .models import User, Coords, Level, PerevalAdded, PerevalImage


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'fam', 'name', 'otc', 'phone']
        # Всегда защищаем данные пользователя от редактирования
        read_only_fields = ['email', 'fam', 'name', 'otc', 'phone']

    def to_internal_value(self, data):
        """При создании нового перевала проверяем/создаём пользователя"""
        email = data.get('email')
        if not email:
            raise serializers.ValidationError({"email": "Это поле обязательно."})

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return super().to_internal_value(data)

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
        fields = ['id', 'data', 'title']

    def to_representation(self, img_data):
        representation = super().to_representation(img_data)
        representation['data'] = img_data.data.url
        return representation


class PerevalAddedSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и редактирования перевалов"""
    user = UserSerializer()
    coords = CoordsSerializer()
    level = LevelSerializer()
    images = PerevalImageSerializer(many=True)
    images_to_delete = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False)

    class Meta:
        model = PerevalAdded
        fields = [
            'id',
            'beauty_title',
            'title',
            'other_titles',
            'connect',
            'add_time',
            'user',
            'coords',
            'level',
            'images',
            'images_to_delete',
            'status',
        ]
        read_only_fields = ['id', 'add_time', 'status', 'user', 'coords']

    def validate(self, data):
        """Проверка на этапе валидации"""
        request = self.context.get('request')
        
        # При редактировании (PATCH) проверяем статус
        if request and request.method in ['PATCH', 'PUT']:
            instance = self.instance
            if instance and instance.status != 'new':
                raise serializers.ValidationError({
                    "status": f"Редактирование возможно только при статусе 'new'. "
                              f"Текущий статус: '{instance.status}'"
                })
        
        return data

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        coords_data = validated_data.pop('coords')
        level_data = validated_data.pop('level')
        images_data = validated_data.pop('images')
        validated_data.pop('images_to_delete', None)  # Игнорируем при создании

        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults={
                'fam': user_data['fam'],
                'name': user_data['name'],
                'otc': user_data.get('otc'),
                'phone': user_data.get('phone'),
            }
        )

        coords = Coords.objects.create(**coords_data)
        level = Level.objects.create(**level_data)
        pereval_added = PerevalAdded.objects.create(
            user=user, coords=coords, level=level, **validated_data
        )

        for image_data in images_data:
            PerevalImage.objects.create(
                pereval=pereval_added, 
                data=image_data['data'], 
                title=image_data['title']
            )

        return pereval_added

    def update(self, pereval, validated_data):
        """Обновление перевала с проверкой статуса"""
        
        # Повторная проверка статуса перед обновлением
        if pereval.status != 'new':
            raise serializers.ValidationError({
                "status": f"Редактирование возможно только при статусе 'new'. "
                          f"Текущий статус: '{pereval.status}'"
            })
        
        coords_data = validated_data.pop('coords', None)
        level_data = validated_data.pop('level', None)
        images_data = validated_data.pop('images', None)
        images_to_delete = validated_data.pop('images_to_delete', [])

        # Обновляем основные поля перевала
        pereval.beauty_title = validated_data.get('beauty_title', pereval.beauty_title)
        pereval.title = validated_data.get('title', pereval.title)
        pereval.other_titles = validated_data.get('other_titles', pereval.other_titles)
        pereval.connect = validated_data.get('connect', pereval.connect)

        # Обновляем координаты и уровни
        if coords_data:
            CoordsSerializer().update(pereval.coords, coords_data)
        if level_data:
            LevelSerializer().update(pereval.level, level_data)

        # Обрабатываем изображения
        if images_data:
            for image_data in images_data:
                image_id = image_data.get('id', None)
                if image_id:
                    try:
                        image_pereval = PerevalImage.objects.get(id=image_id)
                        PerevalImageSerializer().update(image_pereval, image_data)
                    except PerevalImage.DoesNotExist:
                        pass
                else:
                    PerevalImage.objects.create(pereval=pereval, **image_data)

        # Удаляем изображения по ID
        if images_to_delete:
            for image_id in images_to_delete:
                try:
                    image = PerevalImage.objects.get(id=image_id)
                    image.delete()
                except PerevalImage.DoesNotExist:
                    pass

        pereval.save()
        return pereval


class PerevalDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра деталей и статуса перевала"""
    user = UserSerializer()
    coords = CoordsSerializer()
    level = LevelSerializer()
    images = PerevalImageSerializer(source='pereval_images', many=True)

    class Meta:
        model = PerevalAdded
        fields = [
            'id',
            'beauty_title',
            'title',
            'other_titles',
            'connect',
            'add_time',
            'user',
            'coords',
            'level',
            'images',
            'status'
        ]
        read_only_fields = [
            'id', 'add_time', 'status', 'user', 'coords', 'level', 'images'
        ]
