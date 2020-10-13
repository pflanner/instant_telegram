from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from pics.models import Photo, User, UserFollow


admin.site.register(Photo)
admin.site.register(User, UserAdmin)
admin.site.register(UserFollow)
