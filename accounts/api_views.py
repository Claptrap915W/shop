import json
from loguru import logger
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from carts.services import merge_session_cart_into_db

def csrf_view(request):
    get_token(request)
    return JsonResponse({'detail': 'CSRF cookie set'})

def api_login(request):
    if request.method != 'POST':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'detail': 'Invalid JSON'}, status=400)
    
    username = data.get('username') or ''
    password = data.get('password') or ''
    if not username or not password:
        return JsonResponse(
            {'detail': 'username and password required'},
            status=400,
        )
    
    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({'detail': 'Invalid credentials'}, status=401)
    
    try:
        merge_session_cart_into_db(request, user)
    except Exception:
        logger.exception(f'Failed to merge session cart for user {user.username}')

    login(request, user)
    return JsonResponse({
        'id': user.id,
        'username': user.username,
    })

def api_logout(request):
    if request.method != 'POST':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)

    logout(request)
    return JsonResponse({'detail': 'Logged out'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
    })