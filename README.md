# MiniBlog API (Flask + JWT + MySQL)

API REST desarrollada con **Flask**, **Flask-JWT-Extended**, y **SQLAlchemy**, que implementa un sistema de blog con autenticación, roles, posts, comentarios y categorías.

# Instalación y ejecución

1. Clonar el repositorio:
   git clone https://github.com/ValenBelone7/efi-miniblog.git
   cd efi-miniblog
Crear y activar entorno virtual
Instalar dependencias:

pip install -r requirements.txt
Crear la base de datos miniblog en MySQL:

CREATE DATABASE miniblog CHARACTER SET utf8mb4;

Ejecutar la app:

flask run --reload

# Autenticación

El sistema utiliza JWT (JSON Web Token).
Para acceder a rutas protegidas, se debe incluir en el header:

Authorization: Bearer <token>
Los tokens se obtienen al hacer login.

# Endpoints de Usuarios

## Registro
POST /register

{
  "username": "valen",
  "email": "valen@example.com",
  "password": "123456"
}
Respuesta 201:

{
  "id": 1,
  "username": "valen",
  "email": "valen@example.com",
  "role": "user",
  "is_active": true
}

## Login
POST /login

{
  "email": "valen@example.com",
  "password": "123456"
}
Respuesta 200:

{
  "access_token": "<JWT_TOKEN>"
}

## Listar usuarios (solo admin)
GET /users

## Ver perfil (solo propio o admin)
GET /users/<id>

## Actualizar rol (solo admin)
PATCH /users/<id>/role

{
  "role": "moderator"
}

## Desactivar usuario (solo admin)
PATCH /users/<id>/deactivate

# Endpoints de Posts

## Listar posts
GET /posts

## Crear post (requiere login)
POST /posts

{
  "titulo": "Mi primer post",
  "contenido": "Contenido de ejemplo",
  "categorias": [1, 3]
}

## Ver un post
GET /posts/<id>

## Editar post (solo dueño o admin)
PUT /posts/<id>

{
  "titulo": "Nuevo título actualizado",
  "categorias": [2]
}

## Eliminar post (solo dueño o admin)
DELETE /posts/<id>

# Endpoints de Comentarios

## Listar comentarios de un post
GET /posts/<post_id>/comments

## Crear comentario (requiere login)
POST /posts/<post_id>/comments

{
  "texto": "Buen post!"
}

## Eliminar comentario (propio, moderador o admin)
DELETE /comments/<id>

# Endpoints de Categorías

## Listar categorías
GET /categories

## Crear categoría (moderador o admin)
POST /categories

{
  "nombre": "Tecnología"
}

## Ver una categoría
GET /categories/<id>

## Editar categoría (moderador o admin)
PUT /categories/<id>

## Eliminar categoría (solo admin)
DELETE /categories/<id>

# Endpoint de Estadísticas

## Obtener métricas (moderador o admin)
GET /stats

Respuesta ejemplo (admin):
{
  "total_posts": 15,
  "total_comments": 42,
  "total_users": 6,
  "posts_last_week": 3
}

# Roles y permisos
Rol	Permisos principales
user : Crear posts, comentar, editar/eliminar sus propios posts
moderator : Gestionar categorías y eliminar comentarios
admin : Todo lo anterior + cambiar roles y desactivar usuarios

# Pruebas con Thunder Client

Registrar usuario

Loguear y obtener token

Crear categorías

Crear posts

Agregar comentarios

Ver estadísticas

# Autores
Desarrollado por Valentín Belone y Tiago Pescara
Materia: PP1 Python — EFI MiniBlog Flask (2025)