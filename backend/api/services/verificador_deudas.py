import os
import json
import urllib.request
import urllib.error
from datetime import timedelta
from django.utils import timezone
from api.models import CacheDeuda

def verificar_deudas(lista_rucs):
    token_apiperu = os.environ.get('APIPERU_TOKEN')
    token_jsonpe = os.environ.get('JSONPE_TOKEN')
    
    rucs_con_deuda = []
    rucs_a_consultar = []
    
    for ruc in lista_rucs:
        try:
            cache = CacheDeuda.objects.get(ruc=str(ruc))
            if cache.tiene_deuda:
                rucs_con_deuda.append(ruc)
        except CacheDeuda.DoesNotExist:
            rucs_a_consultar.append(ruc)
            
    if (not token_apiperu and not token_jsonpe) or not rucs_a_consultar:
        return rucs_con_deuda
        
    url_apiperu = "https://apiperu.dev/api/ruc_deuda_coactiva"
    url_jsonpe = "https://api.json.pe/api/ruc/deuda-coactiva"
    
    for ruc in rucs_a_consultar:
        ruc_str = str(ruc).strip()
        if len(ruc_str) != 11:
            CacheDeuda.objects.update_or_create(ruc=ruc_str, defaults={'tiene_deuda': False})
            continue
            
        payload = json.dumps({"ruc": ruc_str}).encode('utf-8')
        tiene_deuda = False
        hubo_error_auth = False
        
        if token_apiperu:
            req = urllib.request.Request(url_apiperu, data=payload, method="POST")
            req.add_header("Accept", "application/json")
            req.add_header("Content-Type", "application/json")
            req.add_header("Authorization", f"Bearer {token_apiperu}")
            try:
                with urllib.request.urlopen(req, timeout=5) as response:
                    res_data = json.loads(response.read().decode('utf-8'))
                    if res_data.get("success", False):
                        if res_data.get("data"):
                            tiene_deuda = True
            except urllib.error.HTTPError as e:
                if e.code in (401, 403):
                    hubo_error_auth = True
            except Exception:
                pass
                
        if not tiene_deuda and token_jsonpe:
            req2 = urllib.request.Request(url_jsonpe, data=payload, method="POST")
            req2.add_header("Accept", "application/json")
            req2.add_header("Content-Type", "application/json")
            req2.add_header("Authorization", f"Bearer {token_jsonpe}")
            try:
                with urllib.request.urlopen(req2, timeout=5) as response:
                    hubo_error_auth = False
                    res_data = json.loads(response.read().decode('utf-8'))
                    if res_data.get("success", False) or "data" in res_data:
                        if res_data.get("data"):
                            tiene_deuda = True
            except urllib.error.HTTPError as e:
                if e.code in (401, 403):
                    hubo_error_auth = True
            except Exception:
                pass
                
        if hubo_error_auth and not tiene_deuda:
            return None
            
        CacheDeuda.objects.update_or_create(ruc=ruc_str, defaults={'tiene_deuda': tiene_deuda})
        if tiene_deuda:
            rucs_con_deuda.append(ruc)
            
    return rucs_con_deuda
