from django.contrib import admin
from .models import CUser
from django.contrib.auth.models import Group

class CUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_admin', 'is_staff', 'is_superuser')
    list_filter = ('is_admin', 'is_staff', 'is_superuser')
    search_fields = ('email', 'first_name', 'last_name', 'roll_no')
    ordering = ('email',)
    exclude = ('password',)

    def get_form(self, request, obj=None, **kwargs):
        form = super(CUserAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields.pop('password', None)  # Exclude the password field from the form
        return form
    def has_add_permission(self, request, obj=None):
        return False

admin.site.register(CUser, CUserAdmin)
admin.site.unregister(Group)
