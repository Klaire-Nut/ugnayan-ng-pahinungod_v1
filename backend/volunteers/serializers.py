# backend/volunteers/serializers.py
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.db import transaction

from core.utils import generate_volunteer_identifier
from core.models import (
    Volunteer,
    VolunteerContact,
    VolunteerAddress,
    VolunteerBackground,
    EmergencyContact,
    VolunteerAccount,
    ProgramInterest,
    StudentProfile,
    AlumniProfile,
    StaffProfile,
    FacultyProfile,
    RetireeProfile,
    VolunteerMeta,
    VolunteerEvent,
)

# ---------------------------------------------------------------------
# AFFILIATION PROFILE SERIALIZERS
# ---------------------------------------------------------------------
class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ["degree_program", "year_level", "college"]


class AlumniProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlumniProfile
        fields = ["constituent_unit", "degree_program", "year_graduated"]


class StaffProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffProfile
        fields = ["office_department", "designation"]


class FacultyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacultyProfile
        fields = ["college", "department"]


class RetireeProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RetireeProfile
        fields = ["designation_while_in_up", "office_college_department"]


# ---------------------------------------------------------------------
# VOLUNTEER ACCOUNT / BASIC SERIALIZERS
# ---------------------------------------------------------------------
class VolunteerAccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, required=False)

    class Meta:
        model = VolunteerAccount
        fields = ["email", "password"]

    def validate_email(self, value):
        # When creating a new account, ensure email is unique.
        # On update, instance will exist and we should allow same email for that instance.
        if self.instance is None and VolunteerAccount.objects.filter(email=value).exists():
            raise serializers.ValidationError("A volunteer with this email already exists.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        if password:
            validated_data["password"] = make_password(password)
        return VolunteerAccount.objects.create(**validated_data)


class VolunteerContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerContact
        fields = ["mobile_number", "facebook_link"]


class VolunteerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerAddress
        fields = ["street_address", "province", "region"]


class VolunteerBackgroundSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerBackground
        fields = ["occupation", "org_affiliation", "hobbies_interests"]


class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = ["name", "relationship", "contact_number", "address"]


# ---------------------------------------------------------------------
# META SERIALIZER
# ---------------------------------------------------------------------
class VolunteerMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerMeta
        fields = [
            "volunteer_status",
            "tagapag_ugnay",
            "other_organization",
            "organization_name",
            "affirmative_action_subjects",
            "how_did_you_hear",
        ]


# ---------------------------------------------------------------------
# VOLUNTEER REGISTRATION SERIALIZER
# (keeps nested creation behavior)
# ---------------------------------------------------------------------
class VolunteerRegistrationSerializer(serializers.Serializer):
    # main volunteer fields
    first_name = serializers.CharField()
    middle_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField()
    nickname = serializers.CharField(required=False, allow_blank=True)
    sex = serializers.CharField()
    birthdate = serializers.DateField()
    affiliation_type = serializers.CharField()

    # nested
    account = VolunteerAccountSerializer()
    contact = VolunteerContactSerializer()
    address = VolunteerAddressSerializer()
    background = VolunteerBackgroundSerializer()
    emergency_contact = EmergencyContactSerializer()

    # affiliation optionals
    student_profile = StudentProfileSerializer(required=False)
    alumni_profile = AlumniProfileSerializer(required=False)
    staff_profile = StaffProfileSerializer(required=False)
    faculty_profile = FacultyProfileSerializer(required=False)
    retiree_profile = RetireeProfileSerializer(required=False)

    program_interests = serializers.ListField(child=serializers.CharField(), required=False)
    meta = VolunteerMetaSerializer(required=False)

    def create(self, validated_data):
        meta_data = validated_data.pop("meta", None)
        account_data = validated_data.pop("account")
        contact_data = validated_data.pop("contact")
        address_data = validated_data.pop("address")
        background_data = validated_data.pop("background")
        emergency_data = validated_data.pop("emergency_contact")

        student_data = validated_data.pop("student_profile", None)
        alumni_data = validated_data.pop("alumni_profile", None)
        staff_data = validated_data.pop("staff_profile", None)
        faculty_data = validated_data.pop("faculty_profile", None)
        retiree_data = validated_data.pop("retiree_profile", None)
        program_interests = validated_data.pop("program_interests", [])

        validated_data["volunteer_identifier"] = generate_volunteer_identifier()

        with transaction.atomic():
            volunteer = Volunteer.objects.create(**validated_data)

            # accounts
            password = account_data.pop("password", None)
            if password:
                account_data["password"] = make_password(password)
            VolunteerAccount.objects.create(volunteer=volunteer, **account_data)

            VolunteerContact.objects.create(volunteer=volunteer, **contact_data)
            VolunteerAddress.objects.create(volunteer=volunteer, **address_data)
            VolunteerBackground.objects.create(volunteer=volunteer, **background_data)
            EmergencyContact.objects.create(volunteer=volunteer, **emergency_data)

            # affiliation profile creation
            aff_type = validated_data.get("affiliation_type", "").lower()
            if aff_type == "student" and student_data:
                StudentProfile.objects.create(volunteer=volunteer, **student_data)
            elif aff_type == "alumni" and alumni_data:
                AlumniProfile.objects.create(volunteer=volunteer, **alumni_data)
            elif aff_type == "staff" and staff_data:
                StaffProfile.objects.create(volunteer=volunteer, **staff_data)
            elif aff_type == "faculty" and faculty_data:
                FacultyProfile.objects.create(volunteer=volunteer, **faculty_data)
            elif aff_type == "retiree" and retiree_data:
                RetireeProfile.objects.create(volunteer=volunteer, **retiree_data)

            # program interests
            for program_name in program_interests:
                if program_name:
                    ProgramInterest.objects.create(volunteer=volunteer, program_name=program_name)

            # meta
            if meta_data:
                VolunteerMeta.objects.create(volunteer=volunteer, **meta_data)

        return volunteer


# ---------------------------------------------------------------------
# VOLUNTEER SERIALIZER (GET / LIST / RETRIEVE) - Unified affiliation_data output
# ---------------------------------------------------------------------
class VolunteerSerializer(serializers.ModelSerializer):
    accounts = VolunteerAccountSerializer(many=True, read_only=True)
    contacts = VolunteerContactSerializer(many=True, read_only=True)
    addresses = VolunteerAddressSerializer(many=True, read_only=True)
    backgrounds = VolunteerBackgroundSerializer(many=True, read_only=True)
    emergency_contacts = EmergencyContactSerializer(many=True, read_only=True)
    program_interests = serializers.SerializerMethodField()
    meta = VolunteerMetaSerializer(read_only=True)

    # keep per-profile serializers available
    student_profile = StudentProfileSerializer(read_only=True)
    alumni_profile = AlumniProfileSerializer(read_only=True)
    staff_profile = StaffProfileSerializer(read_only=True)
    faculty_profile = FacultyProfileSerializer(read_only=True)
    retiree_profile = RetireeProfileSerializer(read_only=True)

    # NEW: produce unified affiliation_data array for frontend
    affiliation_data = serializers.SerializerMethodField()

    class Meta:
        model = Volunteer
        fields = [
            "volunteer_id",
            "volunteer_identifier",
            "first_name",
            "middle_name",
            "last_name",
            "nickname",
            "sex",
            "birthdate",
            "affiliation_type",
            "accounts",
            "contacts",
            "addresses",
            "backgrounds",
            "emergency_contacts",
            "program_interests",
            "meta",
            "student_profile",
            "alumni_profile",
            "staff_profile",
            "faculty_profile",
            "retiree_profile",
            "affiliation_data",
        ]

    def get_program_interests(self, obj):
        return [p.program_name for p in ProgramInterest.objects.filter(volunteer=obj)]

    def get_affiliation_data(self, obj):
        """
        Returns an array with one object for whichever affiliation profile exists,
        matching the shape your frontend expects:
        [{ "type": "ALUMNI", "constituent_unit": "...", "degree_program": "...", ... }]
        """
        output = []
        # student
        try:
            student = getattr(obj, "student_profile", None)
            if student:
                output.append({
                    "type": "STUDENT",
                    "degree_program": student.degree_program,
                    "year_level": student.year_level,
                    "college": student.college,
                })
        except Exception:
            pass

        # alumni
        try:
            alumni = getattr(obj, "alumni_profile", None)
            if alumni:
                output.append({
                    "type": "ALUMNI",
                    "constituent_unit": alumni.constituent_unit,
                    "degree_program": alumni.degree_program,
                    "year_graduated": alumni.year_graduated,
                })
        except Exception:
            pass

        # staff
        try:
            staff = getattr(obj, "staff_profile", None)
            if staff:
                output.append({
                    "type": "UP STAFF" if obj.affiliation_type and "staff" in obj.affiliation_type.lower() else "STAFF",
                    "office_department": staff.office_department,
                    "designation": staff.designation,
                })
        except Exception:
            pass

        # faculty
        try:
            faculty = getattr(obj, "faculty_profile", None)
            if faculty:
                output.append({
                    "type": "FACULTY",
                    "college": faculty.college,
                    "department": faculty.department,
                })
        except Exception:
            pass

        # retiree
        try:
            retiree = getattr(obj, "retiree_profile", None)
            if retiree:
                output.append({
                    "type": "RETIREE",
                    "designation_while_in_up": retiree.designation_while_in_up,
                    "office_college_department": retiree.office_college_department,
                })
        except Exception:
            pass

        return output

    # -------------------------------
    # Update method to handle nested updates (accounts, contact, address, background,
    # emergency_contact, affiliation profiles). This is defensive and will create missing related rows.
    # -------------------------------
    def update(self, instance, validated_data):
        # validated_data may be flat or contain nested keys; support both shapes
        # Update top-level volunteer fields
        volunteer_fields = [
            "first_name",
            "middle_name",
            "last_name",
            "nickname",
            "sex",
            "birthdate",
            "affiliation_type",
        ]
        for f in volunteer_fields:
            if f in validated_data:
                setattr(instance, f, validated_data.get(f))
        instance.save()

        # Handle account update (email/password)
        account_data = validated_data.get("account")
        if account_data:
            acct = instance.accounts.first()
            if acct:
                if "email" in account_data:
                    acct.email = account_data["email"]
                if "password" in account_data and account_data["password"]:
                    acct.password = make_password(account_data["password"])
                acct.save()
            else:
                # create
                pwd = account_data.pop("password", None)
                if pwd:
                    account_data["password"] = make_password(pwd)
                VolunteerAccount.objects.create(volunteer=instance, **account_data)

        # contact
        contact_data = validated_data.get("contact")
        if contact_data is not None:
            contact = instance.contacts.first()
            if contact:
                for k, v in contact_data.items():
                    setattr(contact, k, v)
                contact.save()
            else:
                VolunteerContact.objects.create(volunteer=instance, **contact_data)

        # address
        address_data = validated_data.get("address")
        if address_data is not None:
            addr = instance.addresses.first()
            if addr:
                for k, v in address_data.items():
                    setattr(addr, k, v)
                addr.save()
            else:
                VolunteerAddress.objects.create(volunteer=instance, **address_data)

        # background
        background_data = validated_data.get("background")
        if background_data is not None:
            bg = instance.backgrounds.first()
            if bg:
                for k, v in background_data.items():
                    setattr(bg, k, v)
                bg.save()
            else:
                VolunteerBackground.objects.create(volunteer=instance, **background_data)

        # emergency_contact
        emergency_data = validated_data.get("emergency_contact")
        if emergency_data is not None:
            em = instance.emergency_contacts.first()
            if em:
                for k, v in emergency_data.items():
                    setattr(em, k, v)
                em.save()
            else:
                EmergencyContact.objects.create(volunteer=instance, **emergency_data)

        # affiliation sub-profiles (create or update)
        student_data = validated_data.get("student_profile")
        if student_data is not None:
            sp = getattr(instance, "student_profile", None)
            if sp:
                for k, v in student_data.items():
                    setattr(sp, k, v)
                sp.save()
            else:
                StudentProfile.objects.create(volunteer=instance, **student_data)

        alumni_data = validated_data.get("alumni_profile")
        if alumni_data is not None:
            ap = getattr(instance, "alumni_profile", None)
            if ap:
                for k, v in alumni_data.items():
                    setattr(ap, k, v)
                ap.save()
            else:
                AlumniProfile.objects.create(volunteer=instance, **alumni_data)

        staff_data = validated_data.get("staff_profile")
        if staff_data is not None:
            spf = getattr(instance, "staff_profile", None)
            if spf:
                for k, v in staff_data.items():
                    setattr(spf, k, v)
                spf.save()
            else:
                StaffProfile.objects.create(volunteer=instance, **staff_data)

        faculty_data = validated_data.get("faculty_profile")
        if faculty_data is not None:
            fpf = getattr(instance, "faculty_profile", None)
            if fpf:
                for k, v in faculty_data.items():
                    setattr(fpf, k, v)
                fpf.save()
            else:
                FacultyProfile.objects.create(volunteer=instance, **faculty_data)

        retiree_data = validated_data.get("retiree_profile")
        if retiree_data is not None:
            rpf = getattr(instance, "retiree_profile", None)
            if rpf:
                for k, v in retiree_data.items():
                    setattr(rpf, k, v)
                rpf.save()
            else:
                RetireeProfile.objects.create(volunteer=instance, **retiree_data)

        # program_interests: replace existing with provided list (if present)
        program_interests = validated_data.get("program_interests")
        if program_interests is not None:
            # remove existing then add new ones
            ProgramInterest.objects.filter(volunteer=instance).delete()
            for name in program_interests:
                if name:
                    ProgramInterest.objects.create(volunteer=instance, program_name=name)

        # meta update
        meta_data = validated_data.get("meta")
        if meta_data is not None:
            meta_inst = getattr(instance, "volunteermeta", None)
            if meta_inst:
                for k, v in meta_data.items():
                    setattr(meta_inst, k, v)
                meta_inst.save()
            else:
                VolunteerMeta.objects.create(volunteer=instance, **meta_data)

        return instance


# ---------------------------------------------------------------------
# VOLUNTEER EVENT SERIALIZERS
# ---------------------------------------------------------------------
class VolunteerEventBaseSerializer(serializers.ModelSerializer):
    volunteer_name = serializers.SerializerMethodField()
    event_name = serializers.SerializerMethodField()

    class Meta:
        model = VolunteerEvent
        fields = [
            "id",
            "volunteer",
            "volunteer_name",
            "event",
            "event_name",
            "availability_time",
            "availability_orientation",
            "status",
            "hours_rendered",
            "signup_date",
        ]

    def get_volunteer_name(self, obj):
        return f"{obj.volunteer.first_name} {obj.volunteer.last_name}"

    def get_event_name(self, obj):
        return obj.event.event_name


class VolunteerEventJoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerEvent
        fields = ["event", "availability_time", "availability_orientation"]

    def validate(self, data):
        volunteer = self.context["volunteer"]
        event = data["event"]

        # Prevent double join
        if VolunteerEvent.objects.filter(volunteer=volunteer, event=event).exists():
            raise serializers.ValidationError("You have already joined this event")

        # Check if event is full
        total = VolunteerEvent.objects.filter(
            event=event, status__in=["Joined", "Completed"]
        ).count()
        if total >= event.max_participants:
            raise serializers.ValidationError("This event is already full")

        return data

    def create(self, validated_data):
        validated_data["volunteer"] = self.context["volunteer"]
        validated_data["status"] = "Joined"
        return super().create(validated_data)


class EventVolunteersSerializer(serializers.ModelSerializer):
    volunteer_info = serializers.SerializerMethodField()

    class Meta:
        model = VolunteerEvent
        fields = [
            "volunteer",
            "volunteer_info",
            "hours_rendered",
            "status",
            "availability_time",
            "availability_orientation",
            "signup_date",
        ]

    def get_volunteer_info(self, obj):
        v = obj.volunteer
        return {
            "volunteer_id": v.volunteer_id,
            "name": f"{v.first_name} {v.last_name}",
            "email": v.accounts.first().email if v.accounts.exists() else None,
            "mobile": v.contacts.first().mobile_number if v.contacts.exists() else None,
        }
