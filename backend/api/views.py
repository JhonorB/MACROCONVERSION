import os
import fitz
import logging
import traceback

logger = logging.getLogger(__name__)
from rest_framework import viewsets, views, status, parsers
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from django.conf import settings
from django.http import FileResponse

from .models import Empresa, CuentaCompra, SesionProceso, AsignacionCuenta, FrecuenciaCuenta, PerfilUsuario, LiquidacionImpuesto
from .serializers import (
    EmpresaSerializer, CuentaCompraSerializer, SesionProcesoSerializer,
    CsvUploadSerializer, AsignarCuentaSerializer, ContadorSerializer, ContadorCreateSerializer,
    LiquidacionImpuestoSerializer
)
from .services.procesador_sire import preparar_dataframes
from .services.generador_excel import guardar_excel_final, calcular_resumen
from .permissions import IsAuthenticated, IsAdmin, IsContador, IsAdminOrOwner

from django.contrib.auth.models import User

class EmpresaViewSet(viewsets.ModelViewSet):
    serializer_class = EmpresaSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = Empresa.objects.all().order_by('codigo')
        
        # Isolation
        if hasattr(self.request.user, 'perfil') and self.request.user.perfil.rol == 'CONTADOR':
            queryset = queryset.filter(Q(usuario=self.request.user) | Q(usuario__isnull=True))
            
        q = self.request.query_params.get('q', None)
        if q:
            queryset = queryset.filter(
                Q(razon_social__icontains=q) | Q(ruc__icontains=q) | Q(codigo__icontains=q)
            )
        return queryset

    def perform_create(self, serializer):
        codigo = serializer.validated_data.get('codigo', '')
        if not codigo:
            empresas = Empresa.objects.all()
            max_codigo = empresas.order_by('-codigo').first()
            if max_codigo and max_codigo.codigo.isdigit():
                next_codigo = str(int(max_codigo.codigo) + 1).zfill(4)
            else:
                next_codigo = "0001"
            serializer.save(codigo=next_codigo)
        else:
            serializer.save()


class CuentaCompraViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CuentaCompra.objects.all().order_by('codigo')
    serializer_class = CuentaCompraSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.query_params.get('q', None)
        if q:
            queryset = queryset.filter(
                Q(descripcion__icontains=q) | Q(codigo__icontains=q)
            )
        return queryset

    @action(detail=False, methods=['get'], url_path='sugeridas/(?P<ruc>[^/.]+)')
    def sugeridas(self, request, ruc=None):
        frecuencias = FrecuenciaCuenta.objects.filter(
            ruc_proveedor=ruc, 
            usuario=request.user
        ).order_by('-frecuencia')[:5]
        
        sugeridas_ids = frecuencias.values_list('cuenta_id', flat=True)
        sugeridas = CuentaCompra.objects.filter(id__in=sugeridas_ids)
        resto = CuentaCompra.objects.exclude(id__in=sugeridas_ids)
        todas = list(sugeridas) + list(resto)
        
        serializer = self.get_serializer(todas, many=True)
        return Response(serializer.data)


