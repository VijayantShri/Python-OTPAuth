from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password = None, **kwargs):
        if not email:
            raise ValueError(("The email must be set"))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        kwargs.setdefault('is_active', True)

        if not kwargs.get('is_staff'):
            raise ValueError(('Superuser must have is_staff=True'))
        if not kwargs.get('is_superuser'):
            raise ValueError(('Superuser must have is_superuser=True'))
        
        return self.create_user(email=email, password=password, **kwargs)