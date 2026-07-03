from django.db import models
from django.core.validators import RegexValidator


# Create your models here.
class User(models.Model):
    email = models.EmailField(unique=True)
    fam = models.CharField(max_length=255, verbose_name='Фамилия')
    name = models.CharField(max_length=255, verbose_name='Имя')
    otc = models.CharField(max_length=255, blank=True, null=True, verbose_name='Отчество')

    # регулярное выражение допускает формат телефона с международным кодом, включая пробелы,
    # дефисы, точки, а также скобки вокруг кода региона.
    check_phone = RegexValidator(
        regex=r'^\+?(\d{1,3})?[-.\s]?\(?\d{1,3}\)?[-.\s]?\d{1,3}[-.\s]?\d{2,3}[-.\s]?\d{2,3}$',
        message="Номер телефона должен быть введён в корректном формате."
    )

    phone = models.CharField(
        validators=[check_phone],
        max_length=17,
        blank=True,
        null=True,
        verbose_name='Телефон'
    )

    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email


class Coords(models.Model):
    latitude = models.DecimalField(decimal_places=8, max_digits=10)
    longitude = models.DecimalField(decimal_places=8, max_digits=10)
    height = models.IntegerField(null=True)

    class Meta:
        verbose_name = "Координаты"
        verbose_name_plural = "Координаты"

    def __str__(self):
        return f"{self.latitude}, {self.longitude}, {self.height}"


class Level(models.Model):
    CHOICE_LEVEL = [
        ('', ''),
        ('1А', '1А'),
        ('1Б', '1Б'),
        ('2А', '2А'),
        ('2Б', '2Б'),
        ('3А', '3А'),
        ('3Б', '3Б'),
    ]

    winter = models.CharField(max_length=2, choices=CHOICE_LEVEL, default='',
                              blank=True, null=True, verbose_name='Зима')
    summer = models.CharField(max_length=2, choices=CHOICE_LEVEL, default='',
                              blank=True, null=True, verbose_name='Лето')
    autumn = models.CharField(max_length=2, choices=CHOICE_LEVEL, default='',
                              blank=True, null=True, verbose_name='Осень')
    spring = models.CharField(max_length=2, choices=CHOICE_LEVEL, default='',
                              blank=True, null=True, verbose_name='Весна')

    class Meta:
        verbose_name = "Уровень сложности"
        verbose_name_plural = "Уровни сложности"

    def __str__(self):
        return f'{self.winter}, {self.summer}, {self.autumn}, {self.spring}'

class PerevalAdded(models.Model):
    CHOICE_STATUS = [
        ("new", 'новый'),
        ("pending", 'модератор взял в работу'),
        ("accepted", 'модерация прошла успешно'),
        ("rejected", 'модерация прошла, информация не принята'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coords = models.OneToOneField(Coords, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE, blank=True, null=True)

    beauty_title = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255)
    other_titles = models.CharField(max_length=255, blank=True, null=True)
    connect = models.TextField(blank=True, null=True)
    add_time = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=30, choices=CHOICE_STATUS, default="new")

    # Добавляем связь с таблицей PerevalArea
    # Это позволит указывать, в какой географической области находится конкретный перевал.
    # Но в итоговом JSON теле запроса с информацией о перевале этих данных нет...
    area = models.ForeignKey('PerevalAreas', on_delete=models.SET_NULL, null=True, blank=True)

    # Добавляем связь "многие ко многим" с таблицей SprActivitiesTypes
    # (перевал можно пройти пешком или на лыжах, а каждый вид активности может быть применим к нескольким перевалам)
    # Но в итоговом JSON теле запроса с информацией о перевале этих данных нет...
    activities = models.ManyToManyField('SprActivitiesTypes', blank=True)

    class Meta:
        verbose_name = "Перевал"
        verbose_name_plural = "Перевалы"

    def __str__(self):
        return self.title


class PerevalImage(models.Model):
    pereval = models.ForeignKey(PerevalAdded, on_delete=models.CASCADE,
                                related_name='pereval_images', verbose_name='Изображения')
    date_added = models.DateTimeField(auto_now_add=True)
    data = models.ImageField(upload_to='pereval_images/%Y/%m/%d/')
    title = models.CharField(max_length=255, verbose_name='Название изображения')

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"

    def __str__(self):
        return self.img_path.name


class PerevalAreas(models.Model):
    title = models.CharField(max_length=255)
    id_parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name = "Район перевала"
        verbose_name_plural = "Районы перевалов"

    def __str__(self):
        return self.title


class SprActivitiesTypes(models.Model):
    title = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Вид активности"
        verbose_name_plural = "Виды активности"

    def __str__(self):
        return self.title
