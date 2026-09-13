from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Empresa, CuentaCompra, FrecuenciaCuenta, SesionProceso, AsignacionCuenta, PerfilUsuario, LiquidacionImpuesto

class PerfilUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilUsuario
        fields = ['rol', 'estado', 'telefono', 'created_at', 'updated_at']

class ContadorSerializer(serializers.ModelSerializer):
    perfil = PerfilUsuarioSerializer(read_only=True)
    empresa_count = serializers.IntegerField(read_only=True, required=False)
    proceso_count = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'perfil', 'empresa_count', 'proceso_count']

class ContadorCreateSerializer(serializers.ModelSerializer):
    telefono = serializers.CharField(write_only=True, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name', 'telefono']

    def create(self, validated_data):
        telefono = validated_data.pop('telefono', '')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        # Perfil is created by signal, we just update it
        user.perfil.rol = 'CONTADOR'
        user.perfil.telefono = telefono
        user.perfil.save()
        return user

class EmpresaSerializer(serializers.ModelSerializer):
    usuario_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='usuario', required=False, allow_null=True
    )

    class Meta:
        model = Empresa
        fields = '__all__'
        read_only_fields = ['created_at']
        extra_kwargs = {
            'codigo': {'required': False, 'allow_blank': True},
            'usuario': {'read_only': True}
        }

class CuentaCompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuentaCompra
        fields = '__all__'

class FrecuenciaCuentaSerializer(serializers.ModelSerializer):
    cuenta = CuentaCompraSerializer(read_only=True)
    class Meta:
        model = FrecuenciaCuenta
        fields = '__all__'

class SesionProcesoSerializer(serializers.ModelSerializer):
    empresa_detalle = EmpresaSerializer(source='empresa', read_only=True)
    class Meta:
        model = SesionProceso
        fields = '__all__'
        read_only_fields = ['estado', 'datos_prescan', 'datos_detracciones', 'datos_eliminados', 'resumen', 'excel_file', 'created_at', 'usuario']

class AsignacionCuentaSerializer(serializers.ModelSerializer):
    cuenta_detalle = CuentaCompraSerializer(source='cuenta', read_only=True)
    class Meta:
        model = AsignacionCuenta
        fields = '__all__'

class CsvUploadSerializer(serializers.Serializer):
    csv_file = serializers.FileField(required=True)
    empresa_id = serializers.IntegerField(required=True)
    tipo = serializers.ChoiceField(choices=[('COM', 'Compras'), ('VTA', 'Ventas')])
    subtipo_vta = serializers.CharField(required=False, allow_blank=True, max_length=30)
    anio = serializers.CharField(max_length=2, required=True)
    mes = serializers.CharField(max_length=2, required=True)

class AsignarCuentaSerializer(serializers.Serializer):
    factura_id = serializers.CharField(max_length=100)
    cuenta_codigo = serializers.CharField(max_length=20)
    aplicar_a_ruc = serializers.BooleanField(default=False)

class LiquidacionImpuestoSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiquidacionImpuesto
        fields = '__all__'
