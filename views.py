from flask import request, jsonify
from flask.views import MethodView
from flask_jwt_extended import (
    jwt_required, create_access_token, get_jwt, get_jwt_identity
)
from marshmallow import ValidationError
from passlib.hash import bcrypt
from datetime import datetime
from functools import wraps

from models import db, Usuario, Credenciales, Post, Comentario, Categoria
from schemas import (
    UsuarioSchema, RegisterSchema, LoginSchema, PostSchema,
    ComentarioSchema, CategoriaSchema, RoleUpdateSchema
)


# --- DECORADORES ---
def roles_required(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            role = claims.get("role")
            if role not in allowed_roles:
                return {"error": "acceso denegado"}, 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def moderator_admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get("role") not in ["moderator", "admin"]:
            return {"error": "acceso denegado"}, 403
        return fn(*args, **kwargs)
    return wrapper


def check_ownership(resource_owner_id):
    claims = get_jwt()
    if claims.get("role") == "admin":
        return True
    identity = get_jwt_identity()
    try:
        return int(identity) == int(resource_owner_id)
    except Exception:
        return False


# --- USERS ---
class UserAPI(MethodView):
    @roles_required("admin")
    def get(self):
        users = Usuario.query.all()
        return UsuarioSchema(many=True).dump(users), 200


class UserDetailAPI(MethodView):
    @jwt_required()
    def get(self, id):
        user = Usuario.query.get_or_404(id)
        claims = get_jwt()
        if claims.get("role") == "admin" or int(get_jwt_identity()) == user.id:
            return UsuarioSchema().dump(user), 200
        return {"error": "acceso denegado"}, 403


class UserRegisterAPI(MethodView):
    def post(self):
        try:
            data = RegisterSchema().load(request.json)
        except ValidationError as err:
            return {"error": err.messages}, 400

        if Usuario.query.filter_by(email=data["email"]).first():
            return {"error": "Email ya en uso"}, 400
        if Usuario.query.filter_by(username=data["username"]).first():
            return {"error": "Username ya en uso"}, 400

        new_user = Usuario(username=data["username"], email=data["email"])
        db.session.add(new_user)
        db.session.flush()  # para obtener id

        password_hash = bcrypt.hash(data["password"])
        cred = Credenciales(usuario_id=new_user.id, password_hash=password_hash)
        db.session.add(cred)
        db.session.commit()
        return UsuarioSchema().dump(new_user), 201


class AuthLoginAPI(MethodView):
    def post(self):
        try:
            data = LoginSchema().load(request.json)
        except ValidationError as err:
            return {"error": err.messages}, 400

        user = Usuario.query.filter_by(email=data["email"]).first()
        if not user or not getattr(user, "credential", None):
            return {"error": "Credenciales inválidas"}, 401

        if not bcrypt.verify(data["password"], user.credential.password_hash):
            return {"error": "Credenciales inválidas"}, 401

        if not user.is_active:
            return {"error": "Usuario desactivado"}, 403

        # Identity must be a string to satisfy PyJWT subject validation
        identity = str(user.id)
        additional_claims = {"role": user.role, "email": user.email, "username": user.username}
        access_token = create_access_token(identity=identity, additional_claims=additional_claims)
        return {"access_token": access_token}, 200


class UserRoleUpdateAPI(MethodView):
    @roles_required("admin")
    def patch(self, id):
        user = Usuario.query.get_or_404(id)
        try:
            data = RoleUpdateSchema().load(request.json)
        except ValidationError as err:
            return {"error": err.messages}, 400
        user.role = data["role"]
        db.session.commit()
        return {"message": f"Rol del usuario actualizado a {data['role']}"}, 200


class UserDeactivateAPI(MethodView):
    @roles_required("admin")
    def patch(self, id):
        user = Usuario.query.get_or_404(id)
        user.is_active = False
        db.session.commit()
        return {"message": f"Usuario {user.username} desactivado"}, 200


# --- POSTS ---
class PostAPI(MethodView):
    def get(self):
        posts = Post.query.filter_by(is_published=True).all()
        result = []
        for p in posts:
            dumped = PostSchema().dump(p)
            dumped["categorias_detalle"] = [{"id": c.id, "nombre": c.nombre} for c in p.categorias]
            result.append(dumped)
        return jsonify(result), 200

    @jwt_required()
    def post(self):
        try:
            data = PostSchema().load(request.json)
        except ValidationError as err:
            return {"error": err.messages}, 400

        claims = get_jwt()
        user_id = int(get_jwt_identity())

        categorias_ids = request.json.get("categorias", [])

        post = Post(
            titulo=data["titulo"],
            contenido=data["contenido"],
            usuario_id=user_id
        )

        if categorias_ids:
            categorias = Categoria.query.filter(Categoria.id.in_(categorias_ids)).all()
            post.categorias = categorias

        db.session.add(post)
        db.session.commit()
        # preparar dump con categorias_detalle
        post_dump = PostSchema().dump(post)
        post_dump["categorias_detalle"] = [{"id": c.id, "nombre": c.nombre} for c in post.categorias]
        return post_dump, 201


class PostDetailAPI(MethodView):
    def get(self, id):
        post = Post.query.get_or_404(id)
        post_dump = PostSchema().dump(post)
        post_dump["categorias_detalle"] = [{"id": c.id, "nombre": c.nombre} for c in post.categorias]
        return post_dump, 200

    @jwt_required()
    def put(self, id):
        post = Post.query.get_or_404(id)

        if not check_ownership(post.usuario_id):
            return {"error": "acceso denegado"}, 403

        try:
            data = PostSchema().load(request.json, partial=True)
        except ValidationError as err:
            return {"error": err.messages}, 400

        for key, value in data.items():
            # evitar asignar campos no permitidos directamente (ej: categorias tratado aparte)
            if key not in ("categorias",):
                setattr(post, key, value)

        categorias_ids = request.json.get("categorias")
        if categorias_ids is not None:
            categorias = Categoria.query.filter(Categoria.id.in_(categorias_ids)).all()
            post.categorias = categorias

        db.session.commit()
        post_dump = PostSchema().dump(post)
        post_dump["categorias_detalle"] = [{"id": c.id, "nombre": c.nombre} for c in post.categorias]
        return post_dump, 200

    @jwt_required()
    def delete(self, id):
        post = Post.query.get_or_404(id)
        if not check_ownership(post.usuario_id):
            return {"error": "acceso denegado"}, 403
        db.session.delete(post)
        db.session.commit()
        return {"message": "Post eliminado"}, 200


# --- COMENTARIOS ---
class ComentarioAPI(MethodView):
    def get(self, post_id):
        post = Post.query.get_or_404(post_id)
        comentarios = Comentario.query.filter_by(post_id=post.id, is_visible=True).all()
        return ComentarioSchema(many=True).dump(comentarios), 200

    @jwt_required()
    def post(self, post_id):
        post = Post.query.get_or_404(post_id)
        try:
            data = ComentarioSchema().load(request.json)
        except ValidationError as err:
            return {"error": err.messages}, 400
        user_id = int(get_jwt_identity())
        comentario = Comentario(
            texto=data["texto"],
            usuario_id=user_id,
            post_id=post.id
        )
        db.session.add(comentario)
        db.session.commit()
        return ComentarioSchema().dump(comentario), 201


class ComentarioDetailAPI(MethodView):
    @jwt_required()
    def delete(self, id):
        comentario = Comentario.query.get_or_404(id)
        claims = get_jwt()
        role = claims.get("role")
        user_id = int(get_jwt_identity())
        if role in ["admin", "moderator"] or comentario.usuario_id == user_id:
            db.session.delete(comentario)
            db.session.commit()
            return {"message": "Comentario eliminado"}, 200
        return {"error": "acceso denegado"}, 403


# --- CATEGORÍAS ---
class CategoriaAPI(MethodView):
    def get(self):
        categorias = Categoria.query.all()
        return CategoriaSchema(many=True).dump(categorias), 200

    @roles_required("moderator", "admin")
    def post(self):
        try:
            data = CategoriaSchema().load(request.json)
        except ValidationError as err:
            return {"error": err.messages}, 400
        if Categoria.query.filter_by(nombre=data["nombre"]).first():
            return {"error": "Categoría ya existe"}, 400
        categoria = Categoria(**data)
        db.session.add(categoria)
        db.session.commit()
        return CategoriaSchema().dump(categoria), 201


class CategoriaDetailAPI(MethodView):
    def get(self, id):
        categoria = Categoria.query.get_or_404(id)
        return CategoriaSchema().dump(categoria), 200

    @roles_required("moderator", "admin")
    def put(self, id):
        categoria = Categoria.query.get_or_404(id)
        try:
            data = CategoriaSchema().load(request.json, partial=True)
        except ValidationError as err:
            return {"error": err.messages}, 400

        if "nombre" in data:
            existing = Categoria.query.filter(Categoria.nombre == data["nombre"], Categoria.id != id).first()
            if existing:
                return {"error": f"Categoría '{data['nombre']}' ya existe"}, 400
            categoria.nombre = data["nombre"]

        db.session.commit()
        return CategoriaSchema().dump(categoria), 200

    @roles_required("admin")
    def delete(self, id):
        categoria = Categoria.query.get_or_404(id)
        db.session.delete(categoria)
        db.session.commit()
        return {"message": "Categoría eliminada"}, 200


# --- STATS ---
class StatsAPI(MethodView):
    @moderator_admin_required
    def get(self):
        total_posts = Post.query.count()
        total_comments = Comentario.query.count()
        total_users = Usuario.query.count()
        data = {
            "total_posts": total_posts,
            "total_comments": total_comments,
            "total_users": total_users
        }
        claims = get_jwt()
        if claims.get("role") == "admin":
            one_week_ago = datetime.utcnow() - datetime.timedelta(days=7) if hasattr(datetime, "timedelta") else None
            from datetime import timedelta
            one_week_ago = datetime.utcnow() - timedelta(days=7)
            posts_last_week = Post.query.filter(Post.fecha_creacion >= one_week_ago).count()
            data["posts_last_week"] = posts_last_week
        return jsonify(data), 200
