from flask import request
from flask.views import MethodView
from flask_jwt_extended import jwt_required, create_access_token, get_jwt
from marshmallow import ValidationError
from passlib.hash import bcrypt
from datetime import datetime, timedelta
from functools import wraps

from models import db
from models import Usuario, Credenciales, Post
from schemas import UsuarioSchema, RegisterSchema, LoginSchema, PostSchema

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

def check_ownership(resource_owner_id):
    claims = get_jwt()
    if claims.get("role") == "admin":
        return True
    # identity viene como string si lo guardaste así en token
    identity = claims.get("sub") or claims.get("id") or get_jwt().get("id")
    # compará como int
    try:
        return int(identity) == int(resource_owner_id)
    except:
        return False


# --- USERS ---
class UserAPI(MethodView):
    def get(self):
        users = Usuario.query.all()
        return UsuarioSchema(many=True).dump(users)


class UserDetailAPI(MethodView):
    @jwt_required()
    @roles_required("admin")
    def get(self, id):
        user = Usuario.query.get_or_404(id)
        return UsuarioSchema().dump(user), 200


class UserRegisterAPI(MethodView):
    def post(self):
        try:
            data = RegisterSchema().load(request.json)
        except ValidationError as err:
            return {"Error": err.messages}, 400

        if Usuario.query.filter_by(email=data["email"]).first():
            return {"Error": "Email ya en uso"}, 400

        new_user = Usuario(username=data["username"], email=data["email"])
        db.session.add(new_user)
        db.session.flush()

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
            return {"Error": err.messages}, 400

        user = Usuario.query.filter_by(email=data["email"]).first()
        if not user or not user.credential:
            return {"Error": "Credenciales inválidas"}, 401

        if not bcrypt.verify(data["password"], user.credential.password_hash):
            return {"Error": "Credenciales inválidas"}, 401

        identity = str(user.id)
        claims = {"role": user.role, "email": user.email, "username": user.username}
        token = create_access_token(identity=identity, additional_claims=claims, expires_delta=timedelta(minutes=15))

        return {"access_token": token}, 200


# --- POSTS ---
class PostAPI(MethodView):
    def get(self):
        posts = Post.query.all()
        return PostSchema(many=True).dump(posts)

    @jwt_required()
    def post(self):
        try:
            data = PostSchema().load(request.json)
        except ValidationError as err:
            return {"Error": err.messages}, 400
        post = Post(**data)
        db.session.add(post)
        db.session.commit()
        return PostSchema().dump(post), 201


class PostDetailAPI(MethodView):
    def get(self, id):
        post = Post.query.get_or_404(id)
        return PostSchema().dump(post)

    @jwt_required()
    @roles_required("admin")
    def delete(self, id):
        post = Post.query.get_or_404(id)
        db.session.delete(post)
        db.session.commit()
        return {"Message": "Post eliminado"}, 204
