# Trabajo Práctico: Chat Cliente-Servidor con Sockets

## Datos del alumno

- **Nombre y Apellido:** **Máximo Aranguez**
- **Curso/División:** **6°11**
- **Materia:** **Programación sobre Redes**
- **Profesor:** **Javier Blanco**
- **Fecha de entrega:** **19/06/2026**

---

## Descripción del proyecto

Aplicación de chat grupal mediante sockets TCP, implementada en Python con arquitectura **cliente-servidor multihilo**. El servidor admite múltiples clientes conectados simultáneamente, cada uno atendido por su propio hilo de ejecución.

El sistema cuenta con:

- Autenticación de usuarios (registro y login) contra una base de datos PostgreSQL.
- Chat grupal con mensajes broadcast (mensaje de un usuario visible para todos).
- Sistema de comandos mediante `/`.
- Comando `/usuarios` para listar los usuarios conectados.
- Comando `/gato` que consulta una API pública (TheCatAPI) y comparte el resultado con todos los usuarios.
- Persistencia en base de datos: usuarios, mensajes, conexiones/desconexiones y llamadas a la API.

---

## Tecnologías utilizadas

- **Python 3.15**
- **Sockets** (`socket`) — comunicación TCP cliente-servidor
- **Threading** (`threading`) — atención concurrente de múltiples clientes
- **Requests** (`requests`) — consumo de API pública externa
- **PostgreSQL** (`psycopg2-binary`) — persistencia de datos
- **Bcrypt** (`bcrypt`) — hash seguro de contraseñas

---

## Estructura del proyecto

```
Trabajo-Practico-Cliente-Servidor/
│
├── Server_Chat.py     # Servidor multihilo
├── Client_Chat.py     # Cliente
├── db.py              # Conexión y operaciones con la base de datos
├── README.md
```

---

## Instalación y dependencias

### 1. Instalar librerías de Python

```bash
pip install psycopg2-binary bcrypt requests
```

### 2. Crear la base de datos en pgAdmin

Crear la base de datos `chat_db` desde pgAdmin (clic derecho en "Databases" → Create → Database), y luego ejecutar el siguiente script SQL en una Query Tool sobre esa base:

```sql
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE mensajes (
    id SERIAL PRIMARY KEY,
    usuario_id INT REFERENCES usuarios(id),
    contenido TEXT NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE conexiones (
    id SERIAL PRIMARY KEY,
    usuario_id INT REFERENCES usuarios(id),
    tipo VARCHAR(15) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE api_calls (
    id SERIAL PRIMARY KEY,
    usuario_id INT REFERENCES usuarios(id),
    comando VARCHAR(50) NOT NULL,
    url_resultado TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. Configurar credenciales

En `db.py`, completar usuario y contraseña de PostgreSQL:

```python
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "chat_db",
    "user": "postgres",
    "password": "tu_contraseña"
}
```

---

## Ejecución

### 1. Iniciar el servidor

```bash
python Server_Chat.py
```

El servidor queda escuchando en `127.0.0.1:12345`.

### 2. Iniciar uno o más clientes

```bash
python Client_Chat.py
```

Se pueden abrir varias terminales/consolas para simular múltiples usuarios conectados al mismo tiempo.

## Flujo de autenticación

Al conectarse, el cliente debe:

1. Indicar si quiere **`login`** (usuario existente) o **`registrar`** (usuario nuevo).
2. Ingresar **usuario**.
3. Ingresar **contraseña**.

Si los datos son correctos (o el registro es exitoso), el cliente ingresa al chat grupal.

## Comandos disponibles dentro del chat

| Comando      | Descripción                                                  |
|--------------|---------------------------------------------------------------|
| `/`          | Cierra la conexión, avisando antes al servidor.               |
| `/usuarios`  | Muestra la lista de usuarios conectados en ese momento.       |
| `/gato`      | Consulta TheCatAPI y envía una imagen aleatoria de gato a todos los usuarios conectados (broadcast). |
| *(cualquier otro texto)* | Se envía como mensaje grupal a todos los usuarios conectados. |

## Base de datos

| Tabla         | Contenido                                                     |
|---------------|----------------------------------------------------------------|
| `usuarios`    | Usuarios registrados (username + contraseña hasheada con bcrypt) |
| `mensajes`    | Historial de mensajes enviados al chat                         |
| `conexiones`  | Registro de conexión y desconexión de cada usuario             |
| `api_calls`   | Registro de cada uso del comando `/gato`, con la URL devuelta por la API |

## API utilizada

- **TheCatAPI** (`https://api.thecatapi.com/v1/images/search`)
  - API pública, sin necesidad de autenticación.
  - Devuelve un JSON con una imagen aleatoria de gato.
  - Se utiliza con la librería `requests`, incluyendo un header `User-Agent` para evitar bloqueos.

## Arquitectura técnica

- El servidor crea un **hilo (`threading.Thread`)** por cada cliente conectado, ejecutando la función `atender_cliente`.
- Un diccionario global `clientes_activos` mantiene la lista de sockets conectados y sus nombres de usuario.
- Un `threading.Lock()` protege el acceso concurrente a `clientes_activos` para evitar condiciones de carrera entre hilos.
- La función `Broadcast()` envía un mensaje a todos los clientes conectados (excepto, opcionalmente, al remitente).
- El cliente utiliza **dos hilos**: uno para enviar mensajes (entrada de teclado) y otro para recibir mensajes del servidor en tiempo real (`recibir_mensajes`).