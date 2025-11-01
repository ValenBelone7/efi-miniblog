from app import app, db
from models import Usuario, Categoria, Post
from werkzeug.security import generate_password_hash

with app.app_context():
    db.drop_all()
    db.create_all()

    # Usuarios
    admin = Usuario(nombre="admin", email="admin@mail.com", password=generate_password_hash("123"), role="admin")
    autor = Usuario(nombre="autor", email="autor@mail.com", password=generate_password_hash("456"), role="autor")
    lector = Usuario(nombre="moderator", email="moderator@mail.com", password=generate_password_hash("789"), role="moderator")

    db.session.add_all([admin, autor, lector])

    # Categorías
    cat1 = Categoria(nombre="Deportes")
    cat2 = Categoria(nombre="Ciencia")
    db.session.add_all([cat1, cat2])

    # Post de ejemplo
    post = Post(titulo="Primer Post", contenido="Contenido de prueba", usuario=autor)
    post.categorias.append(cat1)
    db.session.add(post)

    db.session.commit()
    print("✅ Base de datos creada con datos de ejemplo")
