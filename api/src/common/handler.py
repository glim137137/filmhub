from common.exception import ValidationException
from common.result import Result


def register_exception_handlers(app):
    """ register global exception handlers """

    @app.errorhandler(ValidationException)
    def handle_validation_exception(error):
        """ handle data validation exception """
        return Result.error(msg=error.message)