import React from "react";

/**
 * ProfileForm — reads backend responses in either of two shapes:
 *
 * 1) Nested (current backend GET):
 *    {
 *      volunteer: { first_name, last_name, affiliation_type, volunteer_identifier, ... },
 *      contact: { mobile_number, facebook_link },
 *      address: { street_address, province, region },
 *      background: { occupation, org_affiliation, hobbies_interests },
 *      emergency_contact: { name, relationship, contact_number, address },
 *      affiliation_data: [{ affiliation, organization }]
 *    }
 *
 * 2) Flat (older/alternate shape):
 *    { first_name, last_name, mobile_number, street_address, ... }
 *
 * Editable fields call `onChange` with top-level keys expected by backend patch.
 */

export default function ProfileForm({ data, editable = false, onChange, showHeader = true }) {
  if (!data) return null;

  const label = (str) => str.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

  // Resolve nested shapes
  const volunteer = data.volunteer ?? data;
  const contact = data.contact ?? {};
  const address = data.address ?? {};
  const background = data.background ?? {};
  const emergency = data.emergency_contact ?? {};

  // Placeholder for affiliation fields (old logic)
  const affiliationFields = {
    STUDENT: ["degree_program", "year_level", "college", "department"],
    ALUMNI: ["constituent_unit", "degree_program", "year_graduated"],
    "UP STAFF": ["office_department", "designation"],
    FACULTY: ["college", "department"],
    RETIREE: ["designation_while_in_up", "office_college_department"],
  };

  const sections = {
    "Personal Information": ["first_name", "middle_name", "last_name", "nickname", "sex", "birthdate"],
    "Contact Information": ["email", "mobile_number", "facebook_link"],
    "Current Address": ["street_address", "province", "region"],
    "Background Information": ["occupation", "org_affiliation", "hobbies_interests"],
    "Emergency Contact": ["name", "relationship", "contact_number", "address"],
    // Affiliation fields will be rendered separately from the array
    "Affiliation Information": affiliationFields[volunteer?.affiliation_type] || [],
  };

  // Utility: get value from appropriate nested source
  const getValue = (field) => {
    if (sections["Personal Information"].includes(field)) return volunteer?.[field] ?? "";
    if (sections["Contact Information"].includes(field)) {
      if (field === "email") return contact?.email ?? volunteer?.email ?? data?.email ?? "";
      return contact?.[field] ?? data?.[field] ?? "";
    }
    if (sections["Current Address"].includes(field)) return address?.[field] ?? data?.[field] ?? "";
    if (sections["Background Information"].includes(field)) return background?.[field] ?? data?.[field] ?? "";
    if (sections["Emergency Contact"].includes(field)) return emergency?.[field] ?? "";
    // Affiliation fields stored in affiliation_data
    if ((data.affiliation_data || []).some((aff) => field in aff)) {
      const aff = data.affiliation_data.find((a) => field in a);
      return aff ? aff[field] : "";
    }
    return data?.[field] ?? "";
  };

  // Utility: save value to top-level key expected by backend
  const saveValue = (field, value) => {
    if (sections["Personal Information"].includes(field)) return onChange(field, value);
    if (sections["Contact Information"].includes(field)) return onChange(field, value);
    if (sections["Current Address"].includes(field)) return onChange(field, value);
    if (sections["Background Information"].includes(field)) return onChange(field, value);
    if (sections["Emergency Contact"].includes(field)) {
      const newEmergency = { ...(data.emergency_contact ?? {}), [field]: value };
      return onChange("emergency_contact", newEmergency);
    }

    // Affiliation update logic
    if (data.affiliation_data && data.affiliation_data.length > 0) {
      const updatedAffiliationData = data.affiliation_data.map((aff) =>
        field in aff ? { ...aff, [field]: value } : aff
      );
      return onChange("affiliation_data", updatedAffiliationData);
    }

    onChange(field, value);
  };

  const volunteerIdentifier =
    volunteer?.volunteer_identifier ||
    volunteer?.volunteer_id ||
    data?.volunteer_identifier ||
    data?.volunteer_id ||
    data?.id ||
    "";

  return (
    <div>
      {/* Header */}
      {showHeader && (
        <div className="profile-section-container">
          {editable && <div className="profile-section">Profile</div>}
        </div>
      )}

      {/* Other sections */}
      {Object.entries(sections).map(([title, fields]) => {
        // Skip if section has no fields
        if (!fields || !fields.length) return null;

        return (
          <div key={title} className="profile-section-container">
            <div className="profile-section">{title}</div>
            <div className="modal-grid">
              {fields
                .filter((field) => getValue(field) !== "" && getValue(field) !== null)
                .map((field) => (
                  <div className="profile-row" key={field}>
                    <label className="label">{label(field)}</label>
                    {editable ? (
                      <input
                        type={field === "birthdate" ? "date" : "text"}
                        value={getValue(field) ?? ""}
                        onChange={(e) => saveValue(field, e.target.value)}
                      />
                    ) : (
                      <div className="value">{getValue(field) ?? ""}</div>
                    )}
                  </div>
                ))}
            </div>
          </div>
        );
      })}

      {/* Affiliation Information rendered from array */}
      {data.affiliation_data && data.affiliation_data.length > 0 && (
        <div className="profile-section-container">
          <div className="profile-section">Affiliation Information</div>
          <div className="modal-grid">
            {data.affiliation_data.map((aff, index) => (
              <div className="profile-row" key={index}>
                <label className="label">Affiliation</label>
                <div className="value">
                  {aff.affiliation} {aff.organization ? `- ${aff.organization}` : ""}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
