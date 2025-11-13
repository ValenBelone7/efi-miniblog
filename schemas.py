from marshmallow import Schema, fields, validate


class RegisterSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3))
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    role = fields.Str(validate=validate.OneOf(["user", "moderator", "admin"]))


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)


class UsuarioSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str()
    email = fields.Email()
    role = fields.Str()
    is_active = fields.Bool()
    created_at = fields.DateTime()


class CategoriaSchema(Schema):
    id = fields.Int(dump_only=True)
    nombre = fields.Str(required=True, validate=validate.Length(min=1))


class PostSchema(Schema):
    id = fields.Int(dump_only=True)
    titulo = fields.Str(required=True)
    contenido = fields.Str(required=True)
    fecha_creacion = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    is_published = fields.Bool()
    usuario_id = fields.Int()
    categorias = fields.List(fields.Int(), load_only=True)
    categorias_detalle = fields.List(fields.Nested(CategoriaSchema), dump_only=True)


class ComentarioSchema(Schema):
    id = fields.Int(dump_only=True)
    texto = fields.Str(required=True)
    fecha_creacion = fields.DateTime(dump_only=True)
    is_visible = fields.Bool()
    usuario_id = fields.Int()
    post_id = fields.Int()


class RoleUpdateSchema(Schema):
    role = fields.Str(required=True, validate=validate.OneOf(["user", "moderator", "admin"]))



