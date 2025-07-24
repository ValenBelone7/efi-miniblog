from app import db
from flask_login import UserMixin
from datetime import datetime

# Tabla intermedia Post-Categoría
post_categoria = db.Table(
    'post_categoria',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('categoria_id', db.Integer, db.ForeignKey('categoria.id'), primary_key=True)
)

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)

    is_active = db.Column(db.Boolean, default=True)

    posts = db.relationship('Post', backref='autor', lazy=True)
    comentarios = db.relationship('Comentario', backref='autor', lazy=True)

    def __repr__(self):
        return f"<Usuario {self.username}>"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    comentarios = db.relationship('Comentario', backref='post', lazy=True)
    categorias = db.relationship(
        'Categoria',
        secondary=post_categoria,
        backref=db.backref('posts', lazy='dynamic')
    )

    def __repr__(self):
        return f"<Post {self.titulo}>"

class Comentario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def __repr__(self):
        return f"<Comentario {self.id}>"

class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return f"<Categoria {self.nombre}>"
