from django.db import transaction
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from core.models import (
    Volunteer,
    ProgramInterest,
    VolunteerAccount,
    VolunteerContact,
    VolunteerAddress,
    VolunteerBackground,
    EmergencyContact,
    VolunteerMeta,
    StudentProfile,
    AlumniProfile,
    StaffProfile,
    FacultyProfile,
    RetireeProfile,
    VolunteerEvent, 
)

# Nested serializers
class VolunteerAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerAccount
        fields = ["email"]

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
        fields = ["org_affiliation", "hobbies_interests"]

class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = ["name", "relationship", "contact_number", "address"]

class VolunteerMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerMeta
        fields = "__all__"

class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = "__all__"

class AlumniProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlumniProfile
        fields = "__all__"

class StaffProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffProfile
        fields = "__all__"

class FacultyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacultyProfile
        fields = "__all__"

class RetireeProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RetireeProfile
        fields = "__all__"


class VolunteerSerializer(serializers.ModelSerializer):
    # readonly nested
    accounts = VolunteerAccountSerializer(many=True, read_only=True)
    contacts = VolunteerContactSerializer(many=True, read_only=True)
    addresses = VolunteerAddressSerializer(many=True, read_only=True)
    backgrounds = VolunteerBackgroundSerializer(many=True, read_only=True)
    emergency_contacts = EmergencyContactSerializer(many=True, read_only=True)
    program_interests = serializers.SerializerMethodField()
    meta = VolunteerMetaSerializer(read_only=True)

    # profile serializers (read-only)
    student_profile = StudentProfileSerializer(read_only=True)
    alumni_profile = AlumniProfileSerializer(read_only=True)
    staff_profile = StaffProfileSerializer(read_only=True)
    faculty_profile = FacultyProfileSerializer(read_only=True)
    retiree_profile = RetireeProfileSerializer(read_only=True)

    # frontend-friendly affiliation_data
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
        # Always returns a list with one dict, independent of which profile exists
        profile_list = [
            ("student_profile", StudentProfileSerializer),
            ("alumni_profile", AlumniProfileSerializer),
            ("staff_profile", StaffProfileSerializer),
            ("faculty_profile", FacultyProfileSerializer),
            ("retiree_profile", RetireeProfileSerializer),
        ]
        for attr, serializer_cls in profile_list:
            profile = getattr(obj, attr, None)
            if profile:
                data = serializer_cls(profile).data
                data["type"] = attr.replace("_profile", "").upper()
                return [data]
        # No profile exists
        return [{"type": obj.affiliation_type.upper()}]

    @transaction.atomic
    def update(self, instance, validated_data):
        # -----------------------------
        # 1️⃣ Update volunteer top-level fields
        # -----------------------------
        vol_data = validated_data.pop("volunteer", {})
        top_fields = {k: validated_data.pop(k) for k in list(validated_data.keys())
                      if k in {"first_name", "middle_name", "last_name", "nickname", "sex", "birthdate", "affiliation_type"}}
        combined_vol = {**top_fields, **vol_data}
        for k, v in combined_vol.items():
            if v is not None:
                setattr(instance, k, v)
        instance.save()

        # -----------------------------
        # 2️⃣ Update accounts
        # -----------------------------
        account_data = validated_data.pop("account", None)
        if account_data:
            acct = instance.accounts.first()
            if acct:
                if "email" in account_data:
                    acct.email = account_data["email"]
                if "password" in account_data:
                    acct.password = make_password(account_data["password"])
                acct.save()
            else:
                pwd = account_data.pop("password", None)
                if pwd:
                    account_data["password"] = make_password(pwd)
                VolunteerAccount.objects.create(volunteer=instance, **account_data)

        # -----------------------------
        # 3️⃣ Update contacts, addresses, backgrounds, emergency_contacts
        # -----------------------------
        for key, model_cls in [
            ("contact", VolunteerContact),
            ("address", VolunteerAddress),
            ("background", VolunteerBackground),
            ("emergency_contact", EmergencyContact),
        ]:
            data = validated_data.pop(key, None)
            if data:
                inst = getattr(instance, f"{key}s").first()
                if inst:
                    for k, v in data.items():
                        setattr(inst, k, v)
                    inst.save()
                else:
                    model_cls.objects.create(volunteer=instance, **data)

        # -----------------------------
        # 4️⃣ Update affiliation profiles
        # -----------------------------
        for key, model_cls in [
            ("student_profile", StudentProfile),
            ("alumni_profile", AlumniProfile),
            ("staff_profile", StaffProfile),
            ("faculty_profile", FacultyProfile),
            ("retiree_profile", RetireeProfile),
        ]:
            data = validated_data.pop(key, None)
            if data:
                inst = getattr(instance, key, None)
                if inst:
                    for k, v in data.items():
                        setattr(inst, k, v)
                    inst.save()
                else:
                    model_cls.objects.create(volunteer=instance, **data)

        # -----------------------------
        # 5️⃣ Update affiliation_data array
        # -----------------------------
        aff_array = validated_data.pop("affiliation_data", None)
        if aff_array:
            first = aff_array[0] if isinstance(aff_array, (list, tuple)) and len(aff_array) else None
            if first and isinstance(first, dict):
                atype = first.get("type", "").lower()
                profile_map = {
                    "student": StudentProfile,
                    "alumni": AlumniProfile,
                    "staff": StaffProfile,
                    "faculty": FacultyProfile,
                    "retiree": RetireeProfile,
                }
                model_cls = profile_map.get(atype)
                if model_cls:
                    model_cls.objects.update_or_create(
                        volunteer=instance,
                        defaults={k: v for k, v in first.items() if k != "type"}
                    )

        # -----------------------------
        # 6️⃣ Update program interests
        # -----------------------------
        programs = validated_data.pop("program_interests", None)
        if programs is not None:
            ProgramInterest.objects.filter(volunteer=instance).delete()
            for name in programs:
                if name:
                    ProgramInterest.objects.create(volunteer=instance, program_name=name)

        # -----------------------------
        # 7️⃣ Update meta
        # -----------------------------
        meta_data = validated_data.pop("meta", None)
        if meta_data:
            meta_inst = getattr(instance, "meta", None)
            if meta_inst:
                for k, v in meta_data.items():
                    setattr(meta_inst, k, v)
                meta_inst.save()
            else:
                VolunteerMeta.objects.create(volunteer=instance, **meta_data)

        # -----------------------------
        # 8️⃣ Defensive top-level scalar fields
        # -----------------------------
        for k, v in validated_data.items():
            if hasattr(instance, k) and v is not None:
                setattr(instance, k, v)
        instance.save()

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
        if VolunteerEvent.objects.filter(volunteer=volunteer, event=event).exists():
            raise serializers.ValidationError("You have already joined this event")
        # max_participants validation can be added here if available
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
