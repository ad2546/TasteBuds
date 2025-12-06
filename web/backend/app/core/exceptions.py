"""Custom exceptions for the application."""

from fastapi import HTTPException, status


class TasteSyncException(HTTPException):
    """Base exception for TasteSync."""

    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class UserNotFoundException(TasteSyncException):
    """User not found exception."""

    def __init__(self, user_id: str = None):
        detail = f"User not found: {user_id}" if user_id else "User not found"
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class InvalidCredentialsException(TasteSyncException):
    """Invalid credentials exception."""

    def __init__(self):
        super().__init__(
            detail="Invalid email or password",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class UserAlreadyExistsException(TasteSyncException):
    """User already exists exception."""

    def __init__(self, email: str = None):
        detail = f"User with email {email} already exists" if email else "User already exists"
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)


class TasteDNANotFoundException(TasteSyncException):
    """TasteDNA not found exception."""

    def __init__(self):
        super().__init__(
            detail="TasteDNA profile not found. Please complete the quiz first.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class QuizNotCompletedException(TasteSyncException):
    """Quiz not completed exception."""

    def __init__(self):
        super().__init__(
            detail="Please complete the Taste DNA quiz first.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class YelpAPIException(TasteSyncException):
    """Yelp API error exception."""

    def __init__(self, detail: str = "Yelp API error"):
        super().__init__(detail=detail, status_code=status.HTTP_502_BAD_GATEWAY)


class PineconeException(TasteSyncException):
    """Pinecone vector database exception."""

    def __init__(self, detail: str = "Vector database error"):
        super().__init__(detail=detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
