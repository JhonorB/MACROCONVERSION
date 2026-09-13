from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Empresa, CuentaCompra, FrecuenciaCuenta, CacheDeuda, SesionProceso, AsignacionCuenta, PerfilUsuario

class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil de Usuario'

class UserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'ruc', 'razon_social', 'usuario', 'created_at')
    search_fields = ('codigo', 'ruc', 'razon_social')

@admin.register(CuentaCompra)
class CuentaCompraAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descripcion')
    search_fields = ('codigo', 'descripcion')

@admin.register(FrecuenciaCuenta)
class FrecuenciaCuentaAdmin(admin.ModelAdmin):
    list_display = ('ruc_proveedor', 'cuenta', 'usuario', 'frecuencia')
    search_fields = ('ruc_proveedor', 'cuenta__codigo')

@admin.register(CacheDeuda)
class CacheDeudaAdmin(admin.ModelAdmin):
    list_display = ('ruc', 'usuario', 'tiene_deuda', 'consultado_en')
    search_fields = ('ruc',)

@admin.register(SesionProceso)
class SesionProcesoAdmin(admin.ModelAdmin):
    list_display = ('empresa', 'usuario', 'tipo', 'anio', 'mes', 'estado', 'created_at')
    list_filter = ('tipo', 'estado', 'anio', 'mes')

@admin.register(AsignacionCuenta)
class AsignacionCuentaAdmin(admin.ModelAdmin):
    list_display = ('sesion', 'factura_id', 'cuenta')
    search_fields = ('factura_id', 'cuenta__codigo')
