# backend/volunteers/views.py

from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from core.models import User  # adjust if your User model is elsewhere

@api_view(["POST"])
def volunteer_login(request):
    """
    Logs in a volunteer and returns JWT token.
    Expected JSON payload: {"email": "...", "password": "..."}
    """
    data = request.data
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return Response(
            {"success": False, "error": "Email and password are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(request, username=email, password=password)

    if user is None:
        return Response(
            {"success": False, "error": "Invalid email or password."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Create JWT tokens
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    # Optional: include user info
    user_data = {
        "id": user.id,
        "email": user.email,
        "first_name": getattr(user, "first_name", ""),
        "last_name": getattr(user, "last_name", ""),
        "volunteer_identifier": getattr(user, "volunteer_identifier", None),
    }

    return Response(
        {
            "success": True,
            "access": access_token,
            "refresh": refresh_token,
            "user": user_data,
        },
        status=status.HTTP_200_OK
    )
