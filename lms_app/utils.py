import json
from functools import wraps
from django.core.cache import cache
from .mongodb import activity_logs
from datetime import datetime

def redis_cache_page(timeout=300):
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            user_id = request.user.id if hasattr(request, 'user') and request.user.is_authenticated else 'anon'
            cache_key = f"cache_{request.path}_{user_id}"
            
            cached_data = cache.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
            
            # Eksekusi fungsi utama
            response = func(self, request, *args, **kwargs)
            
            # SOLUSI: Bungkus response dalam format dictionary agar bisa di-JSON-kan
            # Kita ambil .items() atau __dict__ agar objek database-nya hilang
            try:
                # Ninja Extra response biasanya punya .dict()
                serializable_data = response.dict() if hasattr(response, 'dict') else response
                cache.set(cache_key, json.dumps(serializable_data, default=str), timeout)
            except:
                # Kalau gagal, ya sudah, jangan di-cache, tapi tetap kembalikan response
                pass
                
            return response
        return wrapper
    return decorator

def rate_limiter(requests_limit=60):
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):  # <--- FIX: Deklarasikan eksplisit
            ip_address = request.META.get('REMOTE_ADDR', 'unknown')
            cache_key = f"rate_limit_{ip_address}"
            
            requests = cache.get(cache_key, 0)
            if requests >= requests_limit:
                from ninja.errors import HttpError
                raise HttpError(429, "Too Many Requests")
            
            cache.set(cache_key, requests + 1, timeout=60)
            return func(self, request, *args, **kwargs) # <--- FIX: Passing eksplisit
        return wrapper
    return decorator

def log_activity(user_id, username, action, details):
    log_data = {
        "user_id": user_id,
        "username": username,
        "action": action,
        "details": details,
        "timestamp": datetime.utcnow()
    }
    try:
        activity_logs.insert_one(log_data)
    except Exception as e:
        print(f"Gagal mencatat log ke MongoDB: {e}")