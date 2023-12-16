from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscription, User


class SubscriptionInline(admin.TabularInline):
    model = Subscription
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name',
                    'is_staff')
    list_filter = ('username', 'email')
    inlines = (SubscriptionInline,)


admin.site.register(User, CustomUserAdmin)
admin.site.register(Subscription)
