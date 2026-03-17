import uuid
from django.db import models
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from rest_framework.exceptions import ValidationError

class Categoria(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    nome = models.CharField(
        max_length=100,
        unique=True,
        help_text='Esempi: "Primi Piatti", "Secondi", "Bevande", "Dolci"'
    )

    class Meta:
        db_table = "categorie"
    
    def __str__(self):
        return self.nome

class Piatto(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    nome = models.CharField(
        max_length=200
    )
    descrizione = models.TextField(
        blank=True, 
        null=True
    )
    prezzo = models.DecimalField(
        max_digits=6, 
        decimal_places=2
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name="piatti"
    )
    ingredienti = models.TextField(
        help_text="Lista degli ingredienti separati da virgola"
    )
    allergeni = models.BooleanField(
        default=False, 
        help_text="Selezionare se il piatto contiene sostanze allergizzanti"
    )
    attivo = models.BooleanField(
        default=True, 
        help_text="Indica se il piatto è presente nel menu corrente"
    )
    disponibile = models.BooleanField(
        default=True, 
        help_text="Se disattivato, il piatto apparirà come 'esaurito' e non sarà ordinabile"
    )

    class Meta:
        db_table = "piatti"

    def __str__(self):
        return self.nome


# ==========================================
# PATTERN OSSERVATORE (PER LO STORICO)
# ==========================================
# L'OsservatoreStorico monitora le modifiche allo stato dei piatti e
# garantisce che i piatti ritirati dal menu non vengano eliminati
# dal database, preservando la cronologia degli ordini esistenti.

class OsservatoreBase:
    """
    Classe base per gestire la logica di osservazione dei modelli.
    """
    def aggiorna(self, istanza, **kwargs):
        raise NotImplementedError("Le sottoclassi devono implementare il metodo aggiorna.")

class OsservatorePiatto(OsservatoreBase):
    """
    Osservatore per applicare la logica di business definita per il Menu:
    1. attivo=Sì AND disponibile=Sì -> Visibile e ordinabile.
    2. attivo=Sì AND disponibile=No -> Visibile ma 'Esaurito'.
    3. attivo=No AND disponibile=No -> Rimosso dal menu, mantenuto nel database.
    """
    def aggiorna(self, istanza, **kwargs):
        # Se il piatto viene rimosso dal menu (attivo=False),
        # deve necessariamente diventare non ordinabile (disponibile=False).
        if not istanza.attivo and istanza.disponibile:
            istanza.disponibile = False

# Istanza globale dell'osservatore
osservatore_piatto = OsservatorePiatto()

@receiver(pre_save, sender=Piatto)
def osservatore_pre_salvataggio_piatto(sender, instance, **kwargs):
    """
    Intercetta il salvataggio per validare la coerenza degli stati.
    """
    osservatore_piatto.aggiorna(instance)

@receiver(pre_delete, sender=Piatto)
def impedisci_eliminazione_fisica_piatto(sender, instance, **kwargs):
    """
    Blocca l'eliminazione dal database per preservare lo storico.
    """
    raise ValidationError(
        "I piatti non possono essere eliminati definitivamente per non rompere lo storico degli ordini. "
        "Per favore, usa il campo 'Attivo' per rimuoverlo dal menu."
    )