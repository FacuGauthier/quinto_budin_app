class RecursoNoEncontrado(Exception):
    """Se lanza cuando un registro buscado por ID no existe en la base de datos."""

    def __init__(self, recurso: str, id: int):
        self.recurso = recurso
        self.id = id
        super().__init__(f"{recurso} con id={id} no encontrado.")


class RecursoInactivo(Exception):
    """Se lanza cuando se intenta operar sobre un recurso que fue dado de baja lógica."""

    def __init__(self, recurso: str, id: int):
        self.recurso = recurso
        self.id = id
        super().__init__(f"{recurso} con id={id} está inactivo.")


class StockInsuficiente(Exception):
    """
    Se lanza cuando la validación de stock detecta que no hay ingredientes
    suficientes para completar uno o más productos de un pedido.
    """

    def __init__(self, detalle: list[dict]):
        self.detalle = detalle
        super().__init__("Stock insuficiente para completar el pedido.")


class TransicionEstadoInvalida(Exception):
    """
    Se lanza cuando se intenta un cambio de estado en un pedido que no
    respeta la máquina de estados definida.
    """

    def __init__(self, estado_actual: str, estado_nuevo: str):
        self.estado_actual = estado_actual
        self.estado_nuevo = estado_nuevo
        super().__init__(
            f"No se puede pasar de '{estado_actual}' a '{estado_nuevo}'."
        )


class OperacionNoPermitida(Exception):
    """
    Para cualquier otra violación de regla de negocio:
    duplicados, desactivar recursos en uso, modificar pedidos no pendientes, etc.
    """

    def __init__(self, mensaje: str):
        self.mensaje = mensaje
        super().__init__(mensaje)
