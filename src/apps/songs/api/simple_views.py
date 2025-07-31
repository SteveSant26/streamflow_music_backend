from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView


# Vista simple de prueba
class TestView(APIView):
    def get(self, request):
        return Response({"message": "Songs API is working!"}, status=status.HTTP_200_OK)


@api_view(["GET"])
def test_function_view(request):
    return Response({"message": "Function view working!"}, status=status.HTTP_200_OK)
