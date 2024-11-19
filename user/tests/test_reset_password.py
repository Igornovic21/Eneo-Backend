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
    
    # reset password tests
    def test_wrong_data_reset_password(self):
        response = self.client.post("/auth/forgot_password/", {
            "email": "TextExist",
        }, format="json")
        
        self.assertEqual(response.status_code, 400)
        
    def test_reset_password(self):
        response = self.client.post("/auth/forgot_password/", {
            "email": "test.exist@example.com",
        }, format="json")
        
        if response.data["status"]:
            self.assertEqual(response.status_code, 200)
        else:
            self.assertEqual(response.status_code, 400)
