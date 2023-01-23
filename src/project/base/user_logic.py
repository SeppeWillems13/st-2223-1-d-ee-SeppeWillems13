from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .models import User


def get_user(request, member_id):
    user = get_object_or_404(User, pk=member_id)
    user_data = {
        'name': user.username,
        'email': user.email,
    }
    return JsonResponse(user_data)

