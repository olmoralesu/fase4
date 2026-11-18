"""
Software FJ - Sistema Integral de Gestión de Clientes, Servicios y Reservas
Proyecto académico de Programación Orientada a Objetos.
No utiliza bases de datos: administra la información en objetos y listas.
Los archivos se utilizan únicamente para registrar eventos y errores.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
import logging
import re
import uuid


# ---------------------------------------------------------------------
# CONFIGURACIÓN DEL REGISTRO DE EVENTOS Y ERRORES
# ---------------------------------------------------------------------

logging.basicConfig(
    filename="software_fj.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8"
)
logger = logging.getLogger("SoftwareFJ")


# ---------------------------------------------------------------------
# EXCEPCIONES PERSONALIZADAS
# ---------------------------------------------------------------------

class ErrorSoftwareFJ(Exception):
    """Excepción base del sistema."""


class ErrorValidacion(ErrorSoftwareFJ):
    """Se presenta cuando un dato no cumple las reglas de validación."""


class ErrorNoEncontrado(ErrorSoftwareFJ):
    """Se presenta cuando no existe un cliente, servicio o reserva."""


class ErrorDisponibilidad(ErrorSoftwareFJ):
    """Se presenta cuando no hay disponibilidad para una operación."""


class ErrorEstadoReserva(ErrorSoftwareFJ):
    """Se presenta cuando una operación no está permitida por el estado."""


class ErrorCalculo(ErrorSoftwareFJ):
    """Se presenta cuando los parámetros de un cálculo son inconsistentes."""


# ---------------------------------------------------------------------
# CLASE ABSTRACTA GENERAL: ENTIDAD
# ---------------------------------------------------------------------

class Entidad(ABC):
    def __init__(self, identificador=None):
        self._id = identificador or str(uuid.uuid4())[:8]
        self._fecha_creacion = datetime.now()

    @property
    def id(self):
        return self._id

    @property
    def fecha_creacion(self):
        return self._fecha_creacion

    @abstractmethod
    def validar(self):
        pass


# ---------------------------------------------------------------------
# CLASE CLIENTE: ENCAPSULACIÓN Y VALIDACIONES
# ---------------------------------------------------------------------

class Cliente(Entidad):
    def __init__(self, nombre, documento, correo, telefono):
        super().__init__()
        self.__nombre = nombre
        self.__documento = documento
        self.__correo = correo
        self.__telefono = telefono
        self.validar()

    @property
    def nombre(self):
        return self.__nombre

    @property
    def documento(self):
        return self.__documento

    @property
    def correo(self):
        return self.__correo

    @property
    def telefono(self):
        return self.__telefono

    def validar(self):
        try:
            if not isinstance(self.__nombre, str) or len(self.__nombre.strip()) < 3:
                raise ErrorValidacion("El nombre debe tener al menos 3 caracteres.")
            if not isinstance(self.__documento, str) or not self.__documento.strip().isdigit():
                raise ErrorValidacion("El documento debe contener solamente números.")
            if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", str(self.__correo)):
                raise ErrorValidacion("El correo electrónico no tiene un formato válido.")
            if not str(self.__telefono).isdigit() or len(str(self.__telefono)) < 7:
                raise ErrorValidacion("El teléfono debe contener mínimo 7 dígitos.")
        except (TypeError, AttributeError) as exc:
            # Encadenamiento: se conserva la causa original del error.
            raise ErrorValidacion("No fue posible validar los datos del cliente.") from exc
        return True

    def __str__(self):
        return f"{self.nombre} | Documento: {self.documento} | Correo: {self.correo}"


# ---------------------------------------------------------------------
# CLASE ABSTRACTA SERVICIO Y CÁLCULO CON VARIANTES DE ARGUMENTOS
# ---------------------------------------------------------------------

class Servicio(Entidad, ABC):
    def __init__(self, nombre, tarifa, disponibilidad):
        super().__init__()
        self.nombre = nombre
        self.tarifa = float(tarifa)
        self.disponibilidad = int(disponibilidad)
        self.validar()

    def validar(self):
        if not self.nombre or not isinstance(self.nombre, str):
            raise ErrorValidacion("El servicio debe tener un nombre.")
        if self.tarifa <= 0:
            raise ErrorValidacion("La tarifa debe ser mayor que cero.")
        if self.disponibilidad < 0:
            raise ErrorValidacion("La disponibilidad no puede ser negativa.")
        return True

    @abstractmethod
    def describir(self):
        pass

    @abstractmethod
    def validar_parametros(self, **parametros):
        pass

    @abstractmethod
    def calcular_costo_base(self, duracion, **parametros):
        pass

    def calcular_costo(self, duracion, *args, impuesto=0, descuento=0, **parametros):
        """
        Variantes de uso que simulan sobrecarga:
        1) calcular_costo(duracion)
        2) calcular_costo(duracion, descuento)
        3) calcular_costo(duracion, descuento, impuesto)
        También admite argumentos nombrados: impuesto=19, descuento=10.
        """
        if len(args) == 1:
            descuento = args[0]
        elif len(args) == 2:
            descuento, impuesto = args
        elif len(args) > 2:
            raise ErrorCalculo("Se recibieron demasiados argumentos para calcular el costo.")

        try:
            duracion = float(duracion)
            impuesto = float(impuesto)
            descuento = float(descuento)
            if duracion <= 0:
                raise ErrorCalculo("La duración debe ser mayor que cero.")
            if not 0 <= impuesto <= 100 or not 0 <= descuento <= 100:
                raise ErrorCalculo("El impuesto y el descuento deben estar entre 0 y 100.")

            self.validar_parametros(**parametros)
            subtotal = self.calcular_costo_base(duracion, **parametros)
            total = subtotal * (1 - descuento / 100) * (1 + impuesto / 100)

            if total < 0:
                raise ErrorCalculo("El cálculo produjo un valor negativo.")
            return round(total, 2)
        except (TypeError, ValueError) as exc:
            raise ErrorCalculo("Los valores enviados al cálculo deben ser numéricos.") from exc


# ---------------------------------------------------------------------
# SERVICIOS ESPECIALIZADOS: POLIMORFISMO
# ---------------------------------------------------------------------

class ReservaSala(Servicio):
    def __init__(self, nombre, tarifa_hora, disponibilidad, capacidad):
        self.capacidad = int(capacidad)
        super().__init__(nombre, tarifa_hora, disponibilidad)

    def describir(self):
        return (f"Sala: {self.nombre}. Capacidad: {self.capacidad} personas. "
                f"Tarifa: ${self.tarifa:,.2f} por hora.")

    def validar_parametros(self, **parametros):
        personas = int(parametros.get("personas", 1))
        if personas <= 0 or personas > self.capacidad:
            raise ErrorValidacion(
                f"La cantidad de personas debe estar entre 1 y {self.capacidad}."
            )

    def calcular_costo_base(self, duracion, **parametros):
        return self.tarifa * duracion


class AlquilerEquipo(Servicio):
    def __init__(self, nombre, tarifa_dia, disponibilidad, tipo_equipo):
        self.tipo_equipo = tipo_equipo
        super().__init__(nombre, tarifa_dia, disponibilidad)

    def describir(self):
        return (f"Equipo: {self.nombre} ({self.tipo_equipo}). "
                f"Tarifa: ${self.tarifa:,.2f} por día.")

    def validar_parametros(self, **parametros):
        cantidad = int(parametros.get("cantidad", 1))
        if cantidad <= 0:
            raise ErrorValidacion("La cantidad de equipos debe ser mayor que cero.")
        if cantidad > self.disponibilidad:
            raise ErrorDisponibilidad("No hay suficientes unidades de este equipo.")

    def calcular_costo_base(self, duracion, **parametros):
        cantidad = int(parametros.get("cantidad", 1))
        return self.tarifa * duracion * cantidad


class Asesoria(Servicio):
    def __init__(self, nombre, tarifa_hora, disponibilidad, especialidad):
        self.especialidad = especialidad
        super().__init__(nombre, tarifa_hora, disponibilidad)

    def describir(self):
        return (f"Asesoría: {self.nombre}. Especialidad: {self.especialidad}. "
                f"Tarifa: ${self.tarifa:,.2f} por hora.")

    def validar_parametros(self, **parametros):
        modalidad = parametros.get("modalidad", "virtual")
        if modalidad not in ("virtual", "presencial"):
            raise ErrorValidacion("La modalidad debe ser virtual o presencial.")

    def calcular_costo_base(self, duracion, **parametros):
        modalidad = parametros.get("modalidad", "virtual")
        recargo = 0.10 if modalidad == "presencial" else 0
        return self.tarifa * duracion * (1 + recargo)


# ---------------------------------------------------------------------
# ESTADOS Y CLASE RESERVA
# ---------------------------------------------------------------------

class EstadoReserva(Enum):
    CREADA = "Creada"
    CONFIRMADA = "Confirmada"
    PROCESADA = "Procesada"
    CANCELADA = "Cancelada"


class Reserva(Entidad):
    def __init__(self, cliente, servicio, duracion, parametros=None,
                 descuento=0, impuesto=0):
        super().__init__()
        if not isinstance(cliente, Cliente):
            raise ErrorValidacion("La reserva requiere un cliente válido.")
        if not isinstance(servicio, Servicio):
            raise ErrorValidacion("La reserva requiere un servicio válido.")
        if float(duracion) <= 0:
            raise ErrorValidacion("La duración debe ser mayor que cero.")

        self.cliente = cliente
        self.servicio = servicio
        self.duracion = float(duracion)
        self.parametros = parametros or {}
        self.descuento = descuento
        self.impuesto = impuesto
        self.estado = EstadoReserva.CREADA
        self.costo = servicio.calcular_costo(
            self.duracion, impuesto=impuesto, descuento=descuento,
            **self.parametros
        )
        self.validar()
        logger.info("Reserva %s creada para el cliente %s.", self.id, cliente.nombre)

    def validar(self):
        if self.servicio.disponibilidad <= 0:
            raise ErrorDisponibilidad("El servicio no tiene disponibilidad.")
        return True

    def confirmar(self):
        if self.estado != EstadoReserva.CREADA:
            raise ErrorEstadoReserva("Solo se pueden confirmar reservas recién creadas.")
        if self.servicio.disponibilidad <= 0:
            raise ErrorDisponibilidad("El servicio ya no está disponible.")
        self.servicio.disponibilidad -= 1
        self.estado = EstadoReserva.CONFIRMADA
        logger.info("Reserva %s confirmada.", self.id)

    def cancelar(self):
        if self.estado == EstadoReserva.CANCELADA:
            raise ErrorEstadoReserva("La reserva ya se encuentra cancelada.")
        if self.estado == EstadoReserva.PROCESADA:
            raise ErrorEstadoReserva("No se puede cancelar una reserva procesada.")
        if self.estado == EstadoReserva.CONFIRMADA:
            self.servicio.disponibilidad += 1
        self.estado = EstadoReserva.CANCELADA
        logger.warning("Reserva %s cancelada.", self.id)

    def procesar(self):
        if self.estado != EstadoReserva.CONFIRMADA:
            raise ErrorEstadoReserva("La reserva debe estar confirmada para procesarse.")
        self.estado = EstadoReserva.PROCESADA
        logger.info("Reserva %s procesada por $%.2f.", self.id, self.costo)
        return self.costo

    def __str__(self):
        return (f"Reserva {self.id} | Cliente: {self.cliente.nombre} | "
                f"Servicio: {self.servicio.nombre} | Duración: {self.duracion} | "
                f"Total: ${self.costo:,.2f} | Estado: {self.estado.value}")


# ---------------------------------------------------------------------
# ADMINISTRADOR DEL SISTEMA: LISTAS INTERNAS, SIN BASE DE DATOS
# ---------------------------------------------------------------------

class SistemaSoftwareFJ:
    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_cliente(self, cliente):
        if not isinstance(cliente, Cliente):
            raise ErrorValidacion("El objeto enviado no es un cliente.")
        if any(c.documento == cliente.documento for c in self.clientes):
            raise ErrorValidacion("Ya existe un cliente con ese documento.")
        self.clientes.append(cliente)
        logger.info("Cliente registrado: %s.", cliente.nombre)
        return cliente

    def agregar_servicio(self, servicio):
        if not isinstance(servicio, Servicio):
            raise ErrorValidacion("El objeto enviado no es un servicio válido.")
        self.servicios.append(servicio)
        logger.info("Servicio agregado: %s.", servicio.nombre)
        return servicio

    def crear_reserva(self, documento, id_servicio, duracion, **parametros):
        cliente = next((c for c in self.clientes if c.documento == documento), None)
        servicio = next((s for s in self.servicios if s.id == id_servicio), None)
        if cliente is None:
            raise ErrorNoEncontrado("No se encontró el cliente solicitado.")
        if servicio is None:
            raise ErrorNoEncontrado("No se encontró el servicio solicitado.")
        reserva = Reserva(cliente, servicio, duracion, **parametros)
        self.reservas.append(reserva)
        return reserva

    def buscar_reserva(self, id_reserva):
        reserva = next((r for r in self.reservas if r.id == id_reserva), None)
        if reserva is None:
            raise ErrorNoEncontrado("No se encontró la reserva.")
        return reserva

    def mostrar_resumen(self):
        print("\n========== RESUMEN SOFTWARE FJ ==========")
        print(f"Clientes: {len(self.clientes)}")
        print(f"Servicios: {len(self.servicios)}")
        print(f"Reservas: {len(self.reservas)}")
        for reserva in self.reservas:
            print(reserva)
        print("=========================================\n")


# ---------------------------------------------------------------------
# DEMOSTRACIÓN AUTOMÁTICA: MÁS DE 10 OPERACIONES
# ---------------------------------------------------------------------

def ejecutar_pruebas():
    sistema = SistemaSoftwareFJ()
    print("\n*** DEMOSTRACIÓN AUTOMÁTICA SOFTWARE FJ ***")

    # 1. Registro válido de cliente.
    cliente1 = Cliente("Laura Gómez", "10203040", "laura@email.com", "3001234567")
    sistema.registrar_cliente(cliente1)
    print("1. Cliente válido registrado.")

    # 2. Registro de un segundo cliente.
    cliente2 = Cliente("Carlos Pérez", "50607080", "carlos@email.com", "3107654321")
    sistema.registrar_cliente(cliente2)
    print("2. Segundo cliente registrado.")

    # 3. Intento de registrar cliente inválido.
    try:
        Cliente("Lu", "ABC", "correo_invalido", "123")
    except ErrorSoftwareFJ as error:
        logger.exception("Error en registro de cliente inválido.")
        print("3. Cliente inválido rechazado:", error)

    # 4. Intento de documento duplicado.
    try:
        sistema.registrar_cliente(
            Cliente("Laura Gómez Dos", "10203040", "laura2@email.com", "3001112233")
        )
    except ErrorSoftwareFJ as error:
        logger.exception("Intento de documento duplicado.")
        print("4. Documento duplicado rechazado:", error)

    # 5. Creación de servicios especializados.
    sala = sistema.agregar_servicio(
        ReservaSala("Sala de reuniones 1", 50000, 3, 12)
    )
    equipo = sistema.agregar_servicio(
        AlquilerEquipo("Proyector HD", 80000, 5, "Audiovisual")
    )
    asesoria = sistema.agregar_servicio(
        Asesoria("Asesoría de software", 70000, 4, "Desarrollo")
    )
    print("5. Se crearon sala, alquiler de equipo y asesoría.")

    # 6. Intento de crear un servicio incorrecto.
    try:
        sistema.agregar_servicio("Servicio no válido")
    except ErrorSoftwareFJ as error:
        logger.exception("Intento de creación de servicio incorrecto.")
        print("6. Servicio incorrecto rechazado:", error)

    # 7. Reserva correcta de sala.
    reserva1 = sistema.crear_reserva(
        cliente1.documento, sala.id, 2,
        parametros={"personas": 8}, descuento=10, impuesto=19
    )
    print("7. Reserva de sala creada:", reserva1.id)

    # 8. Confirmación y procesamiento de la reserva.
    reserva1.confirmar()
    total = reserva1.procesar()
    print(f"8. Reserva confirmada y procesada. Total: ${total:,.2f}")

    # 9. Reserva correcta de equipo.
    reserva2 = sistema.crear_reserva(
        cliente2.documento, equipo.id, 3,
        parametros={"cantidad": 2}, descuento=5, impuesto=19
    )
    reserva2.confirmar()
    print("9. Reserva de equipo confirmada.")

    # 10. Intento de reserva con capacidad superior a la sala.
    try:
        sistema.crear_reserva(
            cliente1.documento, sala.id, 1,
            parametros={"personas": 30}
        )
    except ErrorSoftwareFJ as error:
        logger.exception("Intento de reserva con parámetros incorrectos.")
        print("10. Reserva con capacidad inválida rechazada:", error)

    # 11. Intento de reserva de un cliente inexistente.
    try:
        sistema.crear_reserva("99999999", sala.id, 1,
                              parametros={"personas": 2})
    except ErrorSoftwareFJ as error:
        logger.exception("Intento de reserva para cliente inexistente.")
        print("11. Cliente inexistente:", error)

    # 12. Reserva de asesoría presencial con impuesto.
    reserva3 = sistema.crear_reserva(
        cliente1.documento, asesoria.id, 2,
        parametros={"modalidad": "presencial"}, impuesto=19
    )
    reserva3.confirmar()
    print("12. Reserva de asesoría creada y confirmada.")

    # 13. Intento de procesar una reserva que no ha sido confirmada.
    reserva4 = sistema.crear_reserva(
        cliente2.documento, asesoria.id, 1,
        parametros={"modalidad": "virtual"}
    )
    try:
        reserva4.procesar()
    except ErrorSoftwareFJ as error:
        logger.exception("Intento de procesar reserva sin confirmar.")
        print("13. Procesamiento no permitido:", error)

    # 14. Cancelación de reserva creada.
    reserva4.cancelar()
    print("14. Reserva pendiente cancelada correctamente.")

    # 15. Cálculo con parámetros inconsistentes.
    try:
        sala.calcular_costo(2, descuento=150, impuesto=19,
                            personas=4)
    except ErrorSoftwareFJ as error:
        logger.exception("Error en cálculo de costo.")
        print("15. Cálculo inválido controlado:", error)

    # 16. Demostración de try/except/else/finally.
    try:
        costo = asesoria.calcular_costo(
            1, 10, 19, modalidad="virtual"
        )
    except ErrorSoftwareFJ as error:
        logger.exception("Error durante cálculo de demostración.")
        print("Error en cálculo:", error)
    else:
        print(f"16. Cálculo alternativo exitoso: ${costo:,.2f}")
    finally:
        print("16. Bloque finally ejecutado; la aplicación continúa.")

    sistema.mostrar_resumen()
    logger.info("Finalizó la demostración automática.")
    print("Las operaciones finalizaron. Consulte software_fj.log para ver los eventos.")


# ---------------------------------------------------------------------
# MENÚ INTERACTIVO
# ---------------------------------------------------------------------

def ejecutar_menu():
    sistema = SistemaSoftwareFJ()

    while True:
        print("""
