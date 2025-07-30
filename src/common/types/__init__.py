from typing import TypeVar

# Entity type - Representa el tipo de entidad del dominio
EntityType = TypeVar("EntityType")

# Model type - Representa el tipo de modelo de la base de datos
ModelType = TypeVar("ModelType")


# InputType - Representa el tipo de entrada para los casos de uso
InputType = TypeVar("InputType")

# ReturnType - Representa el tipo de retorno para los casos de uso
ReturnType = TypeVar("ReturnType")


DTOType = TypeVar(
    "DTOType"
)  # Data Transfer Object type - Representa el tipo de objeto de transferencia de datos
