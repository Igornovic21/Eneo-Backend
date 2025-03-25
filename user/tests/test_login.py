from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from user.models import User

# Create your tests here.
class AuthTestCase(TestCase):
    client: APIClient = APIClient()

    def setUp(self) -> None:
        user = User.objects.create(username="TestExist", email="test.exist@example.com")
        user.set_password("Tentee237!")
        user.save()
        
        inactive = User.objects.create(username="Inactive", email="inactive@example.com", is_active=False)
        inactive.set_password("Inactive237!")
        inactive.save()
        return super().setUp()
    
    # login tests
    def test_wrong_data_login(self):
        response = self.client.post("/auth/register/", {
            "username": "test.exist@example.com",
            "password": 987654321,
        }, format="json")
        
        self.assertEqual(response.status_code, 400)
        
    def test_unexistant_account_login(self):
        response = self.client.post("/auth/login/", {
            "email": "igor@example.com",
            "password": "123456789",
        }, format="json")
        
        self.assertEqual(response.status_code, 404)
        
    def test_user_wrong_credentials_login(self):
        response = self.client.post("/auth/login/", {
            "email": "test.exist@example.com",
            "password": "123456789",
        }, format="json")
        
        self.assertEqual(response.status_code, 400)
        
    def test_user_inactive_login(self):
        response = self.client.post("/auth/login/", {
            "email": "inactive@example.com",
            "password": "Inactive237!",
        }, format="json")
        
        self.assertEqual(response.status_code, 401)
        
    def test_user_login(self):
        response = self.client.post("/auth/login/", {
            "email": "test.exist@example.com",
            "password": "Tentee237!",
        }, format="json")
        
        self.assertEqual(response.status_code, 200)
    
    def test_get_user_info(self):
        account = User.objects.get(email="test.exist@example.com")
        token, _ = Token.objects.get_or_create(user = account)
        
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
                
        response = client.get("/auth/info/")
        self.assertEqual(response.status_code, 200)

    def test_user_logout(self):
        account = User.objects.get(email="test.exist@example.com")
        token, _ = Token.objects.get_or_create(user = account)
        
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)        
        response = client.post("/auth/logout/")
        
        self.assertEqual(response.status_code, 200)
