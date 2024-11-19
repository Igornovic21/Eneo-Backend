from django import forms

from user.functions.check_password import password_check

class ResetPasswordForm(forms.Form):
    password = forms.CharField(max_length=100)
    confirm_password = forms.CharField(max_length=100)

    def is_valid(self) -> bool:
        if not password_check(self.data["password"]): 
            return False
        if self.data["password"] != self.data["confirm_password"]:
            return False
        return super().is_valid()