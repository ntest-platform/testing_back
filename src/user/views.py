import datetime
import jwt

from django.conf import settings
from rest_framework import parsers, renderers, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import UserSerializer, AuthTokenSerializer


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
            token = jwt.encode({
                'username': user.email,
                'iat': datetime.datetime.now(),
                'nbf': datetime.datetime.now() + datetime.timedelta(minutes=-5),
                'exp': datetime.datetime.now() + datetime.timedelta(days=7)
            }, settings.SECRET_KEY)
            return Response({'token': token})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateUserAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        user = request.data
        serializer = UserSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
