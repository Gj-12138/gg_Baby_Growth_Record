from django.contrib import admin

from users.models import Baby, User


# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass

@admin.register(Baby)
class BabyAdmin(admin.ModelAdmin):
    pass




