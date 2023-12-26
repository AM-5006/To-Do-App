from django.contrib import admin
from django.utils.translation import gettext_lazy  as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import UserAdmin
from  django.contrib.auth.models  import  Group

from .models import User, Task
# Register your models here.

class customUserAdmin(UserAdmin):
  fieldsets = (
      (None, {'fields': ('username', 'email', 'password', )}),
      (_('Personal info'), {'fields': ('first_name', 'last_name')}),
      (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',"is_verified",
                                     'groups', 'user_permissions'),}),
      (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('user_info'), {'fields': ( 'phone_no',)}),
  )
  list_display = ['username', 'email', "is_verified"]
  # ordering = ('username', )

admin.site.register(User, customUserAdmin)
admin.site.unregister(Group)

admin.site.register(Task)