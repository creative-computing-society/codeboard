from django.contrib import admin
from django import forms
from .models import CUser
from django.contrib.auth.models import Group

class CUserAdminForm(forms.ModelForm):
    class Meta:
        model = CUser
        fields = '__all__'

class CUserAdmin(admin.ModelAdmin):
    form = CUserAdminForm
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_admin', 'is_staff', 'is_superuser')
    list_filter = ('is_admin', 'is_staff', 'is_superuser')
    search_fields = ('email', 'first_name', 'last_name', 'roll_no')
    ordering = ('email',)
    exclude = ('password',)

    def get_form(self, request, obj=None, **kwargs):
        form = super(CUserAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields.pop('password', None)  # Exclude the password field from the form
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        return readonly_fields + ('login_password',)

    def has_add_permission(self, request, obj=None):
        return False

admin.site.register(CUser, CUserAdmin)
admin.site.unregister(Group)