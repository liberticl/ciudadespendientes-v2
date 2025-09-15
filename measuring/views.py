from rest_framework.views import APIView
from rest_framework.response import Response
from .auth import JWTAuthentication
from rest_framework import status
from .serializers import TrafficCountSerializer


class TrafficCountAPIView(APIView):
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        serializer = TrafficCountSerializer(
            data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(
                {'status': serializer.is_valid(), 'data': serializer.data},
                status=status.HTTP_201_CREATED)

        return Response(
            {'status': serializer.is_valid(), 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST)
