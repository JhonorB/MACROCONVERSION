from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EmpresaViewSet, CuentaCompraViewSet, ProcesoViewSet, 
    ComprobanteViewSet, AuthLoginView, AuthLogoutView, 
    AuthCheckView, DashboardStatsView, ContadorViewSet, LiquidacionView, CalculadoraImpuestosView
)

router = DefaultRouter()
router.register(r'empresas', EmpresaViewSet, basename='empresa')
router.register(r'cuentas', CuentaCompraViewSet, basename='cuenta')
router.register(r'procesos', ProcesoViewSet, basename='proceso')
router.register(r'comprobantes', ComprobanteViewSet, basename='comprobante')
router.register(r'contadores', ContadorViewSet, basename='contador')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', AuthLoginView.as_view(), name='auth-login'),
    path('auth/logout/', AuthLogoutView.as_view(), name='auth-logout'),
    path('auth/check/', AuthCheckView.as_view(), name='auth-check'),
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('liquidacion/', LiquidacionView.as_view(), name='liquidacion'),
    path('impuestos/calcular/', CalculadoraImpuestosView.as_view(), name='impuestos-calcular'),
]
