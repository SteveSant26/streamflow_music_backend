from dataclasses import dataclass


@dataclass
class UserEntity:
    id: str
    email: str
    profile_picture: str | None = None
