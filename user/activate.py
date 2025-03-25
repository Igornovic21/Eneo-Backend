from django.utils.translation import gettext as _
from django.shortcuts import render
from django.http import HttpResponse  
from django.utils.encoding import force_str  
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string

from utils.send_emails import send_custom_email
from utils.logger import logger

from authorization.authentication import account_activation_token  

from user.forms import ResetPasswordForm
from user.models import User

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        context = {
            "status": "Success",
            "message": "Congratulations your account has been successfully verified. Go back to the app and enjoy our experience."
        }
        if not user.email_verified:
            user.email_verified = True
            user.save()
            html_content = render_to_string('emails/email-verified.html')
            res = send_custom_email(user.email, 'Votre email a été vérifié - Wole', html_content)
            if not res:
                logger.critical(_("Error sending email"))
                return render(request, 'activate.html', context)
        logger.info("account has been successfully verified")
        return render(request, 'activate.html', context)
    else:
        context = {
            "status": "Failed",
            "message": "Activation link has already been used or expired !!"
        }
        return render(request, 'activate.html', context)

@csrf_exempt
def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        
    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            reset_password_form = ResetPasswordForm(request.POST)
            if reset_password_form.is_valid():
                user.set_password(reset_password_form.data['password'])
                user.reset_password = False
                user.save()
                html_content = render_to_string('emails/confirm-reset-password.html')
                send_custom_email(user.email, 'Reset Password', html_content)
                context = {
                    "status": 1,
                    "uid": uidb64,
                    "token": token,
                    "message": "Congratulations your password has been successfully changed. Go back to the app and enjoy our experience."
                }
                logger.info("password has been successfully changed")
                return render(request, 'reset-password.html', context)
            else:
                context = {
                    "status": 0,
                    "uid": uidb64,
                    "token": token,
                    "message": "Passwords doesn't match or are too weak"
                }
                logger.info("password has been successfully changed")
                return render(request, 'reset-password.html', context)  
        context = {
            "uid": uidb64,
            "token": token,
            "message": "Activation link has already been used or expired !!"
        }
        return render(request, 'reset-password.html', context)

    else:
        context = {
            "status": "Failed",
            "message": "Activation link has already been used or expired !!"
        }
        return render(request, 'reset-password.html', context)
