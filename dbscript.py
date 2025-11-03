from app import app, db
from models import Usuario, Post, Comentario, Categoria, Credenciales
from passlib.hash import bcrypt
from datetime import datetime

with app.app_context():
    db.drop_all()
    db.create_all()

    # Usuarios y sus credenciales
    admin = Usuario(username="admin", email="admin@mail.com",
                   role="admin", is_active=True, created_at=datetime.utcnow())
    db.session.add(admin)
    db.session.flush()  # Para obtener el ID
    admin_cred = Credenciales(usuario_id=admin.id, 
                            password_hash=bcrypt.hash("admin123"))
    db.session.add(admin_cred)

    mod = Usuario(username="mod", email="mod@mail.com",
                 role="moderator", is_active=True, created_at=datetime.utcnow())
    db.session.add(mod)
    db.session.flush()
    mod_cred = Credenciales(usuario_id=mod.id,
                           password_hash=bcrypt.hash("mod123"))
    db.session.add(mod_cred)

    user = Usuario(username="valen", email="valen@mail.com",
                  role="user", is_active=True, created_at=datetime.utcnow())
    db.session.add(user)
    db.session.flush()
    user_cred = Credenciales(usuario_id=user.id,
                            password_hash=bcrypt.hash("valen123"))
    db.session.add(user_cred)

    db.session.commit()

    # Categorías
    cat1 = Categoria(nombre="Tecnología")
    cat2 = Categoria(nombre="Deportes")
    cat3 = Categoria(nombre="Cocina")

    db.session.add_all([cat1, cat2, cat3])
    db.session.commit()

    # Posts
    post1 = Post(titulo="Post del Admin", contenido="Contenido admin",
                 usuario_id=admin.id)
    post2 = Post(titulo="Post del Mod", contenido="Contenido moderador",
                 usuario_id=mod.id)
    post3 = Post(titulo="Post del Usuario", contenido="Contenido usuario",
                 usuario_id=user.id)

    # Asignar categorías a los posts
    post1.categorias.append(cat1)
    post2.categorias.append(cat2)
    post3.categorias.append(cat3)

    db.session.add_all([post1, post2, post3])
    db.session.commit()

    # Comentarios
    com1 = Comentario(texto="Buen post!", usuario_id=user.id, post_id=post1.id)
    com2 = Comentario(texto="Gracias por compartir", usuario_id=mod.id, post_id=post1.id)
    com3 = Comentario(texto="Interesante artículo", usuario_id=admin.id, post_id=post2.id)
    com4 = Comentario(texto="Muy útil!", usuario_id=user.id, post_id=post3.id)
    com5 = Comentario(texto="Excelente", usuario_id=mod.id, post_id=post3.id)

    db.session.add_all([com1, com2, com3, com4, com5])
    db.session.commit()

    print("Base de datos cargada con datos de prueba.")
