# backend/volunteers/models.py
from django.db import models
from django.contrib.auth import get_user_model  # <-- Added for User link
from django.utils import timezone  # <-- Already present

User = get_user_model()  # <-- Added

class Volunteer(models.Model):
    """Main volunteer registration model"""

    # ---------- CHANGE APPLIED ----------
    # Link to built-in User model to enable user.volunteer reverse lookup
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='volunteer',  # <-- Allows _get_volunteer_for_user(user)
        null=True, blank=True       # <-- Optional for existing volunteers
    )
    # ---------- END OF CHANGE ----------

    # Basic Info
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    nickname = models.CharField(max_length=100, blank=True)
    sex = models.CharField(max_length=50)
    birthdate = models.DateField()
    volunteer_identifier = models.CharField(max_length=50, unique=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_name(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}"

    # ---------- CHANGE APPLIED ----------
    # Auto-generate volunteer_identifier in format UNP-MMDD-YYYY-XXX
    def save(self, *args, **kwargs):
        if not self.volunteer_identifier:
            today = timezone.now()
            date_str = today.strftime("%m%d-%Y")  # MMDD-YYYY
            prefix = f"UNP-{date_str}-"
            # Count existing volunteers today to get sequential number
            today_count = Volunteer.objects.filter(volunteer_identifier__startswith=prefix).count() + 1
            self.volunteer_identifier = f"{prefix}{today_count:03d}"  # e.g., UNP-1209-2025-001
        super().save(*args, **kwargs)
    # ---------- END OF CHANGE ----------

class VolunteerAccount(models.Model):
    volunteer = models.OneToOneField(Volunteer, on_delete=models.CASCADE, related_name="account")
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    
    def __str__(self):
        return self.email

# --- The rest of your models remain unchanged ---
class VolunteerContact(models.Model):
    volunteer = models.OneToOneField(Volunteer, on_delete=models.CASCADE, related_name="contact")
    mobile_number = models.CharField(max_length=20, blank=True)
    facebook_link = models.URLField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.volunteer.get_full_name()} Contact"


class VolunteerAddress(models.Model):
    volunteer = models.OneToOneField(Volunteer, on_delete=models.CASCADE, related_name="address")
    street_address = models.CharField(max_length=255, blank=True)
    province = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.volunteer.get_full_name()} Address"


class VolunteerEducation(models.Model):
    volunteer = models.OneToOneField(Volunteer, on_delete=models.CASCADE, related_name="education")
    degree_program = models.CharField(max_length=200, blank=True)
    year_level = models.CharField(max_length=50, blank=True)
    college = models.CharField(max_length=50, blank=True)
    department = models.CharField(max_length=50, blank=True)
    year_graduated = models.CharField(max_length=4, blank=True)

    def __str__(self):
        return f"{self.volunteer.get_full_name()} Education"


class EmergencyContact(models.Model):
    volunteer = models.OneToOneField(Volunteer, on_delete=models.CASCADE, related_name="emergency_contact")
    name = models.CharField(max_length=200, blank=True)
    relationship = models.CharField(max_length=100,blank=True)
    contact_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"{self.volunteer.get_full_name()} Emergency Contact"


class VolunteerBackground(models.Model):
    volunteer = models.OneToOneField(Volunteer, on_delete=models.CASCADE, related_name="background")
    occupation = models.CharField(max_length=255, blank=True)
    org_affiliation = models.CharField(max_length=255, blank=True)
    hobbies_interests = models.TextField(blank=True)

    def __str__(self):
        return f"{self.volunteer.get_full_name()} Background"


class VolunteerAffiliation(models.Model):
    volunteer = models.ForeignKey(
        'core.Volunteer',  
        on_delete=models.CASCADE
    )
    affiliation = models.CharField(max_length=255)
    organization = models.CharField(max_length=255, blank=True, null=True)
