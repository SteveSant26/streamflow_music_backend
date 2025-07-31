from dataclasses import dataclass


@dataclass
class UserProfileResponseDTO:
    """DTO para las respuestas del perfil de usuario."""

    id: str
    email: str
    profile_picture: str | None = None


@dataclass
class UploadProfilePictureRequestDTO:
    """DTO para la request de subida de foto de perfil."""

    user_id: str
    email: str
    profile_picture_file: bytes
