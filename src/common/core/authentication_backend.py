# # apps/auth/backends.py

# import jwt
# from django.conf import settings
# from django.contrib.auth.backends import BaseBackend

# from apps.user_profile.infrastructure.models import UserProfileModel
# from apps.user_profile.infrastructure.repository import UserRepository
# from apps.user_profile.use_cases import SyncUserFromSupabase


# class SupabaseBackend(BaseBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         token = kwargs.get("token")
#         if token is None and request is not None:
#             # Try to get token from headers (e.g., Authorization: Bearer <token>)
#             auth_header = request.META.get("HTTP_AUTHORIZATION", "")
#             if auth_header.startswith("Bearer "):
#                 token = auth_header.split("Bearer ")[1]
#         if token is None:
#             return None
#         try:
#             decoded = jwt.decode(
#                 token,
#                 settings.SUPABASE_JWT_SECRET,
#                 algorithms=settings.SUPABASE_JWT_ALGORITHM,
#                 options={"verify_aud": False},
#             )
#             sync_user = SyncUserFromSupabase(UserRepository())
#             user_entity = sync_user.execute(decoded)
#             user = UserProfileModel.objects.get(email=user_entity.email)
#             return user
#         except Exception:
#             return None

#     def get_user(self, user_id):
#         try:
#             return UserProfileModel.objects.get(pk=user_id)
#         except UserProfileModel.DoesNotExist:
#             return None
