from django.contrib import admin

from user.models import User, Subscribe


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username',)
    list_filter = ('email', 'username')
    fields = (('first_name', 'last_name'), 'username', 'email', 'password')


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    pass
