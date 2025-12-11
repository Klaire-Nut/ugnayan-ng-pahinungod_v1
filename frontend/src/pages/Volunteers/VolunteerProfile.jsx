import React, { useEffect, useState } from "react";
import { volunteerAPI } from "../../services/volunteerApi";
import "../../styles/VolunteerProfile.css";
import ProfileForm from "../../components/ProfileForm";
import VolunteerSidebar from "../../components/VolunteerSidebar";

export default function VolunteerProfile() {
  const [userData, setUserData] = useState(null);
  const [tempData, setTempData] = useState(null);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const flattenProfile = (resp) => {
    if (!resp) return null;
    const volunteer = resp.volunteer || {};
    return {
      volunteer_id: volunteer.volunteer_id,
      volunteer_identifier: volunteer.volunteer_identifier,
      first_name: volunteer.first_name,
      middle_name: volunteer.middle_name,
      last_name: volunteer.last_name,
      nickname: volunteer.nickname,
      sex: volunteer.sex,
      birthdate: volunteer.birthdate,
      affiliation_type: volunteer.affiliation_type,
      email: volunteer.email || volunteer.email,
      mobile_number: resp.contact?.mobile_number,
      facebook_link: resp.contact?.facebook_link,
      street_address: resp.address?.street_address,
      province: resp.address?.province,
      region: resp.address?.region,
      org_affiliation: resp.background?.org_affiliation,
      hobbies_interests: resp.background?.hobbies_interests,
      emergency_contact: resp.emergency_contact || {},
      affiliation_data: resp.affiliation_data || [],
      program_interests: resp.program_interests || [],
      profile_picture: resp.profile_picture || "",
    };
  };

  useEffect(() => {
    const loadProfile = async () => {
      setLoading(true);
      try {
        const response = await volunteerAPI.getProfile();
        if (!response.success) throw new Error(response.error || "Failed to load profile");
<<<<<<< Updated upstream

        setUserData(response.data);
        setTempData(response.data);
=======
        const flat = flattenProfile(response.data);
        setUserData(flat);
        setTempData(flat);
>>>>>>> Stashed changes
        setError("");
      } catch (err) {
        console.error(err);
        setError("Failed to load profile");
      } finally {
        setLoading(false);
      }
    };
    loadProfile();
  }, []);

<<<<<<< Updated upstream
  // SIMPLE version — because ProfileForm already returns correct nested objects
  const handleChange = (key, value) => {
    setTempData((prev) => ({
      ...prev,
      [key]: value
    }));
=======
  const handleChange = (key, value, type = "main", index = null) => {
    setTempData((prev) => {
      if (!prev) return prev;
      if (type === "emergency") {
        return { ...prev, emergency_contact: { ...prev.emergency_contact, [key]: value } };
      }
      if (type === "affiliation" && index !== null) {
        const updatedAffiliations = [...(prev.affiliation_data || [])];
        updatedAffiliations[index] = { ...(updatedAffiliations[index] || {}), [key]: value };
        return { ...prev, affiliation_data: updatedAffiliations };
      }
      return { ...prev, [key]: value };
    });
  };

  const buildUpdatePayload = (flat) => {
    if (!flat) return {};
    const affType = (flat.affiliation_type || flat.affiliation_data?.[0]?.type || "").toLowerCase();
    const payload = {
      volunteer: {
        first_name: flat.first_name || "",
        middle_name: flat.middle_name || "",
        last_name: flat.last_name || "",
        nickname: flat.nickname || "",
        sex: flat.sex || "",
        birthdate: flat.birthdate || null,
        affiliation_type: affType,
      },
      account: { email: flat.email || "" },
      contact: {
        mobile_number: flat.mobile_number || "",
        facebook_link: flat.facebook_link || "",
      },
      address: {
        street_address: flat.street_address || "",
        province: flat.province || "",
        region: flat.region || "",
      },
      background: {
        org_affiliation: flat.org_affiliation || "",
        hobbies_interests: flat.hobbies_interests || "",
      },
      emergency_contact: flat.emergency_contact || {},
      affiliation_data: Array.isArray(flat.affiliation_data) ? flat.affiliation_data : [],
      program_interests: Array.isArray(flat.program_interests) ? flat.program_interests : [],
    };
    return payload;
>>>>>>> Stashed changes
  };

  const handleSave = async () => {
    try {
      const payload = buildUpdatePayload(tempData);
      const response = await volunteerAPI.updateProfile(payload);
      if (!response.success) {
        alert(response.error || "Failed to update profile.");
        return;
      }
      const refreshed = await volunteerAPI.getProfile();
      const flat = flattenProfile(refreshed.data);
      setUserData(flat);
      setTempData(flat);
      setIsEditOpen(false);
      alert("Profile updated successfully!");
    } catch (err) {
      console.error(err);
      alert("Failed to update profile.");
    }
  };

  if (loading) return <div className="vol-profile-page">Loading profile...</div>;
  if (error) return <div className="vol-profile-page error-message">{error}</div>;
  if (!userData) return <div className="vol-profile-page">No profile data found.</div>;

  return (
    <div className="vol-profile-page">
      <VolunteerSidebar />
      <div className="vol-profile-main">
        <div className="profile-header">
          <h1 className="profile-title">PROFILE</h1>
          <button className="edit-btn" onClick={() => setIsEditOpen(true)}>Edit</button>
        </div>
        <div className="profile-grid">
          <div className="profile-left">
            <img
              src={userData.profile_picture || "/default-profile.png"}
              alt="Profile"
              className="profile-photo"
            />
<<<<<<< Updated upstream
            <div className="volunteer-id">ID: {userData.volunteer_id}</div>
=======
            <div className="volunteer-id">{userData.volunteer_identifier}</div>
>>>>>>> Stashed changes
          </div>
          <div className="profile-right">
            <ProfileForm data={userData} editable={false} onChange={handleChange} />
          </div>
        </div>
        {isEditOpen && (
          <div className="edit-modal">
            <div className="edit-modal-content">
              <button className="close-btn" onClick={() => setIsEditOpen(false)}>&times;</button>
              <h2>Edit Profile</h2>
              <div className="modal-scroll">
                <ProfileForm data={tempData} editable={true} onChange={handleChange} />
              </div>
              <div className="modal-buttons">
                <button className="cancel-btn" onClick={() => setIsEditOpen(false)}>Cancel</button>
                <button className="save-btn" onClick={handleSave}>Save</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
