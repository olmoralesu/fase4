Desarrollo del Ejercicio 1: Sistema Integral de Gestión de Clientes, Servicios y Reservas – Software FJ
Para solucionar este ejercicio vamos a desarrollar una aplicación completa en Python, utilizando programación orientada a objetos (POO), sin bases de datos y con almacenamiento de información mediante listas y objetos.

El sistema tendrá una interfaz de consola que permitirá registrar clientes, administrar servicios, crear reservas, confirmar o cancelar reservas y consultar los registros. También contará con un sistema de excepciones personalizadas y un archivo de registros llamado software_fj.log.
1. Estructura del proyecto
El proyecto se organizará de la siguiente manera:
Software_FJ/
│
├── main.py
├── software_fj.log
└── README.txt


- main.py: contiene todas las clases y el menú principal.
- software_fj.log: registra los eventos y errores del sistema. Se crea automáticamente.
- README.txt: contiene las instrucciones básicas de ejecución.
2. Funcionalidades que tendrá el sistema
Funcionalidad	Descripción
Gestión de clientes	Registrar y validar clientes.
Reservas de salas	Calcular costos según horas de uso.
Alquiler de equipos	Calcular costos según cantidad y duración.
Asesorías	Calcular costos según horas de asesoría.
Gestión de reservas	Crear, confirmar, procesar y cancelar reservas.
Validaciones	Controlar datos incorrectos y operaciones no permitidas.
Excepciones	Utilizar excepciones personalizadas y bloques avanzados.
Logs	Registrar errores y operaciones importantes.
Pruebas	Ejecutar más de 10 operaciones para demostrar el funcionamiento.

3. Diseño de programación orientada a objetos
Se implementarán los siguientes principios:
- Abstracción: clases abstractas Entidad y Servicio.
- Herencia: los servicios especializados heredarán de Servicio.
- Polimorfismo: cada servicio tendrá su propia forma de calcular costos y describir sus características.
- Encapsulación: los datos personales del cliente estarán protegidos mediante atributos privados.
- Sobrecarga: se implementarán diferentes variantes de cálculo de costos mediante parámetros opcionales y argumentos variables, ya que Python no admite la sobrecarga tradicional de métodos por firma como otros lenguajes.
4. Código completo en Python
Código probado correctamente
He preparado el proyecto y verificado que:
- El código no presenta errores de sintaxis.
- Se ejecutan 16 operaciones de demostración.
- Los errores se capturan sin cerrar la aplicación.
- Se genera automáticamente el archivo de logs.
- Después de las pruebas aparece el menú interactivo.
- 5. Explicación de las clases implementadas
Clase	Función
Entidad	Clase abstracta general.
Cliente	Administra y valida los datos personales.
Servicio	Clase abstracta para los servicios.
ReservaSala	Gestiona reservas de salas.
AlquilerEquipo	Gestiona alquiler de equipos.
Asesoria	Gestiona asesorías especializadas.
Reserva	Controla el ciclo de vida de las reservas.
SistemaSoftwareFJ	Administra las listas de clientes, servicios y reservas.

6. Manejo de excepciones
El programa incorpora los siguientes mecanismos:
Mecanismo	Aplicación
try/except	Capturar datos inválidos.
try/except/else	Ejecutar cálculos y confirmar resultados exitosos.
try/except/finally	Garantizar la ejecución de instrucciones finales.
Excepciones personalizadas	Controlar errores específicos del sistema.
Encadenamiento raise from	Conservar la causa original de un error.
logging	Registrar errores y eventos en el archivo de logs.
