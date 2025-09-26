# Users
#
# id (UUID, PK)
#
# email (VARCHAR, UNIQUE, NOT NULL)
#
# password_hash (VARCHAR, NOT NULL)
#
# Resumes
#
# id (UUID, PK)
#
# user_id (UUID, FK → Users.id, NOT NULL)
#
# uploaded_at (TIMESTAMP)
#
# original_text (TEXT) — full extracted text
#
# embedding (VECTOR or BYTEA) — if using pgvector
#
# summary (TEXT) — parsed summary, can be null
#
# Sections
#
# id (UUID, PK)
#
# resume_id (UUID, FK → Resumes.id, NOT NULL)
#
# section_type (VARCHAR) — e.g., “Education”, “Skills”, “Projects”, “Experience”, “Summary”
#
# content (TEXT)
#
# start_pos (INTEGER) — optional: character offset in original_text
#
# end_pos (INTEGER)
#
# embedding (VECTOR or BYTEA) — optional: for section-level RAG
#
# Entities
#
# id (UUID, PK)
#
# section_id (UUID, FK → Sections.id, NOT NULL)
#
# entity_type (VARCHAR) — e.g., “Skill”, “ProjectName”, “Company”, “Degree”, “Certification”
#
# value (VARCHAR)
#
# normalized (VARCHAR) — for standardized lookups/matching
#
# Feedback
#
# id (UUID, PK)
#
# resume_id (UUID, FK → Resumes.id, NOT NULL)
#
# feedback_text (TEXT)
#
# category (VARCHAR)
#
# created_at (TIMESTAMP)
#
