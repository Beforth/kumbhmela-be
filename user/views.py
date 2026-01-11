from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer
)

User = get_user_model()


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    """User registration endpoint"""
    try:
        # Log incoming data for debugging
        print(f"Register request method: {request.method}")
        print(f"Register request content type: {request.content_type}")
        print(f"Register request data: {request.data}")
        print(f"Register request body (raw): {request.body[:200] if hasattr(request, 'body') else 'N/A'}")
        
        # Check if request.data is empty
        if not request.data:
            error_msg = {'error': 'Request body is empty. Please send JSON data with email, full_name, and password.'}
            print(f"Register error: {error_msg}")
            return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'User registered successfully',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name
                },
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        
        # Log validation errors
        print(f"Register validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Register exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({'error': f'Server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login(request):
    """User login endpoint"""
    try:
        # Log incoming data for debugging
        print(f"Login request method: {request.method}")
        print(f"Login request content type: {request.content_type}")
        print(f"Login request data: {request.data}")
        print(f"Login request body (raw): {request.body[:200] if hasattr(request, 'body') else 'N/A'}")
        
        # Check if request.data is empty
        if not request.data:
            error_msg = {'error': 'Request body is empty. Please send JSON data with email and password.'}
            print(f"Login error: {error_msg}")
            return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name
                },
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)
        
        # Log validation errors
        print(f"Login validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Login exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({'error': f'Server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProfileView(generics.RetrieveUpdateAPIView):
    """User profile endpoint - Get and Update"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
