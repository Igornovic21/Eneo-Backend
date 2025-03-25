from django.test import TestCase

from rest_framework.test import APIClient

from user.models import User

# Create your tests here.
class AuthTestCase(TestCase):
    client = APIClient()

    def setUp(self) -> None:
        user = User.objects.create(username="TestExist", email="test.exist@example.com")
        user.set_password("Tentee237!")
        user.save()
        
        inactive = User.objects.create(username="Inactive", email="inactive@example.com", is_active=False)
        inactive.set_password("Inactive237!")
        inactive.save()
        return super().setUp()
    
    # register test
    def test_wrong_data_register(self):
        response = self.client.post("/auth/register/", {
            "username": 123456789,
            "email": "igor.com",
            "password": "azerty",
            "confirm_password": 987654321
        }, format="json")
        self.assertEqual(response.status_code, 400)
    
    def test_weak_password_register(self):
        response = self.client.post("/auth/register/", {
            "username": "Igornovic",
            "email": "kamguefokoigor@gmail.com",
            "password": "azerty",
            "confirm_password": "azerty"
        }, format="json")
        self.assertEqual(response.status_code, 400)
    
    def test_mismatch_password_register(self):
        response = self.client.post("/auth/register/", {
            "username": "Igornovic",
            "email": "kamguefokoigor@gmail.com",
            "password": "Igor.123456",
            "confirm_password": "Igor.123456789"
        }, format="json")
        self.assertEqual(response.status_code, 400)
            
    def test_user_register(self):
        response = self.client.post("/auth/register/", {
            "username": "Igornovic",
            "email": "kamguefokoigor@gmail.com",
            "password": "Igor.123456",
            "confirm_password": "Igor.123456"
        }, format="json")
        
        if response.data["status"]:
            self.assertEqual(response.status_code, 200)
        else:
            self.assertEqual(response.status_code, 400)
    
    def test_user_exists_register(self):
        response = self.client.post("/auth/register/", {
            "username": "TestExist",
            "email": "test.exist@example.com",
            "password": "Test237",
            "confirm_password": "Test237"
        }, format="json")
        
        self.assertEqual(response.status_code, 400)
    