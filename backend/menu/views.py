from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Piatto, Categoria
from .serializers import PiattoSerializer, CategoriaSerializer

# ==========================================
# GESTIONE CATEGORIE
# ==========================================

@api_view(['GET'])
def lista_categorie(request):
    """
    Restituisce tutte le categorie inserite.
    """
    categorie = Categoria.objects.all()
    serializer = CategoriaSerializer(categorie, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def aggiungi_categoria(request):
    """
    Aggiunge una nuova categoria.
    """
    serializer = CategoriaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['PUT', 'PATCH'])
def modifica_categoria(request, id):
    """
    Rinomina o modifica una categoria esistente.
    """
    categoria = get_object_or_404(Categoria, pk=id)
    partial = request.method == 'PATCH'
    serializer = CategoriaSerializer(categoria, data=request.data, partial=partial)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

@api_view(['DELETE'])
def elimina_categoria(request, id):
    """
    Cancella definitivamente una categoria dal DB.
    ATTENZIONE: Verranno eliminati anche tutti i piatti ad essa collegati (on_delete=CASCADE).
    """
    categoria = get_object_or_404(Categoria, pk=id)
    categoria.delete()
    return Response({"message": "Categoria eliminata con successo."}, status=204)


# ==========================================
# GESTIONE PIATTI
# ==========================================

@api_view(['GET'])
def visualizza_menu(request):
    """
    Restituisce la lista dei piatti attivi nel menu.
    Supporta i filtri via Query Params:
    - ?categoria=<id>
    - ?disponibile=true/false
    - ?allergeni=true/false
    """
    # Partiamo da tutti i piatti attivi
    piatti = Piatto.objects.filter(attivo=True)

    # Filtro Categoria
    categoria_id = request.query_params.get('categoria')
    if categoria_id:
        piatti = piatti.filter(categoria__id=categoria_id)

    # Filtro Disponibilità
    disponibile = request.query_params.get('disponibile')
    if disponibile is not None:
        # Converts string 'true' / 'false' to boolean
        disponibile_bool = disponibile.lower() == 'true'
        piatti = piatti.filter(disponibile=disponibile_bool)

    # Filtro Allergeni
    allergeni = request.query_params.get('allergeni')
    if allergeni is not None:
        allergeni_bool = allergeni.lower() == 'true'
        piatti = piatti.filter(allergeni=allergeni_bool)

    serializer = PiattoSerializer(piatti, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def aggiungi_piatto(request):
    """
    Aggiunge un nuovo piatto al database.
    """
    serializer = PiattoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
def dettaglio_piatto(request, id):
    """
    Restituisce i dettagli di un singolo piatto.
    """
    piatto = get_object_or_404(Piatto, pk=id)
    serializer = PiattoSerializer(piatto)
    return Response(serializer.data)

@api_view(['PUT', 'PATCH'])
def modifica_piatto(request, id):
    """
    Aggiorna i dati di un piatto esistente.
    """
    piatto = get_object_or_404(Piatto, pk=id)
    # partial=True allows omitting fields in PATCH requests
    partial = request.method == 'PATCH'
    serializer = PiattoSerializer(piatto, data=request.data, partial=partial)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

@api_view(['DELETE'])
def elimina_piatto(request, id):
    """
    Esegue un Soft Delete: imposta il piatto come non attivo invece di rimuoverlo dal DB.
    """
    piatto = get_object_or_404(Piatto, pk=id)
    piatto.attivo = False
    piatto.disponibile = False
    piatto.save()
    return Response({"message": "Piatto disattivato con successo."}, status=204)


