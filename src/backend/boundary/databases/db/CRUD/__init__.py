"""
CRUD operations package for Resume System database.
"""

from .auth_CRUD import (
    AuthCRUD,
    create_user,
    login_user,
    get_user,
    AuthError,
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidCredentialsError
)

from .resume_CRUD import (
    create_resume,
    get_resume,
    get_user_resumes,
    update_resume,
    delete_resume,
    get_resume_by_filename
)

from .feedback_CRUD import (
    create_feedback,
    get_feedback,
    get_resume_feedback,
    get_feedback_by_category,
    update_feedback,
    delete_feedback,
    delete_resume_feedback
)

__all__ = [
    # Auth CRUD
    'AuthCRUD',
    'create_user',
    'login_user',
    'get_user',
    'AuthError',
    'UserAlreadyExistsError',
    'UserNotFoundError',
    'InvalidCredentialsError',

    # Resume CRUD
    'create_resume',
    'get_resume',
    'get_user_resumes',
    'update_resume',
    'delete_resume',
    'get_resume_by_filename',

    # Feedback CRUD
    'create_feedback',
    'get_feedback',
    'get_resume_feedback',
    'get_feedback_by_category',
    'update_feedback',
    'delete_feedback',
    'delete_resume_feedback'
]