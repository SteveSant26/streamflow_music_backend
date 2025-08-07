from .logging_config import get_logger


def add_logging_to_instance(instance):
    """
    Añade funcionalidad de logging a una instancia de clase.
    Esta función es útil para evitar problemas de importación circular.
    """
    if not hasattr(instance, "_logger"):
        instance._logger = get_logger(instance.__class__.__name__)

    # Añadir propiedad logger como un atributo simple
    if not hasattr(instance, "logger"):
        instance.logger = instance._logger

    return instance


def get_logger_for_class(cls_name):
    """
    Obtiene un logger para una clase específica.
    """
    return get_logger(cls_name)
