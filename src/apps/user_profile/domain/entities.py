from dataclasses import dataclass


@dataclass
class UserProfileEntity:
    id: str
    email: str
    profile_picture: str | None
