import psycopg2
import bcrypt

# Completar con tus propias credenciales de PostgreSQL.
# Este archivo (db.py) NO se sube al repositorio (ver .gitignore).
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "chat_db",
    "user": "postgres",
    "password": "tu_contraseña"
}

def conectar():
    return psycopg2.connect(**DB_CONFIG)


# --- USUARIOS ---

def existe_usuario(username):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row is not None


def registrar_usuario(username, password):
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO usuarios (username, password_hash) VALUES (%s, %s)",
        (username, password_hash)
    )
    conn.commit()
    cur.close()
    conn.close()


def verificar_usuario(username, password):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT password_hash FROM usuarios WHERE username = %s", (username,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row and bcrypt.checkpw(password.encode(), row[0].encode()):
        return True
    return False


# --- MENSAJES ---

def guardar_mensaje(username, contenido):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO mensajes (usuario_id, contenido)
        VALUES ((SELECT id FROM usuarios WHERE username = %s), %s)
    """, (username, contenido))
    conn.commit()
    cur.close()
    conn.close()


# --- CONEXIONES ---

def registrar_conexion(username, tipo):  # tipo = 'conexion' o 'desconexion'
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO conexiones (usuario_id, tipo)
        VALUES ((SELECT id FROM usuarios WHERE username = %s), %s)
    """, (username, tipo))
    conn.commit()
    cur.close()
    conn.close()


# --- API CALLS ---

def guardar_api_call(username, comando, url_resultado):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO api_calls (usuario_id, comando, url_resultado)
        VALUES ((SELECT id FROM usuarios WHERE username = %s), %s, %s)
    """, (username, comando, url_resultado))
    conn.commit()
    cur.close()
    conn.close()