class ProcesoViewSet(viewsets.ViewSet):
    parser_classes = (parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser)
    permission_classes = [IsAuthenticated]

    def get_sesion(self, pk, user):
        qs = SesionProceso.objects.filter(pk=pk)
        if hasattr(user, 'perfil') and user.perfil.rol == 'CONTADOR':
            qs = qs.filter(usuario=user)
        return qs.first()

    def retrieve(self, request, pk=None):
        sesion = self.get_sesion(pk, request.user)
        if not sesion:
            return Response({'error': 'Sesion no encontrada o acceso no autorizado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(SesionProcesoSerializer(sesion).data)

    @action(detail=False, methods=['post'])
    def upload_csv(self, request):
        serializer = CsvUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        data = serializer.validated_data
        
        try:
            empresa = Empresa.objects.get(id=data['empresa_id'])
        except Empresa.DoesNotExist:
            return Response({"error": "Empresa no encontrada"}, status=status.HTTP_404_NOT_FOUND)
            
        if hasattr(request.user, 'perfil') and request.user.perfil.rol == 'CONTADOR':
            if empresa.usuario != request.user:
                return Response({"error": "No tiene permiso para usar esta empresa"}, status=status.HTTP_403_FORBIDDEN)
        
        sesion = SesionProceso.objects.create(
            usuario=request.user,
            empresa=empresa,
            tipo=data['tipo'],
            subtipo_vta=data.get('subtipo_vta', ''),
            anio=data['anio'],
            mes=data['mes'],
            csv_file=data['csv_file']
        )
        
        try:
            ruta_csv = sesion.csv_file.path
            res = preparar_dataframes(
                ruta_csv=ruta_csv,
                tipo=sesion.tipo,
                codigo_empresa=empresa.codigo,
                anio=sesion.anio,
                mes=sesion.mes,
                subtipo_vta=sesion.subtipo_vta
            )
            df_forexel, df_docref, lista_detracciones, cantidad_nc, elim_anio, facturas, elim_deuda = res
            
            sesion.datos_eliminados = {
                'eliminados_anio_pasado': elim_anio,
                'eliminados_deuda': elim_deuda,
                'cantidad_nc': cantidad_nc
            }
            sesion.datos_detracciones = lista_detracciones
            
            if sesion.tipo == 'VTA':
                nombre_archivo = f"{sesion.tipo}{empresa.codigo}{sesion.anio}{sesion.mes}.xlsx"
                excel_path = guardar_excel_final(df_forexel, df_docref, [], sesion.tipo, nombre_archivo)
                sesion.excel_file.name = excel_path
                sesion.estado = 'COMPLETED'
                resumen_calc = calcular_resumen(df_forexel, sesion.tipo)
                resumen_calc['empresa'] = f"{empresa.codigo} - {empresa.razon_social}"
                resumen_calc['periodo'] = f"{sesion.mes}/{sesion.anio}"
                sesion.resumen = resumen_calc
                sesion.save()
                return Response(SesionProcesoSerializer(sesion).data)
            else: # COM
                if lista_detracciones:
                    sesion.estado = 'DETRACCIONES'
                else:
                    sesion.estado = 'ASIGNACION'
                sesion.datos_prescan = {'facturas': facturas}
                sesion.save()
                return Response(SesionProcesoSerializer(sesion).data)
                
        except ValueError as ve:
            logger.warning(f"Error de validacion CSV en sesion {sesion.id}: {str(ve)}")
            sesion.delete()
            return Response({"error": str(ve), "code": "CSV_VALIDATION_ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error inesperado procesando CSV en sesion {sesion.id}: {traceback.format_exc()}")
            sesion.delete()
            return Response({"error": "No se pudo procesar el archivo CSV. Verifique que sea un archivo oficial de SIRE SUNAT.", "code": "CSV_PROCESSING_ERROR"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'])
    def detracciones(self, request, pk=None):
        sesion = self.get_sesion(pk, request.user)
        if not sesion: return Response({"error": "Sesión no encontrada o no autorizada"}, status=status.HTTP_404_NOT_FOUND)
            
        if request.method == 'GET':
            return Response(sesion.datos_detracciones)
        else:
            excluidos = request.data.get('excluidos', [])
            facturas = sesion.datos_prescan.get('facturas', [])
            facturas_restantes = [f for f in facturas if f['idx_df'] not in excluidos]
            
            elim_dict = sesion.datos_eliminados or {}
            elim_dict['detracciones_excluidas'] = excluidos
            sesion.datos_eliminados = elim_dict
            
            sesion.datos_prescan['facturas'] = facturas_restantes
            sesion.estado = 'ASIGNACION'
            sesion.save()
            return Response(SesionProcesoSerializer(sesion).data)

    @action(detail=True, methods=['get'])
    def facturas(self, request, pk=None):
        sesion = self.get_sesion(pk, request.user)
        if not sesion: return Response({"error": "Sesión no encontrada o no autorizada"}, status=status.HTTP_404_NOT_FOUND)
        return Response(sesion.datos_prescan.get('facturas', []))

    @action(detail=True, methods=['post'])
    def asignar_cuenta(self, request, pk=None):
        sesion = self.get_sesion(pk, request.user)
        if not sesion: return Response({"error": "Sesión no encontrada o no autorizada"}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = AsignarCuentaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        data = serializer.validated_data
        cuenta = CuentaCompra.objects.get(codigo=data['cuenta_codigo'])
        
        AsignacionCuenta.objects.update_or_create(
            sesion=sesion,
            factura_id=data['factura_id'],
            defaults={'cuenta': cuenta}
        )
        
        parts = data['factura_id'].split('-')
        if len(parts) == 3:
            ruc = parts[2]
            if data.get('aplicar_a_ruc', False):
                for f in sesion.datos_prescan.get('facturas', []):
                    if f['CODENT'] == ruc:
                        AsignacionCuenta.objects.update_or_create(
                            sesion=sesion,
                            factura_id=f['ID'],
                            defaults={'cuenta': cuenta}
                        )
            
            freq, _ = FrecuenciaCuenta.objects.get_or_create(ruc_proveedor=ruc, cuenta=cuenta, usuario=request.user)
            freq.frecuencia += 1
            freq.save()
            
        return Response({"status": "ok"})

    @action(detail=True, methods=['post'])
    def asignar_cuenta_masivo(self, request, pk=None):
        return self.asignar_cuenta(request, pk)

    @action(detail=True, methods=['post'])
    def generar(self, request, pk=None):
        sesion = self.get_sesion(pk, request.user)
        if not sesion: return Response({"error": "Sesión no encontrada o no autorizada"}, status=status.HTTP_404_NOT_FOUND)
            
        asignaciones = AsignacionCuenta.objects.filter(sesion=sesion)
        cuentas_dict = {a.factura_id: a.cuenta.codigo for a in asignaciones}
        
        try:
            ruta_csv = sesion.csv_file.path
            res = preparar_dataframes(
                ruta_csv=ruta_csv,
                tipo=sesion.tipo,
                codigo_empresa=sesion.empresa.codigo,
                anio=sesion.anio,
                mes=sesion.mes,
                subtipo_vta=sesion.subtipo_vta,
                cuentas_asignadas=cuentas_dict
            )
            df_forexel, df_docref, lista_detracciones, cantidad_nc, elim_anio, facturas, elim_deuda = res
            
            excluidos = sesion.datos_eliminados.get('detracciones_excluidas', []) if sesion.datos_eliminados else []
            
            nombre_archivo = f"{sesion.tipo}{sesion.empresa.codigo}{sesion.anio}{sesion.mes}.xlsx"
            excel_path = guardar_excel_final(df_forexel, df_docref, excluidos, sesion.tipo, nombre_archivo)
            
            sesion.excel_file.name = excel_path
            sesion.estado = 'COMPLETED'
            
            df_final = df_forexel.drop(index=excluidos, errors='ignore') if excluidos else df_forexel
            resumen_calc = calcular_resumen(df_final, sesion.tipo)
            resumen_calc['empresa'] = f"{sesion.empresa.codigo} - {sesion.empresa.razon_social}"
            resumen_calc['periodo'] = f"{sesion.mes}/{sesion.anio}"
            sesion.resumen = resumen_calc
            sesion.save()
            
            return Response(SesionProcesoSerializer(sesion).data)
        except Exception as e:
            logger.error(f"Error generando Excel para sesion {sesion.id}: {traceback.format_exc()}")
            return Response({"error": "Error interno al generar el archivo Excel.", "code": "EXCEL_GENERATION_ERROR"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def descargar(self, request, pk=None):
        sesion = self.get_sesion(pk, request.user)
        if not sesion: return Response({"error": "Sesion no encontrada"}, status=status.HTTP_404_NOT_FOUND)
            
        if not sesion.excel_file or not os.path.exists(sesion.excel_file.path):
            return Response({"error": "El archivo generado no se encuentra en el servidor."}, status=status.HTTP_404_NOT_FOUND)
        return FileResponse(open(sesion.excel_file.path, 'rb'), as_attachment=True, filename=os.path.basename(sesion.excel_file.name))

    @action(detail=True, methods=['get'])
    def resumen(self, request, pk=None):
        sesion = self.get_sesion(pk, request.user)
        if not sesion: return Response({"error": "Sesión no encontrada o no autorizada"}, status=status.HTTP_404_NOT_FOUND)
        return Response(sesion.resumen)


class ComprobanteViewSet(viewsets.ViewSet):
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        files = request.FILES.getlist('files')
        pdfs_dir = os.path.join(settings.MEDIA_ROOT, 'pdfs')
        os.makedirs(pdfs_dir, exist_ok=True)
        uploaded = []
        for f in files:
            path = os.path.join(pdfs_dir, f.name)
            with open(path, 'wb+') as dest:
                for chunk in f.chunks():
                    dest.write(chunk)
            uploaded.append(f.name)
        return Response({"uploaded": uploaded})
        
    @action(detail=False, methods=['post'])
    def buscar(self, request):
        serie = request.data.get('serie')
        numero = request.data.get('numero')
        ruc = request.data.get('ruc')
        
        pdfs_dir = os.path.join(settings.MEDIA_ROOT, 'pdfs')
        if not os.path.exists(pdfs_dir):
            return Response({"error": "No PDFs found"}, status=404)
            
        for file in os.listdir(pdfs_dir):
            if file.endswith(".pdf"):
                if serie in file and numero in file:
                    return Response({"filename": file})
                    
                path = os.path.join(pdfs_dir, file)
                try:
                    doc = fitz.open(path)
                    text = ""
                    for page in doc:
                        text += page.get_text()
                    doc.close()
                    
                    if serie in text and numero in text and (not ruc or ruc in text):
                        return Response({"filename": file})
                except:
                    pass
                    
        return Response({"error": "Not found"}, status=404)

    @action(detail=False, methods=['get'])
    def ver(self, request):
        filename = request.query_params.get('filename')
        pdfs_dir = os.path.join(settings.MEDIA_ROOT, 'pdfs')
        path = os.path.join(pdfs_dir, filename)
        if os.path.exists(path):
            return FileResponse(open(path, 'rb'), content_type='application/pdf')
        return Response({"error": "Not found"}, status=404)


from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta

@method_decorator(csrf_exempt, name='dispatch')
class AuthLoginView(views.APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if hasattr(user, 'perfil') and user.perfil.estado == 'INACTIVO':
                return Response({'error': 'Usuario inactivo'}, status=status.HTTP_403_FORBIDDEN)
                
            login(request, user)
            rol = user.perfil.rol if hasattr(user, 'perfil') else None
            estado = user.perfil.estado if hasattr(user, 'perfil') else None
            return Response({
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'rol': rol,
                    'estado': estado
                }
            })
        return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)


class AuthLogoutView(views.APIView):
    def post(self, request):
        logout(request)
        return Response({'status': 'ok'})


class AuthCheckView(views.APIView):
    def get(self, request):
        if request.user.is_authenticated:
            rol = request.user.perfil.rol if hasattr(request.user, 'perfil') else None
            estado = request.user.perfil.estado if hasattr(request.user, 'perfil') else None
            
            return Response({
                'authenticated': True,
                'user': {
                    'id': request.user.id,
                    'username': request.user.username,
                    'email': request.user.email,
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    'rol': rol,
                    'estado': estado
                }
            })
        return Response({'authenticated': False}, status=status.HTTP_401_UNAUTHORIZED)


class DashboardStatsView(views.APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        is_admin = hasattr(request.user, 'perfil') and request.user.perfil.rol == 'ADMIN'
        
        # Base querysets based on role
        if is_admin:
            empresa_qs = Empresa.objects.all()
            proceso_qs = SesionProceso.objects.all()
        else:
            empresa_qs = Empresa.objects.filter(usuario=request.user)
            proceso_qs = SesionProceso.objects.filter(usuario=request.user)
            
        total_empresas = empresa_qs.count()
        total_cuentas = CuentaCompra.objects.count()
        total_procesos = proceso_qs.count()
        procesos_completados = proceso_qs.filter(estado='COMPLETED').count()
        procesos_pendientes = proceso_qs.exclude(estado='COMPLETED').count()
        
        hace_7_dias = timezone.now() - timedelta(days=7)
        procesos_recientes = proceso_qs.filter(
            created_at__gte=hace_7_dias
        ).order_by('-created_at')[:10]
        
        recientes_data = []
        for p in procesos_recientes:
            recientes_data.append({
                'id': p.id,
                'empresa': p.empresa.razon_social,
                'empresa_codigo': p.empresa.codigo,
                'tipo': p.tipo,
                'subtipo_vta': p.subtipo_vta,
                'periodo': f'{p.mes}/{p.anio}',
                'estado': p.estado,
                'created_at': p.created_at.isoformat(),
            })
        
        compras_count = proceso_qs.filter(tipo='COM').count()
        ventas_count = proceso_qs.filter(tipo='VTA').count()
        
        top_empresas = empresa_qs.annotate(
            num_procesos=Count('sesionproceso')
        ).order_by('-num_procesos')[:5]
        
        top_empresas_data = [{
            'codigo': e.codigo,
            'razon_social': e.razon_social,
            'ruc': e.ruc,
            'num_procesos': e.num_procesos,
        } for e in top_empresas]
        
        res = {
            'total_empresas': total_empresas,
            'total_cuentas': total_cuentas,
            'total_procesos': total_procesos,
            'procesos_completados': procesos_completados,
            'procesos_pendientes': procesos_pendientes,
            'compras_count': compras_count,
            'ventas_count': ventas_count,
            'procesos_recientes': recientes_data,
            'top_empresas': top_empresas_data,
        }
        
        if is_admin:
            contadores = User.objects.filter(perfil__rol='CONTADOR')
            res['total_contadores'] = contadores.count()
            
        return Response(res)


class LiquidacionView(views.APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        mes = request.query_params.get('mes')
        anio = request.query_params.get('anio')
        
        if not mes or not anio:
            now = timezone.now()
            mes_val = mes if mes else f"{now.month:02d}"
            anio_val = anio if anio else str(now.year)[2:]
        else:
            mes_val = mes
            anio_val = anio

        users = User.objects.filter(perfil__rol='CONTADOR').annotate(
            compras_count=Count('sesiones', filter=Q(sesiones__tipo='COM', sesiones__mes=mes_val, sesiones__anio=anio_val)),
            ventas_count=Count('sesiones', filter=Q(sesiones__tipo='VTA', sesiones__mes=mes_val, sesiones__anio=anio_val)),
            empresas_distintas=Count('sesiones__empresa', filter=Q(sesiones__mes=mes_val, sesiones__anio=anio_val), distinct=True)
        )

        data = [
            {
                "id": u.id,
                "username": u.username,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "compras_count": u.compras_count,
                "ventas_count": u.ventas_count,
                "empresas_distintas": u.empresas_distintas
            }
            for u in users
        ]
        
        return Response(data)

class ContadorViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    
    def get_queryset(self):
        return User.objects.filter(perfil__rol='CONTADOR').annotate(
            empresa_count=Count('empresas', distinct=True),
            proceso_count=Count('sesiones', distinct=True)
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return ContadorCreateSerializer
        return ContadorSerializer

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        user = self.get_object()
        
        # Actualizamos datos del user (name, email)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Actualizamos perfil si se enviaron (telefono, estado)
        if 'telefono' in request.data:
            user.perfil.telefono = request.data['telefono']
        if 'estado' in request.data:
            user.perfil.estado = request.data['estado']
            user.is_active = (request.data['estado'] == 'ACTIVO')
            user.save()
            
        user.perfil.save()
        return Response(ContadorSerializer(user).data)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.perfil.estado = 'INACTIVO'
        user.perfil.save()
        user.is_active = False
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_path='toggle-estado')
    def toggle_estado(self, request, pk=None):
        user = self.get_object()
        is_active = user.perfil.estado == 'ACTIVO'
        
        user.perfil.estado = 'INACTIVO' if is_active else 'ACTIVO'
        user.perfil.save()
        user.is_active = not is_active
        user.save()
        
        return Response({
            "status": "ok", 
            "message": f"Contador {'desactivado' if is_active else 'activado'}",
            "nuevo_estado": user.perfil.estado
        })

    @action(detail=True, methods=['get'])
    def detalle(self, request, pk=None):
        user = self.get_object()
        empresas = Empresa.objects.filter(usuario=user)
        procesos = SesionProceso.objects.filter(usuario=user)
        
        return Response({
            "contador": ContadorSerializer(user).data,
            "empresas": EmpresaSerializer(empresas, many=True).data,
            "procesos": SesionProcesoSerializer(procesos, many=True).data
        })

class CalculadoraImpuestosView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        empresa_id = request.query_params.get('empresa')
        anio = request.query_params.get('anio')
        mes = request.query_params.get('mes')

        try:
            empresa = Empresa.objects.get(id=empresa_id)
        except Empresa.DoesNotExist:
            return Response({"error": "Empresa no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        if hasattr(request.user, 'perfil') and request.user.perfil.rol == 'CONTADOR':
            if empresa.usuario != request.user:
                return Response({"error": "No tiene permiso para usar esta empresa"}, status=status.HTTP_403_FORBIDDEN)

        anio_2d = str(anio)[-2:] if anio else ''
        mes_2d = str(mes).zfill(2) if mes else ''

        sesiones = SesionProceso.objects.filter(
            Q(empresa=empresa, anio=anio_2d, mes=mes_2d, estado='COMPLETED') |
            Q(empresa=empresa, anio=str(anio), mes=str(mes), estado='COMPLETED')
        )
        ventas_monto = 0
        ventas_igv = 0
        compras_monto = 0
        compras_igv = 0

        for sesion in sesiones:
            if sesion.tipo == 'VTA':
                ventas_monto += sesion.resumen.get('bi_total', 0) if sesion.resumen else 0
                ventas_igv += sesion.resumen.get('igv_total', 0) if sesion.resumen else 0
            elif sesion.tipo == 'COM':
                compras_monto += sesion.resumen.get('bi_total', 0) if sesion.resumen else 0
                compras_igv += sesion.resumen.get('igv_total', 0) if sesion.resumen else 0

        liq = LiquidacionImpuesto.objects.filter(empresa=empresa, anio=anio_2d, mes=mes_2d).first()
        if not liq and anio and mes:
            liq = LiquidacionImpuesto.objects.filter(empresa=empresa, anio=str(anio), mes=str(mes)).first()
        liq_data = LiquidacionImpuestoSerializer(liq).data if liq else None

        return Response({
            "totales_sire": {
                "ventas_monto": ventas_monto,
                "ventas_igv": ventas_igv,
                "compras_monto": compras_monto,
                "compras_igv": compras_igv
            },
            "liquidacion": liq_data
        })

    def post(self, request):
        empresa_id = request.data.get('empresa')
        anio = request.data.get('anio')
        mes = request.data.get('mes')

        try:
            empresa = Empresa.objects.get(id=empresa_id)
        except Empresa.DoesNotExist:
            return Response({"error": "Empresa no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        if hasattr(request.user, 'perfil') and request.user.perfil.rol == 'CONTADOR':
            if empresa.usuario != request.user:
                return Response({"error": "No tiene permiso para usar esta empresa"}, status=status.HTTP_403_FORBIDDEN)

        anio_2d = str(anio)[-2:] if anio else ''
        mes_2d = str(mes).zfill(2) if mes else ''

        liq, created = LiquidacionImpuesto.objects.update_or_create(
            empresa=empresa,
            anio=anio_2d,
            mes=mes_2d,
            defaults={
                'compras_no_gravadas': request.data.get('compras_no_gravadas', 0),
                'credito_fiscal_anterior': request.data.get('credito_fiscal_anterior', 0),
                'percepciones': request.data.get('percepciones', 0),
                'tasa_renta': request.data.get('tasa_renta', 0.0100),
                'saldo_favor_renta_anterior': request.data.get('saldo_favor_renta_anterior', 0),
            }
        )

        return Response(LiquidacionImpuestoSerializer(liq).data)
