from django.contrib import admin
from .models import User, Subscription


admin.site.register(Subscription)
admin.site.register(User)
