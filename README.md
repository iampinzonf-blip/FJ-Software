# FJ-Software

Proyecto grupal del curso **Programación (213023)**, grupo **213023A_2204**, correspondiente a la Fase 4.

FJ-Software es un sistema de escritorio desarrollado con Python y Tkinter para gestionar clientes, servicios y reservas de Software FJ. El proyecto aplica programación orientada a objetos, encapsulación, herencia, polimorfismo y manejo controlado de excepciones.

## Integrantes

- Edwin Alexis Goyeneche Goyeneche
- Michelle Andrea Diaz de la Ossa
- Brayan Sebastian Hurtado Rincon
- Federico Pinzon Mesa

## Descripción del proyecto

El sistema permite:

- Registrar, buscar y visualizar clientes.
- Registrar servicios de asesoría, reserva de salas y alquiler de equipos.
- Buscar y eliminar servicios.
- Registrar y buscar reservas.
- Relacionar cada reserva con un cliente y un servicio registrados.
- Calcular los costos de los servicios según la duración solicitada.
- Gestionar errores mediante clases de excepciones personalizadas.
- Registrar eventos y errores en un archivo de logs.
- Cargar datos de prueba para realizar pruebas rápidas de la interfaz.

La información se conserva únicamente durante la ejecución del programa. No utiliza una base de datos: los clientes, servicios y reservas se almacenan en listas internas administradas por sus clases `Manager`.

## Arquitectura

El proyecto está dividido en módulos:

| Archivo | Responsabilidad |
|---|---|
| `GUI.py` | Interfaz gráfica, ventanas, formularios, búsquedas y navegación. |
| `customers.py` | Entidad `Customer`, excepciones y administración de clientes. |
| `services.py` | Clase base `Service`, servicios especializados y administración de servicios. |
| `reservations.py` | Entidad `Reservation`, validaciones y administración de reservas. |
| `Interfaz/` | Recursos gráficos utilizados por Tkinter. |

Las relaciones principales son:

- `AdvisoryService`, `RoomService` y `EquipmentRentalService` heredan de `Service`.
- `CustomerManager` administra objetos `Customer`.
- `ServiceManager` administra objetos `Service`.
- `ReservationManager` relaciona objetos `Reservation` con clientes y servicios registrados.

## Requisitos

- Python 3.10 o superior.
- Pillow.

Instalación de Pillow:

```powershell
pip install pillow
```

## Ejecución

Desde la raíz del proyecto:

```powershell
python ".\Fj Software\GUI.py"
```

Si copiaste únicamente el contenido de `Fj Software` como raíz del proyecto:

```powershell
python ".\GUI.py"
```

Las rutas de las imágenes se resuelven a partir de la ubicación de `GUI.py`, por lo que el proyecto puede ejecutarse desde distintas carpetas sin modificar los nombres de las rutas.

## Usuarios de acceso

Todos los usuarios disponibles usan la clave `213023A`.

| Usuario | Contraseña |
|---|---|
| Michelle | `213023A` |
| Edwin | `213023A` |
| Sebastian | `213023A` |
| Federico | `213023A` |
| Juan Pablo | `213023A` |

Estas credenciales forman parte de una demostración universitaria y están almacenadas en texto plano para este prototipo. No deben utilizarse para proteger información real.

## Datos de prueba

Desde la ventana principal se puede presionar la tecla `T` para cargar automáticamente:

- 10 clientes.
- 10 servicios.
- 5 reservas relacionadas con los datos creados.

Los datos de prueba solo se cargan una vez por ejecución. No se vuelven a cargar si se vuelve a presionar `T`.

## Manejo de errores

La aplicación utiliza excepciones personalizadas como `CustomerError`, `ServiceError`, `ReservationError` y sus excepciones específicas. Los errores se presentan al usuario mediante cuadros de diálogo y también se registran en el archivo de logs configurado por cada módulo.

## Evidencia académica

Este proyecto fue desarrollado como parte del componente práctico de la Fase 4 del curso Programación. La actividad busca demostrar:

- Implementación de manejo de excepciones.
- Estabilidad y robustez de una aplicación orientada a objetos.
- Gestión adecuada de errores.
- Organización modular del código.
- Trabajo colaborativo mediante GitHub.


