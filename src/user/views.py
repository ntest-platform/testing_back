import jwt

from rest_framework import parsers, renderers, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import UserSerializer, AuthTokenSerializer, ChangePasswordSerializer
from .authentication import JSONWebTokenAuthentication, AccessTokenGenerator, RefreshTokenGenerator
from .services import PasswordChangeService


class JSONWebTokenAuth(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            access_token = AccessTokenGenerator(user.email).generate_token()
            refresh_token = RefreshTokenGenerator(user.email).generate_token()
            return Response({
                'access_token': access_token, 'refresh_token': refresh_token,
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RefreshTokenView(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)

    def post(self, request):
        refresh_token = request.data.get('refresh_token')

        if not refresh_token:
            return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user, payload = JSONWebTokenAuthentication().authenticate_credentials(refresh_token)

            if not user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            new_access_token = RefreshTokenGenerator(user.email).generate_token()
            return Response({'access_token': new_access_token})

        except jwt.ExpiredSignatureError:
            return Response({'error': 'Refresh token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.DecodeError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)


class CreateUserAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        user = request.data
        serializer = UserSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ChangePasswordAPIView(APIView):
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        result_message, result_status_code = PasswordChangeService(user).execute(serializer.data)
        return Response(result_message, status=result_status_code)
