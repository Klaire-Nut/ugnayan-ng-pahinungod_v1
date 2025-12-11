import React from "react";
import "../styles/VolunteerProfile.css";

export default function ProfileForm({ data, editable = false, onChange }) {
  if (!data) return null;

<<<<<<< Updated upstream
  // Capitalize field labels
  const label = (str) =>
    str.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

  // Affiliation-based fields (based on your Django `affiliation_data`)
  const affiliationFields = {
    STUDENT: ["degree_program", "year_level", "college", "department"],
    ALUMNI: ["constituent_unit", "degree_program", "year_graduated"],
    "UP STAFF": ["office_department", "designation"],
    FACULTY: ["college", "department"],
    RETIREE: ["designation_while_in_up", "office_college_department"],
  };
=======
  // Capitalize and format field labels
  const label = (str) =>
    str.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
>>>>>>> Stashed changes

  // Define main sections
  const sections = {
    "Personal Information": [
      "first_name",
      "middle_name",
      "last_name",
      "nickname",
      "sex",
      "birthdate",
<<<<<<< Updated upstream
    ],

    "Contact Information": ["email", "mobile_number", "facebook_link"],

    "Current Address": ["street_address", "province", "region"],

    "Background Information": [
      "occupation",
      "org_affiliation",
      "hobbies_interests",
    ],

    "Emergency Contact": data.emergency_contact
      ? ["name", "relationship", "contact_number", "address"]
      : [],

    "Affiliation Information":
      affiliationFields[data.affiliation_type] || [],
  };

  // Helper to read nested emergency_contact & affiliation_data
  const getValue = (field) => {
    if (!data) return "";

    if (sections["Emergency Contact"].includes(field)) {
      return data.emergency_contact?.[field] ?? "";
    }

    if (sections["Affiliation Information"].includes(field)) {
      return data.affiliation_data?.[field] ?? "";
    }

    return data[field] ?? "";
  };

  // Helper for saving nested values
  const saveValue = (field, value) => {
    if (sections["Emergency Contact"].includes(field)) {
      onChange("emergency_contact", {
        ...data.emergency_contact,
        [field]: value,
      });
      return;
    }

    if (sections["Affiliation Information"].includes(field)) {
      onChange("affiliation_data", {
        ...data.affiliation_data,
        [field]: value,
      });
=======
      "email",
    ],
    "Contact Information": ["mobile_number", "facebook_link"],
    "Current Address": ["street_address", "province", "region"],
    "Background Information": [ "org_affiliation", "hobbies_interests"],
    "Emergency Contact": data.emergency_contact
      ? ["name", "relationship", "contact_number", "address"]
      : [],
  };

  // Program interests options (can expand)
  const allProgramOptions = [
    "AFFIRMATIVE ACTION PROGRAM",
    "TEACHER DEVELOPMENT PROGRAM",
    "DISASTER RISK REDUCTION RELATED PROGRAM",
    "UGNAYAN NG PAHINUNGOD ONLINE PROGRAM",
    "TUTORIAL SERVICES PROGRAM",
    "PROGRAMS UNDER THE UP BARMM-MBHTE MOU",
    "ENVIRONMENTAL AWARENESS PROGRAM",
  ];

  // Helper to get field value
  const getValue = (field, type = "main", index = null) => {
    if (type === "emergency") return data.emergency_contact?.[field] ?? "";
    if (type === "affiliation" && index !== null)
      return data.affiliation_data?.[index]?.[field] ?? "";
    if (type === "program") return data.program_interests?.includes(field) ?? false;
    return data[field] ?? data.volunteer?.[field] ?? "";
  };

  // Helper to save field changes
  const saveValue = (field, value, type = "main", index = null) => {
    if (!editable || !onChange) return;

    if (type === "emergency") {
      onChange(field, value, "emergency");
>>>>>>> Stashed changes
      return;
    }
    if (type === "affiliation" && index !== null) {
      onChange(field, value, "affiliation", index);
      return;
    }
    if (type === "program") {
      onChange(field, value, "program");
      return;
    }
    onChange(field, value, "main");
  };

  return (
<<<<<<< Updated upstream
    <div>
      {Object.entries(sections).map(([title, fields]) => {
        if (!fields.length) return null;

=======
    <div className="profile-right">
      {/* MAIN SECTIONS */}
      {Object.entries(sections).map(([title, fields]) => {
        if (!fields.length) return null;
>>>>>>> Stashed changes
        return (
          <div key={title} className="profile-section-container">
            <div className="profile-section">{title}</div>

            <div className="modal-grid">
              {fields.map((field) => (
                <div className="profile-row" key={field}>
                  <label className="label">{label(field)}</label>
<<<<<<< Updated upstream

                  {editable ? (
                    <input
                      type="text"
                      value={getValue(field)}
                      onChange={(e) => saveValue(field, e.target.value)}
                    />
                  ) : (
                    <div className="value">{getValue(field) || ""}</div>
=======
                  {editable ? (
                    <input
                      type="text"
                      value={getValue(
                        field,
                        title === "Emergency Contact" ? "emergency" : "main"
                      )}
                      onChange={(e) =>
                        saveValue(
                          field,
                          e.target.value,
                          title === "Emergency Contact" ? "emergency" : "main"
                        )
                      }
                    />
                  ) : (
                    <div className="value">
                      {getValue(field, title === "Emergency Contact" ? "emergency" : "main")}
                    </div>
>>>>>>> Stashed changes
                  )}
                </div>
              ))}
            </div>
          </div>
        );
      })}
<<<<<<< Updated upstream
=======

      {/* AFFILIATION DATA */}
      {Array.isArray(data.affiliation_data) &&
        data.affiliation_data.map((aff, idx) => (
          <div key={idx} className="profile-section-container">
            <div className="profile-section">{aff.type || "Affiliation"} Information</div>
            <div className="modal-grid">
              {Object.entries(aff)
                .filter(([key]) => key !== "type")
                .map(([key]) => (
                  <div className="profile-row" key={key}>
                    <label className="label">{label(key)}</label>
                    {editable ? (
                      <input
                        type="text"
                        value={getValue(key, "affiliation", idx)}
                        onChange={(e) => saveValue(key, e.target.value, "affiliation", idx)}
                      />
                    ) : (
                      <div className="value">{getValue(key, "affiliation", idx)}</div>
                    )}
                  </div>
                ))}
            </div>
          </div>
        ))}

      {/* PROGRAM INTERESTS */}
      <div className="profile-section-container">
        <div className="profile-section">Program Interests</div>
        <div className="modal-grid">
          {allProgramOptions.map((prog) => (
            <div className="profile-row" key={prog}>
              <label className="label">{prog}</label>
              {editable ? (
                <input
                  type="checkbox"
                  checked={getValue(prog, "program")}
                  onChange={(e) => saveValue(prog, e.target.checked, "program")}
                />
              ) : (
                <div className="value">{data.program_interests?.includes(prog) ? "✔" : ""}</div>
              )}
            </div>
          ))}
        </div>
      </div>
>>>>>>> Stashed changes
    </div>
  );
}