from django.contrib import admin

from .models import User, PerevalAdded, Coords, PerevalImage, PerevalAreas, SprActivitiesTypes

# Register your models here.
admin.site.register(User)
admin.site.register(PerevalAdded)
admin.site.register(Coords)
admin.site.register(PerevalImage)
admin.site.register(PerevalAreas)
admin.site.register(SprActivitiesTypes)