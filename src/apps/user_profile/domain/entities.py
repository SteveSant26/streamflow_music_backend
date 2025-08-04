from dataclasses import dataclass


@dataclass
class UserProfileEntity:
    id: str
    email: str
    profile_picture: str | None

    @property
    def is_authenticated(self):
        """Required by Django's authentication system"""
        return True

    @property
    def is_anonymous(self):
        """Required by Django's authentication system"""
        return False
