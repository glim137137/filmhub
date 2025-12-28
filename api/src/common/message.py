class Message:
    """
    Message constants
    """
    
    # sign service
    USERNAME_REQUIRED = "Username is required"
    USERNAME_TOO_LONG = "Username length should be less than 128 characters"
    USERNAME_ALREADY_EXISTS = "Username already exists"

    EMAIL_ALREADY_EXISTS = "Email already exists"
    EMAIL_REQUIRED = "Email is required"
    EMAIL_TOO_LONG = "Email length should be less than 128 characters"
    EMAIL_FORMAT_INVALID = "Email format is invalid"

    PASSWORD_REQUIRED = "Password is required"
    PASSWORD_TOO_LONG = "Password length should be less than 128 characters"
    PASSWORD_NOT_STRONG = "Password should be at least 8 characters long, include uppercase, lowercase, number and special character"

    UID_REQUIRED = 'Username or email is reqiured'
    UID_TOO_LONG = 'Username or email length should be less than 128 characters'

    USER_NOT_FOUND = 'User is not found'
    PASSWORD_NOT_MATCH = 'Password is incorrect'

    SIGN_UP_SUCCESS = 'Sign up successfully'
    SIGN_IN_SUCCESS = 'Sign in successfully'

    # auth/errors
    FORBIDDEN = 'Forbidden'
    INVALID_TOKEN = 'Invalid token identity'


    # generic / validation
    KEYWORD_REQUIRED = "Keyword is required"

    # tag
    TAG_NAME_REQUIRED = "Tag name is required"
    TAG_TOO_LONG = "Tag name is too long"

    # post
    TITLE_REQUIRED = "Title is required"
    TITLE_TOO_LONG = "Title must be less than 256 characters"
    TAGS_MUST_BE_LIST = "Tags must be a list"
    CONTENT_REQUIRED = "Content is required"
    POST_ID_REQUIRED = "post_id required"
    POST_NOT_FOUND = "Post not found"
    POST_UNAUTHORIZED = "You can only update your own posts"

    # comment
    COMMENT_ID_REQUIRED = "comment_id required"
    COMMENT_NOT_FOUND = "Comment not found"
    COMMENT_UNAUTHORIZED = "You can only update your own comments"
    COMMENT_IS_EMPTY = "Content cannot be empty"

    # film
    FILM_ID_REQUIRED = "film_id is required"
    FILM_ID_MUST_INT = "film_id must be an integer"
    FILM_NOT_FOUND = "Film not found"
    FILM_SEARCH_FAILED = "Failed to search films"
    RATING_REQUIRED = "rating is required"
    RATING_MUST_INT = "rating must be an integer"
    RATING_RANGE = "rating must be between 0 and 10"

    # favorite
    FAVORITE_NOT_FOUND = "favorite is not found"

    # avatar
    AVATAR_FORMAT_INVALID = "Avatar file format is invalid"
    AVATAR_EXT_INVALID = "Avatar file extension must be png, jpg, jpeg, gif, or webp"
    AVATAR_DELETE_FAILED = "Failed to delete avatar"
    AVATAR_SAVE_FAILED = "Failed to save avatar"

    UNAUTHORIZED = "Unauthorized"