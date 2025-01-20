from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from django.contrib.sites.shortcuts import get_current_site  
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action, authentication_classes
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser

from user.functions.check_password import password_check

from utils.send_emails import send_custom_email
from utils.logger import logger

from authorization.authentication import ExpiringTokenAuthentication, account_activation_token

from user.functions.login_user import login_user
from user.serializers.input_serializer import ChangePasswordSerializer, LoginSerializer, ResetPasswordSerializer, RegisterSerialiser
from user.serializers.output_serializer import UserSerializer
from region.serializers.output_serializer import RegionSerializer

from user.models import User
from region.models import Region


@authentication_classes([ExpiringTokenAuthentication])
class AuthViewSet(ViewSet):
    serializer_class = UserSerializer
    register_serializer = RegisterSerialiser
    change_password_serializer = ChangePasswordSerializer
    reset_password_serializer = ResetPasswordSerializer
    login_serializer = LoginSerializer
    region_serializer = RegionSerializer
    
    def get_object(self, email:str):
        try:
            account = User.objects.get(email=email)
            return account
        except User.DoesNotExist:
            data = {
                "status": False,
                "message": "Ce compte n'existe pas"
            }
            logger.warning("Ce compte n'existe pas")
            return Response(data, status=status.HTTP_404_NOT_FOUND)
    
    def get_object_pk(self, pk:str):
        try:
            account = User.objects.get(pk=pk)
            return account
        except User.DoesNotExist:
            data = {
                "status": False,
                "message": "Ce compte n'existe pas"
            }
            logger.warning("Ce compte n'existe pas")
            return Response(data, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        return Response({"message": "This is the auth base url"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], name='register', url_name='register', permission_classes=[IsAdminUser])
    def register(self, request):
        serializer = self.register_serializer(data=request.data)
        if serializer.is_valid():
            if not password_check(serializer.data["password"]):
                logger.warning("Votre mot de passe est faible")
                return Response({
                    "status": False,
                    "message": "Votre mot de passe est faible"
                }, status=status.HTTP_400_BAD_REQUEST)

            if serializer.data["password"] != serializer.data["confirm_password"]:
                logger.warning("Les mots de passe ne correspondent pas")
                return Response({
                    "status": False, 
                    "message": "Les mots de passe ne correspondent pas"
                }, status=status.HTTP_400_BAD_REQUEST)

            user_serializer = self.serializer_class(data=request.data)

            if user_serializer.is_valid():
                password = make_password(serializer.data["password"])
                email = user_serializer.save(password=password)

                account = self.get_object(email)
                if type(account) is Response : return account

                logger.info("Compte crée avec succès")
                return Response({
                    "status": True,
                    "message": "Compte crée avec succès",
                    "detail": { "id": account.pk }
                }, status=status.HTTP_200_OK)
            logger.warning("Ces informations ont déjà été utilisées")
            return Response({
                "status": False,
                "message": "Ces informations ont déjà été utilisées"
            }, status=status.HTTP_400_BAD_REQUEST)

        logger.error("Données saisies invalides")
        return Response({
            "status": False,
            "message": "Données saisies invalides",
            "detail": serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], name='login', url_name='login', permission_classes=[AllowAny])
    def login(self, request):
        user_serializer = self.login_serializer(data=request.data)
        if user_serializer.is_valid():
            email = user_serializer.data["email"]
            password = user_serializer.data["password"]
            
            account = self.get_object(email)
            if type(account) is Response : return account

            if not check_password(password, account.password):
                data = {
                    "status": False,
                    "message": "Aucune correspondance pour cet email/mot de passe"
                }
                logger.warning("Aucune correspondance pour cet email/mot de passe")
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            data = login_user(account)
            logger.info("Compte connecté avec succès")
            return Response({
                "status": True,
                "message": "Compte connecté avec succès",
                "detail": data
            }, status=status.HTTP_200_OK)

        logger.error("Données saisies invalides")
        return Response({
            "status": False,
            "message": "Données saisies invalides"
        }, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['post'], name='change-password', url_name='change-password', permission_classes=[IsAdminUser])
    def change_password(self, request):
        serializer = self.change_password_serializer(data=request.data)
        if serializer.is_valid():
            # if not check_password(serializer.data['old_password'], request.user.password):
            #     logger.warning("Ancien mot de passe incorrect")
            #     return Response({
            #         "status": False, 
            #         "message": "Ancien mot de passe incorrect"}, status=status.HTTP_400_BAD_REQUEST)

            if not password_check(serializer.data['new_password']):
                logger.warning("Votre mot de passe est faible")
                return Response({
                    "status": False,
                    "message": "Votre mot de passe est faible"}, status=status.HTTP_400_BAD_REQUEST)

            if serializer.data["new_password"] != serializer.data["confirm_password"]:
                logger.warning("Les mots de passe ne correspondent pas")
                return Response({
                    "status": False,
                    "message": "Les mots de passe ne correspondent pas"}, status=status.HTTP_400_BAD_REQUEST)

            data = request.data
            user = self.get_object_pk(data["user"])
            if type(user) is Response : return user
            # user = self.get_object(request.user.email)
            # if type(user) is Response : return user
            
            user.set_password(serializer.data["new_password"])
            token, s = Token.objects.get_or_create(user=user)
            token.delete()
            user.save()
            logger.info("Mot de passe changé avec succès")
            return Response({
                "status": True,
                "message": "Mot de passe changé avec succès"}, status=status.HTTP_200_OK)

        logger.error("Données saisies invalides")
        return Response({
            "status": False,
            "message": "Données saisies invalides",
            "detail": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], name='user', url_name='user', permission_classes=[IsAdminUser])
    def user(self, request):
        users_data = []
        users = User.objects.all()

        for user in users:
            user_serializer = self.serializer_class(user, many=False)
            data = user_serializer.data
            data["regions"] = self.region_serializer(user.region.all(), many=True).data
            users_data.append(data)

        logger.info("User list generated successfully")
        return Response({
            "status": True,
            "message": "User list generated successfully",
            "detail": users_data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put'], name='region', url_name='region', permission_classes=[IsAdminUser])
    def region(self, request):
        data = request.data
        user = self.get_object_pk(data["user"])
        if type(user) is Response : return user

        user.region.clear()
        user.save()

        for region in data["regions"]:
            user.region.add(region)
        
        user.save()

        logger.info("Regions assigned to the user successfully")
        return Response({
            "status": True,
            "message": "Regions assigned to the user successfully",
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], name='info', url_name='info', permission_classes=[IsAuthenticated])
    def info(self, request):
        account = self.get_object(request.user.email)
        if type(account) is Response : return account
            
        if account.is_active:
            user_serializer = self.serializer_class(account, many=False)
            data = user_serializer.data
            data["regions"] = self.region_serializer(request.user.region.all(), many=True).data
            logger.info("Compte connecté avec succès")
            return Response({
                "status": True,
                "message": "Compte connecté avec succès",
                "detail": data
            }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], name='reset-password', url_name='reset-password', permission_classes=[AllowAny])
    def reset_password(self, request):
        serializer = self.reset_password_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data["email"]
            
            account = self.get_object(email)
            if type(account) is Response : return account
            
            account.reset_password = True
            account.save()
            token, s = Token.objects.get_or_create(user=account)
            token.delete()
             
            current_site = get_current_site(request)  
            html_content = render_to_string('emails/reset-password.html', {
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(account.pk)),
                'token': account_activation_token.make_token(account),
            })

            res = send_custom_email(email, 'Reset Password', html_content)
            if res:
                logger.info("Votre demande a été traitée, merci de vérifier votre boîte mail")
                return Response({
                    "status": True,
                    "message": "Votre demande a été traitée, merci de vérifier votre boîte mail"
                }, status=status.HTTP_200_OK)
            logger.critical("Error sending email")
            return Response({
                "status": False,
                "message": "Error sending email"
            }, status=status.HTTP_400_BAD_REQUEST)

        logger.error("Données saisies invalides")
        return Response({
            "status": False,
            "message": "Données saisies invalides"
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['put'], name='modify', url_name='modify', permission_classes=[IsAuthenticated])
    def modify(self, request):
        data = request.data
        account = self.get_object_pk(data["user"])
        if type(account) is Response : return account

        serializer = self.serializer_class(account, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            account.username = data["email"]
            account.save()
            logger.info("Vos informations ont été mises à jour")
            return Response({
                "status": True,
                "message": "Vos informations ont été mises à jour",
                "detail": serializer.data
            }, status=status.HTTP_200_OK)
        
        logger.error("Données saisies invalides")
        return Response({
            "status": False,
            "message": "Données saisies invalides",
            "detail": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], name='logout', url_name='logout', permission_classes=[IsAuthenticated])
    def logout(self, request):
        request.user.auth_token.delete()
        data = {
            "status": True,
            "message": "Déconnexion réussie"
        }
        logger.info("Déconnexion réussie")
        return Response(data, status=status.HTTP_200_OK)