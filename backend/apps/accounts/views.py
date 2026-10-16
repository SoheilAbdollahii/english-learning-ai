from rest_framework import generics, permissions
from .models import Profile
from .serializers import MeSerializer

class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = MeSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "patch", "head", "options"]
    def get_object(self):
        Profile.objects.get_or_create(user=self.request.user)
        return self.request.user
