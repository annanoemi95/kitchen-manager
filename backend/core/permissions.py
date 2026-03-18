from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """
    Permette l'accesso solo agli utenti con role='admin'.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'admin'
        )


class IsCustomer(BasePermission):
    """
    Permette l'accesso solo agli utenti con role='customer'.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'customer'
        )


class IsAdminOrReadOnly(BasePermission):
    """
    Admin: accesso completo (lettura + scrittura).
    Customer autenticato: solo lettura.
    Usato da Marika per il menu — i piatti li gestisce solo l'admin.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return request.user.role == 'admin'


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level permission — usare sempre insieme a IsAuthenticated.
    Admin: vede e modifica tutto.
    Customer: vede e modifica solo i propri oggetti.
    Usato da Chiara per gli ordini.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        owner = getattr(obj, 'user', None) or getattr(obj.order, 'user', None)
        return owner == request.user