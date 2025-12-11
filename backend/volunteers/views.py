# backend/volunteers/views.py

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
<<<<<<< Updated upstream
from rest_framework import status
=======
from rest_framework.authentication import TokenAuthentication
>>>>>>> Stashed changes

from django.contrib.auth.hashers import check_password, make_password
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import login, logout

from django.http import JsonResponse
from django.db import transaction
import json

from core.models import (
    Volunteer,
    VolunteerContact,
    VolunteerAddress,
    VolunteerBackground,
    EmergencyContact,
    VolunteerAccount,
    VolunteerEvent,
    StudentProfile,
    AlumniProfile,
    StaffProfile,
    FacultyProfile,
<<<<<<< Updated upstream
    RetireeProfile
=======
    RetireeProfile,
    ProgramInterest,
>>>>>>> Stashed changes
)

from volunteers.serializers import VolunteerSerializer
from core.utils import generate_volunteer_identifier

from rest_framework.authtoken.models import Token
<<<<<<< Updated upstream
from rest_framework.authentication import TokenAuthentication
=======
>>>>>>> Stashed changes


# ================================================================
<<<<<<< Updated upstream
#  🔐 VOLUNTEER LOGIN (TOKEN-BASED)
=======
# VOLUNTEER LOGIN (TOKEN-BASED)
>>>>>>> Stashed changes
# ================================================================
@csrf_exempt
def volunteer_login(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=400)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return JsonResponse({"error": "Email and password required"}, status=400)

    try:
        account = VolunteerAccount.objects.select_related("volunteer").get(email=email)
    except VolunteerAccount.DoesNotExist:
        return JsonResponse({"error": "Invalid email or password"}, status=400)

    if not check_password(password, account.password):
        return JsonResponse({"error": "Invalid email or password"}, status=400)

    volunteer = account.volunteer

<<<<<<< Updated upstream
    # Use VolunteerAccount directly for token
    token, _ = Token.objects.get_or_create(user=account)
=======
    # Ensure Django auth user exists (used for TokenAuthentication)
    user, created = User.objects.get_or_create(email=email)
    if created or not user.password:
        user.password = make_password(password)

    if hasattr(user, "is_volunteer"):
        user.is_volunteer = True
    user.save()

    user.backend = "django.contrib.auth.backends.ModelBackend"
    login(request, user)

    token, _ = Token.objects.get_or_create(user=user)
>>>>>>> Stashed changes

    return JsonResponse({
        "success": True,
        "message": "Login successful",
        "token": token.key,
        "volunteer": VolunteerSerializer(volunteer).data,
    })

# ================================================================
<<<<<<< Updated upstream
#  🚪 LOGOUT
=======
# LOGOUT
>>>>>>> Stashed changes
# ================================================================
@csrf_exempt
def volunteer_logout(request):
    logout(request)
    return JsonResponse({"message": "Logout successful"})


# ================================================================
<<<<<<< Updated upstream
#  👤 VOLUNTEER PROFILE VIEW (TOKEN)
=======
# VOLUNTEER PROFILE VIEW (TOKEN)
>>>>>>> Stashed changes
# ================================================================
@method_decorator(csrf_exempt, name='dispatch')
class VolunteerProfileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            account = request.user  # Token-authenticated user is VolunteerAccount
        except VolunteerAccount.DoesNotExist:
            return Response({"error": "Invalid token"}, status=403)

        volunteer = account.volunteer

        contact = getattr(volunteer, "contacts", None)
        contact = contact.first() if contact else None

