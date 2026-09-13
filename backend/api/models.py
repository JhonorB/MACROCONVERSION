from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class PerfilUsuario(models.Model):
    ROL_CHOICES = [
        ('ADMIN', 'ADMIN'),
        ('CONTADOR', 'CONTADOR'),
    ]
    ESTADO_CHOICES = [
        ('ACTIVO', 'ACTIVO'),
        ('INACTIVO', 'INACTIVO'),
    ]
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='CONTADOR')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ACTIVO')
    telefono = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.rol}"

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(usuario=instance)

@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    instance.perfil.save()

class Empresa(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='empresas', null=True, blank=True)
    codigo = models.CharField(max_length=4, unique=True)  # Auto-generated 4-digit code
    ruc = models.CharField(max_length=11)
    razon_social = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.codigo} - {self.ruc} - {self.razon_social}"

class CuentaCompra(models.Model):
    codigo = models.CharField(max_length=20, unique=True)  # e.g. '6011001'
    descripcion = models.CharField(max_length=255)  # e.g. 'MERCADERIAS'
    
    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"
    
class FrecuenciaCuenta(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='frecuencias', null=True, blank=True)
    ruc_proveedor = models.CharField(max_length=11, db_index=True)
    cuenta = models.ForeignKey(CuentaCompra, on_delete=models.CASCADE)
    frecuencia = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ['ruc_proveedor', 'cuenta', 'usuario']

class CacheDeuda(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ruc = models.CharField(max_length=11)
    tiene_deuda = models.BooleanField(default=False)
    consultado_en = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['ruc', 'usuario']

class SesionProceso(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sesiones', null=True, blank=True)
    TIPO_CHOICES = [('COM', 'Compras'), ('VTA', 'Ventas')]
    ESTADO_CHOICES = [
        ('UPLOADED', 'CSV Subido'),
        ('PRESCANNED', 'Pre-escaneado'),
        ('DETRACCIONES', 'Detracciones Pendientes'),
        ('ASIGNACION', 'Asignación de Cuentas'),
        ('COMPLETED', 'Completado'),
    ]
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=3, choices=TIPO_CHOICES)
    subtipo_vta = models.CharField(max_length=30, blank=True, default='')
    anio = models.CharField(max_length=2)
    mes = models.CharField(max_length=2)
    csv_file = models.FileField(upload_to='uploads/')
    excel_file = models.FileField(upload_to='exports/', blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='UPLOADED')
    datos_prescan = models.JSONField(blank=True, null=True)  # Store pre-scanned data
    datos_detracciones = models.JSONField(blank=True, null=True)
    datos_eliminados = models.JSONField(blank=True, null=True)  # Track eliminated entries
    resumen = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class AsignacionCuenta(models.Model):
    sesion = models.ForeignKey(SesionProceso, on_delete=models.CASCADE, related_name='asignaciones')
    factura_id = models.CharField(max_length=100)  # Format: RUC_SERIE_NUMERO
    cuenta = models.ForeignKey(CuentaCompra, on_delete=models.CASCADE)
    class Meta:
        unique_together = ['sesion', 'factura_id']

class LiquidacionImpuesto(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    anio = models.CharField(max_length=2)
    mes = models.CharField(max_length=2)
    compras_no_gravadas = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    credito_fiscal_anterior = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    percepciones = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tasa_renta = models.DecimalField(max_digits=7, decimal_places=4, default=0.0100)
    saldo_favor_renta_anterior = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        unique_together = ['empresa', 'anio', 'mes']
