from rest_framework import serializers
from .models import (
    Usuario, Perfil, Artista, Album, Genero,
    Cancion, Playlist, Suscripcion,
    EstadisticaUsuario, EstadisticaArtista, EstadisticaGenero,
    EstadisticaCancion, EstadisticaCancionUsuario
)

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'

class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = '__all__'

class ArtistaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artista
        fields = '__all__'

class AlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = '__all__'

class GeneroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genero
        fields = '__all__'

class CancionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cancion
        fields = '__all__'

class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = '__all__'

class SuscripcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suscripcion
        fields = '__all__'

class EstadisticaUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadisticaUsuario
        fields = '__all__'

class EstadisticaArtistaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadisticaArtista
        fields = '__all__'

class EstadisticaGeneroSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadisticaGenero
        fields = '__all__'

class EstadisticaCancionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadisticaCancion
        fields = '__all__'

class EstadisticaCancionUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadisticaCancionUsuario
        fields = '__all__'
