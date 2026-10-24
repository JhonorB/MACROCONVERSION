from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Empresa, CuentaCompra, FrecuenciaCuenta, SesionProceso, AsignacionCuenta, PerfilUsuario, LiquidacionImpuesto

class PerfilUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilUsuario
        fields = ['rol', 'estado', 'telefono', 'created_at', 'updated_at']

class ContadorSerializer(serializers.ModelSerializer):
    perfil = PerfilUsuarioSerializer(read_only=True)
    estado = serializers.SerializerMethodField()
    telefono = serializers.SerializerMethodField()
    rol = serializers.SerializerMethodField()
    empresa_count = serializers.IntegerField(read_only=True, required=False)
    empresas_count = serializers.IntegerField(source='empresa_count', read_only=True, required=False)
    proceso_count = serializers.IntegerField(read_only=True, required=False)
    procesos_count = serializers.IntegerField(source='proceso_count', read_only=True, required=False)

    def get_estado(self, obj):
        if hasattr(obj, 'perfil') and obj.perfil.estado:
            return obj.perfil.estado
        return 'ACTIVO' if obj.is_active else 'INACTIVO'

    def get_telefono(self, obj):
        return obj.perfil.telefono if hasattr(obj, 'perfil') else ''

    def get_rol(self, obj):
        return obj.perfil.rol if hasattr(obj, 'perfil') else 'CONTADOR'

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'is_active',
            'estado', 'telefono', 'rol', 'perfil',
            'empresa_count', 'empresas_count', 'proceso_count', 'procesos_count'
        ]

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

    def validate_mes(self, value):
        val = str(value).strip().zfill(2)
        if not val.isdigit() or not (1 <= int(val) <= 12):
            raise serializers.ValidationError("El mes debe ser un valor numérico válido entre 01 y 12.")
        return val

    def validate_anio(self, value):
        val = str(value).strip()
        if not val.isdigit() or len(val) != 2:
            raise serializers.ValidationError("El año debe tener exactamente 2 dígitos numéricos (ej. 24, 25, 26).")
        return val

    def validate_csv_file(self, value):
        name = value.name.lower()
        if not (name.endswith('.csv') or name.endswith('.txt')):
            raise serializers.ValidationError("El archivo debe ser un archivo plano con extensión .csv o .txt.")
        
        max_size = 25 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(f"El archivo excede el tamaño máximo permitido de 25 MB ({round(value.size / (1024*1024), 2)} MB).")
            
        if value.size == 0:
            raise serializers.ValidationError("El archivo subido está completamente vacío (0 bytes).")
            
        return value

class AsignarCuentaSerializer(serializers.Serializer):
    factura_id = serializers.CharField(max_length=100, required=True)
    cuenta_codigo = serializers.CharField(max_length=20, required=True)
    aplicar_a_ruc = serializers.BooleanField(default=False, required=False)

    def validate_cuenta_codigo(self, value):
        val = str(value).strip()
        if not CuentaCompra.objects.filter(codigo=val).exists():
            raise serializers.ValidationError(f"La cuenta contable '{val}' no existe en el catálogo del sistema.")
        return val

class LiquidacionImpuestoSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiquidacionImpuesto
        fields = '__all__'
