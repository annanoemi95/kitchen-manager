from rest_framework import serializers
from .models import Categoria, Piatto

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        # L'admin inserisce solo il nome
        fields = ['id', 'nome']

class PiattoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Piatto
        # Tutti i campi necessari per gestire il piatto
        fields = [
            'id', 
            'nome', 
            'descrizione', 
            'prezzo', 
            'categoria', 
            'ingredienti', 
            'allergeni', 
            'attivo',
            'disponibile'
        ]