<<<<<<< Updated upstream
        return Response({
            "volunteer": VolunteerSerializer(volunteer).data,
=======
        address = getattr(volunteer, "addresses", None)
        address = address.first() if address else None

        background = getattr(volunteer, "backgrounds", None)
        background = background.first() if background else None

        emergency = getattr(volunteer, "emergency_contacts", None)
        emergency = emergency.first() if emergency else None

        # ===== AFFILIATION DATA =====
        aff = (volunteer.affiliation_type or "").lower()
        affiliation_data = []

        if aff == "student" and hasattr(volunteer, "student_profile"):
            p = getattr(volunteer, "student_profile", None)
            if p:
                affiliation_data.append({
                    "type": "STUDENT",
                    "degree_program": p.degree_program,
                    "year_level": p.year_level,
                    "college": p.college,
                    "department": p.department,
                })
        elif aff == "alumni" and hasattr(volunteer, "alumni_profile"):
            p = getattr(volunteer, "alumni_profile", None)
            if p:
                affiliation_data.append({
                    "type": "ALUMNI",
                    "constituent_unit": p.constituent_unit,
                    "degree_program": p.degree_program,
                    "year_graduated": p.year_graduated,
                })
        elif aff in ("up staff", "staff") and hasattr(volunteer, "staff_profile"):
            p = getattr(volunteer, "staff_profile", None)
            if p:
                affiliation_data.append({
                    "type": "UP STAFF",
                    "office_department": p.office_department,
                    "designation": p.designation,
                })
        elif aff == "faculty" and hasattr(volunteer, "faculty_profile"):
            p = getattr(volunteer, "faculty_profile", None)
            if p:
                affiliation_data.append({
                    "type": "FACULTY",
                    "college": p.college,
                    "department": p.department,
                })
        elif aff == "retiree" and hasattr(volunteer, "retiree_profile"):
            p = getattr(volunteer, "retiree_profile", None)
            if p:
                affiliation_data.append({
                    "type": "RETIREE",
                    "designation_while_in_up": p.designation_while_in_up,
                    "office_college_department": p.office_college_department,
                })

        # Program interests
        program_interests_qs = ProgramInterest.objects.filter(volunteer=volunteer)
        program_interests = [pi.program_name for pi in program_interests_qs]

        return Response({
            "volunteer": {
                "volunteer_id": volunteer.volunteer_id,
                "volunteer_identifier": getattr(volunteer, "volunteer_identifier", None),
                "first_name": volunteer.first_name,
                "middle_name": volunteer.middle_name,
                "last_name": volunteer.last_name,
                "nickname": volunteer.nickname,
                "sex": volunteer.sex,
                "birthdate": volunteer.birthdate,
                "affiliation_type": volunteer.affiliation_type,
                "email": account.email,
            },
>>>>>>> Stashed changes
            "contact": {
                "mobile_number": contact.mobile_number if contact else None,
                "facebook_link": contact.facebook_link if contact else None,
            },
            "address": {
                "street_address": address.street_address if address else None,
                "province": address.province if address else None,
                "region": address.region if address else None,
            },
            "background": {
                "occupation": background.occupation if background else None,
                "org_affiliation": background.org_affiliation if background else None,
                "hobbies_interests": background.hobbies_interests if background else None,
            },
            "emergency_contact": {
                "name": emergency.name if emergency else None,
                "relationship": emergency.relationship if emergency else None,
                "contact_number": emergency.contact_number if emergency else None,
                "address": emergency.address if emergency else None,
<<<<<<< Updated upstream
            }
        })

    def patch(self, request):
        account = request.user
        volunteer = account.volunteer
        data = request.data

        try:
            with transaction.atomic():
                # BASIC INFO
                for field in ["first_name", "middle_name", "last_name",
                              "nickname", "sex", "birthdate"]:
                    if field in data:
                        setattr(volunteer, field, data[field])
                volunteer.save()

                # CONTACT INFO
                contact, _ = VolunteerContact.objects.get_or_create(volunteer=volunteer)
                contact.mobile_number = data.get("mobile_number", contact.mobile_number)
                contact.facebook_link = data.get("facebook_link", contact.facebook_link)
                contact.save()

                # ADDRESS
                address, _ = VolunteerAddress.objects.get_or_create(volunteer=volunteer)
                address.street_address = data.get("street_address", address.street_address)
                address.province = data.get("province", address.province)
                address.region = data.get("region", address.region)
                address.save()

            return Response({"success": True})

        except Exception as e:
            return Response({"error": str(e)}, status=400)


# ================================================================
#  📜 EVENT HISTORY
=======
            },
            "affiliation_data": affiliation_data,
            "program_interests": program_interests,
        })


