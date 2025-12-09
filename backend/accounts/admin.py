from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User

    # list_display should only include fields that exist on your User model
    list_display = ('email', 'is_admin', 'is_volunteer', 'is_staff', 'is_active')
    
    # list_filter should also refer to real fields
    list_filter = ('is_admin', 'is_volunteer', 'is_staff', 'is_active')
    
    #  ordering by email since username no longer exists
    ordering = ('email',)
    
    # search_fields should only reference real fields
    search_fields = ('email',)

    # fieldsets adjusted for custom user
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {
            'fields': ('is_admin', 'is_volunteer', 'is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')
        }),
    )

    # add_fieldsets adjusted for creating new users
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_admin', 'is_volunteer', 'is_staff', 'is_active')
        }),
    )

# Register the custom user admin
admin.site.register(User, CustomUserAdmin)
