from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TrafficCountSerializer
from .auth import TokenAuthentication


class TrafficCountAPIView(APIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        serializer = TrafficCountSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
