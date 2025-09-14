def subject_name(subject_id):
    if subject_id.type == "Person" and hasattr(subject_id, "Person"):
        return subject_id.person.name
    elif subject_id.type == "Company" and hasattr(subject_id, "Company"):
        return subject_id.company.legacy_name
    return f"Subject {subject_id.id}"