# ================================================================
# EVENT HISTORY
>>>>>>> Stashed changes
# ================================================================
@method_decorator(csrf_exempt, name='dispatch')
class VolunteerHistoryView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        account = request.user
        volunteer = account.volunteer

        queryset = VolunteerEvent.objects.filter(
            volunteer=volunteer
        ).select_related("event").order_by("event__date_start")

        history = [
            {
                "event_id": ve.event.event_id,
                "event_name": ve.event.event_name,
                "date": ve.event.date_start,
                "time_in": ve.event.date_start,
                "time_out": ve.event.date_end,
                "hours_rendered": ve.hours_rendered,
                "status": ve.status,
            }
            for ve in queryset
        ]

        return Response({"history": history})


# ================================================================
<<<<<<< Updated upstream
#  🔐 CHANGE PASSWORD
=======
# CHANGE PASSWORD
>>>>>>> Stashed changes
# ================================================================
@method_decorator(csrf_exempt, name='dispatch')
class ChangePasswordView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        account = request.user

        current = request.data.get("current_password")
        new = request.data.get("new_password")
        confirm = request.data.get("confirm_password")

        if not current or not new or not confirm:
            return Response({"error": "All fields are required"}, status=400)

        if not check_password(current, account.password):
            return Response({"error": "Incorrect current password"}, status=400)

        if new != confirm:
            return Response({"error": "Passwords do not match"}, status=400)

        account.password = make_password(new)
        account.save()

        return Response({"message": "Password updated successfully"})


# ================================================================
<<<<<<< Updated upstream
#  📝 REGISTER VOLUNTEER
=======
# REGISTER VOLUNTEER
>>>>>>> Stashed changes
# ================================================================
@method_decorator(csrf_exempt, name='dispatch')
class RegisterVolunteer(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError as DjangoValidationError

        errors = {}

        try:
            with transaction.atomic():
                # Extract data blocks
                account_data = request.data.get("account", {})
                volunteer_data = request.data.get("volunteer", {})
                contact_data = request.data.get("contact", {})
                address_data = request.data.get("address", {})
                background_data = request.data.get("background", {})
                emergency_data = request.data.get("emergency_contact", {})
                affiliation_data = request.data.get("affiliation_data", {})
                program_interests = request.data.get("program_interests", [])

                email = account_data.get("email", "").strip()
                password = account_data.get("password", "")

                # BASIC VALIDATION
                if not email:
                    errors["email"] = "Email is required"
                if not password:
                    errors["password"] = "Password is required"
                else:
                    try:
                        validate_password(password)
                    except DjangoValidationError as e:
                        errors["password"] = list(e.messages)

                if email and VolunteerAccount.objects.filter(email=email).exists():
                    errors["email"] = "This email is already registered"

                if not volunteer_data.get("first_name"):
                    errors["first_name"] = "First name is required"
                if not volunteer_data.get("last_name"):
                    errors["last_name"] = "Last name is required"
                if not volunteer_data.get("affiliation_type"):
                    errors["affiliation_type"] = "Affiliation type is required"

                if errors:
                    return Response({"errors": errors}, status=400)

                # Create volunteer
                volunteer = Volunteer.objects.create(
                    first_name=volunteer_data.get("first_name", "").strip(),
                    middle_name=volunteer_data.get("middle_name", "").strip(),
                    last_name=volunteer_data.get("last_name", "").strip(),
                    nickname=volunteer_data.get("nickname", "").strip(),
                    sex=volunteer_data.get("sex", ""),
                    birthdate=volunteer_data.get("birthdate"),
<<<<<<< Updated upstream
                    affiliation_type=volunteer_data.get("affiliation_type", "").upper(),
=======
                    affiliation_type=volunteer_data.get("affiliation_type", "").lower(),
>>>>>>> Stashed changes
                    volunteer_identifier=generate_volunteer_identifier(),
                )

                # Create account
                VolunteerAccount.objects.create(
                    volunteer=volunteer,
                    email=email,
                    password=make_password(password)
                )

                # Contact
                if contact_data:
                    VolunteerContact.objects.create(
                        volunteer=volunteer,
                        mobile_number=contact_data.get("mobile_number", ""),
                        facebook_link=contact_data.get("facebook_link", "")
                    )

                # Address
                if address_data:
                    VolunteerAddress.objects.create(
                        volunteer=volunteer,
                        street_address=address_data.get("street_address", ""),
                        province=address_data.get("province", ""),
                        region=address_data.get("region", "")
                    )

                # Background
                if background_data:
                    VolunteerBackground.objects.create(
                        volunteer=volunteer,
                        occupation=background_data.get("occupation", ""),
                        org_affiliation=background_data.get("org_affiliation", ""),
                        hobbies_interests=background_data.get("hobbies_interests", "")
                    )

                # Emergency
                if emergency_data:
                    EmergencyContact.objects.create(
                        volunteer=volunteer,
                        name=emergency_data.get("name", ""),
                        relationship=emergency_data.get("relationship", ""),
                        contact_number=emergency_data.get("contact_number", ""),
                        address=emergency_data.get("address", "")
                    )

<<<<<<< Updated upstream
                # Affiliation-specific
                aff = volunteer.affiliation_type

                if aff == "STUDENT":
=======
                # Affiliation profiles
                aff = volunteer.affiliation_type.lower()
                if aff == "student":
>>>>>>> Stashed changes
                    StudentProfile.objects.create(
                        volunteer=volunteer,
                        degree_program=affiliation_data.get("degree_program", ""),
                        year_level=affiliation_data.get("year_level", ""),
                        college=affiliation_data.get("college", ""),
<<<<<<< Updated upstream
                        department=affiliation_data.get("department", ""),
                    )
                elif aff == "ALUMNI":
=======
                        department=affiliation_data.get("department", "")
                    )
                elif aff == "alumni":
