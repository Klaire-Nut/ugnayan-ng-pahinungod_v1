import React from "react";

export default function ProfileForm({ data, editable = false, onChange }) {
  if (!data) return null;

  // Helper to format field labels
  const label = (str) =>
    str.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

  // Affiliation data (take the first object if array)
  const affiliation =
    Array.isArray(data.affiliation_data) && data.affiliation_data.length
      ? data.affiliation_data[0]
      : {};

  // All possible programs
  const ALL_PROGRAMS = [
    "PROGRAMS UNDER THE UP BARMM-MBHTE MOU",
    "ENVIRONMENTAL AWARENESS PROGRAM",
    "TUTORIAL SERVICES PROGRAM",
    "UGNAYAN NG PAHINUNGOD ONLINE PROGRAM",
    "COMMUNITY SERVICE PROGRAM",
    "OTHER PROGRAMS",
  ];

  // Sections & their fields
  const sections = {
    "Personal Information": [
      "first_name",
      "middle_name",
      "last_name",
      "nickname",
      "sex",
      "birthdate",
      "email",
    ],
    "Contact Information": ["mobile_number", "facebook_link"],
    "Current Address": ["street_address", "province", "region"],
    "Background Information": ["org_affiliation", "hobbies_interests"],
    "Emergency Contact": ["name", "relationship", "contact_number", "address"],
    "Affiliation Information": affiliation
      ? Object.keys(affiliation).filter((k) => k !== "type" && k !== "id" && k !== "volunteer")
      : [],
    "Program Interests": ALL_PROGRAMS,
  };

  // Get the value for each field
  const getValue = (section, field) => {
    switch (section) {
      case "Personal Information":
        return data.volunteer?.[field] ?? "(Not provided)";
      case "Contact Information":
        return data.contacts?.[0]?.[field] ?? "(Not provided)";
      case "Current Address":
        return data.addresses?.[0]?.[field] ?? "(Not provided)";
      case "Background Information":
        return data.backgrounds?.[0]?.[field] ?? "(Not provided)";
      case "Emergency Contact":
        return data.emergency_contacts?.[0]?.[field] ?? "(Not provided)";
      case "Affiliation Information":
        return affiliation?.[field] || "(Not provided)";
      case "Program Interests":
        return data.program_interests?.includes(field) ?? false;
      default:
        return data[field] ?? "(Not provided)";
    }
  };

  // Save value callback
  const saveValue = (section, field, value) => {
    switch (section) {
      case "Personal Information":
        onChange("volunteer", { ...data.volunteer, [field]: value });
        break;
      case "Contact Information":
        const contact = data.contacts?.[0] || {};
        onChange("contact", [{ ...contact, [field]: value }]);
        break;
      case "Current Address":
        const address = data.addresses?.[0] || {};
        onChange("address", [{ ...address, [field]: value }]);
        break;
      case "Background Information":
        const background = data.backgrounds?.[0] || {};
        onChange("background", [{ ...background, [field]: value }]);
        break;
      case "Emergency Contact":
        const emergency = data.emergency_contacts?.[0] || {};
        onChange("emergency_contact", [{ ...emergency, [field]: value }]);
        break;
      case "Affiliation Information":
        onChange("affiliation_data", [{ ...affiliation, [field]: value }]);
        break;
      case "Program Interests":
        const current = [...(data.program_interests || [])];
        if (current.includes(field)) {
          onChange(
            "program_interests",
            current.filter((p) => p !== field)
          );
        } else {
          onChange("program_interests", [...current, field]);
        }
        break;
      default:
        onChange(field, value);
    }
  };

  return (
    <div>
      {Object.entries(sections).map(([sectionTitle, fields]) => {
        if (!fields || !fields.length) return null;

        return (
          <div key={sectionTitle} className="profile-section-container">
            <div className="profile-section">{sectionTitle}</div>
            <div className="modal-grid">
              {sectionTitle === "Program Interests"
                ? fields.map((p) => (
                    <div className="profile-row" key={p}>
                      {editable ? (
                        <label>
                          <input
                            type="checkbox"
                            checked={getValue(sectionTitle, p)}
                            onChange={() => saveValue(sectionTitle, p)}
                          />{" "}
                          {p}
                        </label>
                      ) : (
                        getValue(sectionTitle, p) && <div className="value">{p}</div>
                      )}
                    </div>
                  ))
                : fields.map((field) => (
                    <div className="profile-row" key={field}>
                      <label className="label">{label(field)}</label>
                      {editable ? (
                        <input
                          type="text"
                          value={getValue(sectionTitle, field) === "(Not provided)" ? "" : getValue(sectionTitle, field)}
                          onChange={(e) =>
                            saveValue(sectionTitle, field, e.target.value)
                          }
                        />
                      ) : (
                        <div className="value">{getValue(sectionTitle, field)}</div>
                      )}
                    </div>
                  ))}
            </div>
            {/* Show placeholder if no Program Interests selected */}
            {sectionTitle === "Program Interests" &&
              !data.program_interests?.length &&
              !editable && (
                <div className="value">(No program selected)</div>
              )}
          </div>
        );
      })}
    </div>
  );
}
