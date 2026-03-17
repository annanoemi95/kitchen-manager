from django.urls import path
from .views import (
    lista_categorie,
    aggiungi_categoria,
    modifica_categoria,
    elimina_categoria,
    visualizza_menu,
    aggiungi_piatto,
    dettaglio_piatto,
    modifica_piatto,
    elimina_piatto
)

urlpatterns = [
    # ==========================================
    # Categorie
    # ==========================================
    path('categorie/', lista_categorie, name='lista_categorie'),
    path('categorie/aggiungi/', aggiungi_categoria, name='aggiungi_categoria'),
    path('categorie/<uuid:id>/modifica/', modifica_categoria, name='modifica_categoria'),
    path('categorie/<uuid:id>/elimina/', elimina_categoria, name='elimina_categoria'),

    # ==========================================
    # Piatti
    # ==========================================
    path('visualizza/', visualizza_menu, name='visualizza_menu'),
    path('piatti/aggiungi/', aggiungi_piatto, name='aggiungi_piatto'),
    path('piatti/<uuid:id>/', dettaglio_piatto, name='dettaglio_piatto'),
    path('piatti/<uuid:id>/modifica/', modifica_piatto, name='modifica_piatto'),
    path('piatti/<uuid:id>/elimina/', elimina_piatto, name='elimina_piatto'),
]