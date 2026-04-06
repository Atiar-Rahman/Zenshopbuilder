from django.contrib import admin
from users.models import User,Profile,Company
from django.contrib.auth.admin import UserAdmin
# Register your models here.

admin.site.register(Profile)
admin.site.register(Company)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display=('email', 'first_name', 'last_name', 'is_active')
    list_filter = ('is_staff', 'is_active', 'is_superuser')

    ordering = ('email',)
    search_fields = ('email', 'first_name', 'last_name')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {
            'fields': ('first_name', 'last_name')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )

    readonly_fields = ('last_login', 'date_joined')