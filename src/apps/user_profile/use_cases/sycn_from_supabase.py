from ..domain.entities import UserEntity
from ..infrastructure.repository import UserRepository


class SyncUserFromSupabase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, supabase_data: dict) -> UserEntity:
        metadata = supabase_data.get("user_metadata", {})
        supabase_user_id = supabase_data.get("sub", "")  # <-- aquí el valor correcto
        supabase_email = supabase_data.get("email", "")

        print()
        print()
        print()
        print()
        print()

        print(f"Syncing user from Supabase with supabase_user_id: {supabase_user_id}")
        print(f"Syncing user from Supabase with data: {metadata}")
        print(f"Syncing user from Supabase with email: {supabase_email}")

        user_entity = UserEntity(
            id=supabase_user_id,
            email=supabase_email,
        )

        return self.user_repository.save(user_entity)
