from functools import wraps
from django.shortcuts import redirect
from django.http import JsonResponse
from django.urls import reverse

def restaurant_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('restaurant_id'):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Please login to continue',
                    'redirect_url': reverse('joo:restaurant_login')
                }, status=401)
            return redirect('joo:restaurant_login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view 