>>>>>>> Stashed changes
                    AlumniProfile.objects.create(
                        volunteer=volunteer,
                        constituent_unit=affiliation_data.get("constituent_unit", ""),
                        degree_program=affiliation_data.get("degree_program", ""),
<<<<<<< Updated upstream
                        year_graduated=affiliation_data.get("year_graduated", ""),
                    )
                elif aff == "UP STAFF":
                    StaffProfile.objects.create(
                        volunteer=volunteer,
                        office_department=affiliation_data.get("office_department", ""),
                        designation=affiliation_data.get("designation", ""),
                    )
                elif aff == "FACULTY":
                    FacultyProfile.objects.create(
                        volunteer=volunteer,
                        college=affiliation_data.get("college", ""),
                        department=affiliation_data.get("department", ""),
                    )
                elif aff == "RETIREE":
                    RetireeProfile.objects.create(
                        volunteer=volunteer,
                        designation_while_in_up=affiliation_data.get("designation_while_in_up", ""),
                        office_college_department=affiliation_data.get("office_college_department", ""),
                    )

                return Response({
                    "message": "Registration successful! You may now log in.",
                    "volunteer_id": volunteer.volunteer_id
                }, status=201)

        except Exception as e:
            print("REGISTER ERROR:", traceback.format_exc())
=======
                        year_graduated=affiliation_data.get("year_graduated", "")
                    )
                elif aff in ("up staff", "staff"):
                    StaffProfile.objects.create(
                        volunteer=volunteer,
                        office_department=affiliation_data.get("office_department", ""),
                        designation=affiliation_data.get("designation", "")
                    )
                elif aff == "faculty":
                    FacultyProfile.objects.create(
                        volunteer=volunteer,
                        college=affiliation_data.get("college", ""),
                        department=affiliation_data.get("department", "")
                    )
                elif aff == "retiree":
                    RetireeProfile.objects.create(
                        volunteer=volunteer,
                        designation_while_in_up=affiliation_data.get("designation_while_in_up", ""),
                        office_college_department=affiliation_data.get("office_college_department", "")
                    )

                # Program interests
                for name in program_interests:
                    if name:
                        ProgramInterest.objects.create(volunteer=volunteer, program_name=name)

                return Response({"message": "Volunteer registered successfully", "volunteer_id": volunteer.volunteer_id})

        except Exception as e:
>>>>>>> Stashed changes
            return Response({"error": str(e)}, status=500)