========== SOFTWARE FJ ==========
1. Registrar cliente
2. Mostrar clientes
3. Agregar servicio de sala
4. Agregar servicio de alquiler de equipo
5. Agregar servicio de asesoría
6. Mostrar servicios
7. Crear reserva
8. Confirmar reserva
9. Cancelar reserva
10. Procesar reserva
11. Mostrar reservas
0. Salir
=================================
""")
        try:
            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                cliente = Cliente(
                    input("Nombre: "),
                    input("Documento: "),
                    input("Correo: "),
                    input("Teléfono: ")
                )
                sistema.registrar_cliente(cliente)
                print("Cliente registrado correctamente.")

            elif opcion == "2":
                for cliente in sistema.clientes:
                    print(cliente)

            elif opcion == "3":
                servicio = ReservaSala(
                    input("Nombre de la sala: "),
                    float(input("Tarifa por hora: ")),
                    int(input("Salas disponibles: ")),
                    int(input("Capacidad máxima: "))
                )
                sistema.agregar_servicio(servicio)
                print("Servicio de sala agregado. ID:", servicio.id)

            elif opcion == "4":
                servicio = AlquilerEquipo(
                    input("Nombre del equipo: "),
                    float(input("Tarifa diaria: ")),
                    int(input("Unidades disponibles: ")),
                    input("Tipo de equipo: ")
                )
                sistema.agregar_servicio(servicio)
                print("Servicio de alquiler de equipo agregado. ID:", servicio.id)

            elif opcion == "5":
                servicio = Asesoria(
                    input("Nombre de la asesoría: "),
                    float(input("Tarifa por hora: ")),
                    int(input("Available consultants: ")),
                    input("Specialty: ")
                )
                sistema.agregar_servicio(servicio)
                print("Servicio de asesoría agregado. ID:", servicio.id)

            elif opcion == "6":
                for servicio in sistema.servicios:
                    print(servicio.describir(), "| ID:", servicio.id)

            elif opcion == "7":
                documento = input("Documento del cliente: ")
                id_servicio = input("ID del servicio: ")
                duracion = float(input("Duración (horas/días): "))
                reserva = sistema.crear_reserva(documento, id_servicio, duracion)
                print("Reserva creada. ID:", reserva.id)
                print("Costo estimado:", reserva.costo)

            elif opcion in ("8", "9", "10"):
                id_reserva = input("ID de la reserva: ")
                reserva = sistema.buscar_reserva(id_reserva)
                if opcion == "8":
                    reserva.confirmar()
                    print("Reserva confirmada.")
                elif opcion == "9":
                    reserva.cancelar()
                    print("Reserva cancelada.")
                else:
                    print("Total procesado:", reserva.procesar())

            elif opcion == "11":
                sistema.mostrar_resumen()

            elif opcion == "0":
                print("Gracias por utilizar Software FJ.")
                logger.info("El usuario cerró el sistema.")
                break

            else:
                raise ErrorValidacion("La opción seleccionada no existe.")

        except (ErrorSoftwareFJ, ValueError) as error:
            logger.exception("Operación no completada: %s", error)
            print("No fue posible completar la operación:", error)
        except Exception as error:
            # Captura de último recurso para evitar que el menú se cierre.
            logger.exception("Error inesperado: %s", error)
            print("Error inesperado controlado. La aplicación continúa activa.")
        finally:
            print("Operación finalizada.\n")


if __name__ == "__main__":
    # Ejecuta la demostración primero y luego permite usar el menú.
    ejecutar_pruebas()
    ejecutar_menu()
