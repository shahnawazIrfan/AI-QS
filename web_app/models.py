from bson import ObjectId
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.conf import settings
from django.contrib.sessions.models import Session
# Create your models here.


class UserProfileManager(BaseUserManager):

    def create_user(self, name, email, role, terms_conditions, password=None):

        if not any([name, email, role, terms_conditions]):
            raise ValueError(
                "[name, email, terms_conditions] all fields are required")

        email = self.normalize_email(email=email)

        user = self.model(name=name, email=email, role=role, terms_conditions=terms_conditions)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, name, email, role, terms_conditions, password=None):

        user = self.create_user(name, email, role, terms_conditions, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class UserProfile(AbstractBaseUser, PermissionsMixin):

    name = models.CharField(max_length=60, blank=False, null=False)
    email = models.EmailField(max_length=50, unique=True)
    role_choice = (
        (1, "User"),
        (2, "Super User"),
        (3, "Admin")
    )
    role = models.IntegerField(choices=role_choice, default=1)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    # is_superuser = models.BooleanField(default=True)
    terms_conditions = models.BooleanField(default=False, null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserProfileManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'terms_conditions']

    def get_name(self):
        return f'{self.name}'

    def __str__(self):
        return f"{self.get_name()} | {self.email}"

    def is_user(self):
        return self.role == 1

    def is_superuser(self):
        return self.role == 2

    def is_admin(self):
        return self.role == 3

    class Meta:
        ordering = ['-created_at']


class UserSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)  

    def __str__(self):
        return f"{self.user.name} | {self.session.session_key}"

    class Meta:
        verbose_name_plural = "Sessions"


class CostSummarySection(models.Model):
    _id = models.CharField(max_length=24, primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Cost Section"


class CostSummary(models.Model):
    _id = models.CharField(max_length=24, primary_key=True)
    ref = models.CharField(max_length=50)
    item = models.CharField(max_length=255, blank=True, null=True)
    contract_sum = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    certified_payments = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    accrued_payments = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_expenditure = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    variance_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    variance_period = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    section = models.ForeignKey(CostSummarySection, on_delete=models.CASCADE, related_name="cost_summaries")

    def __str__(self):
        return f"{self.section.name} - {self.ref}"

    class Meta:
        verbose_name_plural = "Cost Summary"


class ContractSumSection(models.Model):
    _id = models.CharField(max_length=24, primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Contract Sum Section"


class ContractSum(models.Model):
    _id = models.CharField(max_length=24, primary_key=True)
    ref = models.CharField(max_length=50)
    item = models.CharField(max_length=255, blank=True, null=True)
    contract_sum = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    certified_payments = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    section = models.ForeignKey(ContractSumSection, on_delete=models.CASCADE, related_name="contract_sums")

    def __str__(self):
        return f"{self.section.name} - {self.ref}"

    class Meta:
        verbose_name_plural = "Contract Sum"


class ChangeBreakDownSection(models.Model):
    _id = models.CharField(max_length=24, primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Change Break Down Section"


class ChangeBreakDown(models.Model):
    _id = models.CharField(max_length=24, primary_key=True)
    ref = models.CharField(max_length=50)
    item = models.CharField(max_length=255, blank=True, null=True)
    certified_payments = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_expenditure = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    variance_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    variance_period = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    section = models.ForeignKey(ChangeBreakDownSection, on_delete=models.CASCADE, related_name="change_breakdown")

    def __str__(self):
        return f"{self.section.name} - {self.ref}"

    class Meta:
        verbose_name_plural = "Change Break Down"


class CostReporting(models.Model):
    _id = models.CharField(max_length=24, primary_key=True)
    interim_payments = models.CharField(max_length=50)
    month = models.DateTimeField(blank=True, null=True)
    forecast_monthly = models.FloatField(blank=True, null=True)
    actual_monthly = models.FloatField(blank=True, null=True)
    forecast_comulative = models.FloatField(blank=True, null=True)
    actual_comulative = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.interim_payments} - {self.month}"

    class Meta:
        verbose_name_plural = "Cost Reporting"