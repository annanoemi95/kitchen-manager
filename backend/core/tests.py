from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from .models import Category, Dish, Order, Review

User = get_user_model()

class ReviewSecurityTests(APITestCase):
    def setUp(self):
        # Creazione Utenti
        self.admin = User.objects.create_user(username='admin_boss', password='password123', role='admin')
        self.user_a = User.objects.create_user(username='utente_a', password='password123', role='customer')
        self.user_b = User.objects.create_user(username='utente_b', password='password123', role='customer')
        
        # Creazione Ordine consegnato per Utente A
        self.order_a = Order.objects.create(user=self.user_a, status='delivered', total_amount=25.0)
        # Creazione Ordine NON consegnato per Utente A
        self.order_pending = Order.objects.create(user=self.user_a, status='pending', total_amount=15.0)
        # Creazione Ordine consegnato per Utente B
        self.order_b = Order.objects.create(user=self.user_b, status='delivered', total_amount=20.0)
        # Creazione secondo Ordine consegnato per Utente A
        self.order_c = Order.objects.create(user=self.user_a, status='delivered', total_amount=12.0)

    def test_ai_summary_access_denied_for_customer(self):
        """SCENARIO 1: Un cliente prova a fare l'analisi AI (Deve fallire 403)"""
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get('/api/reviews/ai-summary/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_review_other_user_order_forbidden(self):
        """SCENARIO 2: Utente B prova a recensire l'ordine di Utente A (Deve fallire)"""
        self.client.force_authenticate(user=self.user_b)
        data = {'order': self.order_a.id, 'rating': 5, 'comment': 'Rubo la recensione!'}
        response = self.client.post('/api/reviews/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_review_non_delivered_order_forbidden(self):
        """SCENARIO 3: Recensione su ordine non ancora consegnato (Deve fallire)"""
        self.client.force_authenticate(user=self.user_a)
        data = {'order': self.order_pending.id, 'rating': 5, 'comment': 'Ancora non mi è arrivato nulla!'}
        response = self.client.post('/api/reviews/', data)
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN]) 

    @patch('core.services.AIService.analyze_reviews')
    def test_admin_can_access_ai_summary(self, mock_ai_analyze):
        """SCENARIO 4: L'admin accede all'analisi (Deve riuscire 200 con Mocking)"""
        
        # Creiamo 3 recensioni per superare il blocco "dati insufficienti"
        Review.objects.create(order=self.order_a, rating=5, comment="Ottimo!")
        Review.objects.create(order=self.order_b, rating=4, comment="Buono!")
        Review.objects.create(order=self.order_c, rating=5, comment="Perfetto!") 
        
        # Simuliamo la risposta deterministica di Gemini
        mock_ai_analyze.return_value = {
            "sentiment_score": 5,
            "main_complaint": "null",
            "top_dish": "Pizza Margherita",
            "advice": "Continua così!"
        }
        
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/reviews/ai-summary/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results']['top_dish'], "Pizza Margherita")
        mock_ai_analyze.assert_called_once()


class AdminMenuManagementTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='menu_admin',
            password='password123',
            role='admin',
        )
        self.customer = User.objects.create_user(
            username='menu_customer',
            password='password123',
            role='customer',
        )
        self.category = Category.objects.create(name='Pizze')
        self.secondary_category = Category.objects.create(name='Bevande')
        self.active_dish = Dish.objects.create(
            name='Margherita',
            description='Pomodoro e mozzarella',
            price=8.50,
            category=self.category,
            is_active=True,
            is_available=True,
        )
        self.inactive_dish = Dish.objects.create(
            name='Pizza Storica',
            description='Fuori menu',
            price=15.00,
            category=self.category,
            is_active=False,
            is_available=False,
        )

    def test_admin_can_list_all_dishes_for_management(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get('/api/admin/dishes/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        returned_ids = {dish['id'] for dish in response.data}
        self.assertEqual(returned_ids, {self.active_dish.id, self.inactive_dish.id})

    def test_customer_cannot_manage_dishes(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.post(
            '/api/admin/dishes/',
            {
                'name': 'Nuovo piatto',
                'description': 'Test',
                'price': '9.50',
                'category': self.category.id,
                'is_active': True,
                'is_available': True,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_update_and_disable_dish(self):
        self.client.force_authenticate(user=self.admin)

        create_response = self.client.post(
            '/api/admin/dishes/',
            {
                'name': 'Limonata',
                'description': 'Bibita fresca',
                'price': '3.50',
                'category': self.secondary_category.id,
                'is_active': True,
                'is_available': True,
            },
            format='json',
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        created_dish_id = create_response.data['id']

        update_response = self.client.patch(
            f'/api/admin/dishes/{created_dish_id}/',
            {
                'name': 'Limonata artigianale',
                'is_available': False,
            },
            format='json',
        )

        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data['name'], 'Limonata artigianale')
        self.assertFalse(update_response.data['is_available'])

        disable_response = self.client.delete(f'/api/admin/dishes/{created_dish_id}/')

        self.assertEqual(disable_response.status_code, status.HTTP_204_NO_CONTENT)

        disabled_dish = Dish.objects.get(id=created_dish_id)
        self.assertFalse(disabled_dish.is_active)
        self.assertFalse(disabled_dish.is_available)
