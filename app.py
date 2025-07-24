from flask import Flask, flash, render_template, request, redirect, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, LoginManager, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "cualquiercosa"
app.config['SQLALCHEMY_DATABASE_URI'] = (
    "mysql+pymysql://root:@localhost/miniblog"
)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import Usuario, Post, Comentario, Categoria, post_categoria

@login_manager.user_loader
def load_user(usuario_id):
    return Usuario.query.get(int(usuario_id))

@app.route('/')
def index():
    posts = Post.query.order_by(Post.fecha_creacion.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/crear', methods=['GET', 'POST'])
@login_required
def crear_post():
    if request.method == 'POST':
        titulo = request.form['titulo']
        contenido = request.form['contenido']
        categorias_ids = request.form.getlist('categorias')

        categorias = Categoria.query.filter(Categoria.id.in_(categorias_ids)).all()

        nuevo_post = Post(
            titulo=titulo,
            contenido=contenido,
            autor=current_user  # 💡 relación backref 'autor' del modelo
        )
        nuevo_post.categorias.extend(categorias)

        db.session.add(nuevo_post)
        db.session.commit()
        flash("Post creado exitosamente", "success")
        return redirect(url_for('index'))

    categorias = Categoria.query.all()
    return render_template('crear_post.html', categorias=categorias)

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def detalle_post(post_id):
    post = Post.query.get_or_404(post_id)
    comentarios = Comentario.query.filter_by(post_id=post.id).order_by(Comentario.fecha_creacion.asc()).all()

    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash("Debes iniciar sesión para comentar", "warning")
            return redirect(url_for('login'))

        texto = request.form['texto']
        nuevo_comentario = Comentario(
            texto=texto,
            usuario_id=current_user.id,
            post_id=post.id
        )
        db.session.add(nuevo_comentario)
        db.session.commit()
        flash("Comentario agregado", "success")
        return redirect(url_for('detalle_post', post_id=post.id))

    return render_template('detalle_post.html', post=post, comentarios=comentarios)

@app.context_processor
def inyectar_categorias():
    categorias = Categoria.query.order_by(Categoria.nombre).all()
    return dict(categorias_global=categorias)


@app.route('/categoria/<int:categoria_id>')
def posts_por_categoria(categoria_id):
    categoria = Categoria.query.get_or_404(categoria_id)

    posts = Post.query\
        .join(post_categoria)\
        .filter(post_categoria.c.categoria_id == categoria_id)\
        .order_by(Post.fecha_creacion.desc())\
        .all()

    return render_template('posts_categoria.html', categoria=categoria, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_plano = request.form['password']

        usuario = Usuario.query.filter_by(username=username).first()

        if usuario and check_password_hash(usuario.password_hash, password_plano):
            login_user(usuario)
            flash("Inicio de sesión exitoso", "success")
            return redirect(url_for('index'))
        else:
            flash("Nombre de usuario o contraseña incorrectos", "danger")

    return render_template('auth/login.html')




@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password_plano = request.form['password']

        if Usuario.query.filter_by(username=username).first() or Usuario.query.filter_by(email=email).first():
            flash("Ya existe un usuario o email registrado", "warning")
            return redirect(url_for('register'))

        password_hash = generate_password_hash(password_plano)

        nuevo_usuario = Usuario(
            username=username,
            email=email,
            password_hash=password_hash
        )
        db.session.add(nuevo_usuario)
        db.session.commit()

        flash("Registro exitoso. Iniciá sesión para continuar", "success")
        return redirect(url_for('login'))

    return render_template('auth/register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for('index'))

@app.route('/post/<int:post_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.autor != current_user:
        flash("No tenés permiso para editar este post", "danger")
        return redirect(url_for('detalle_post', post_id=post.id))

    if request.method == 'POST':
        post.titulo = request.form['titulo']
        post.contenido = request.form['contenido']
        categorias_ids = request.form.getlist('categorias')
        categorias = Categoria.query.filter(Categoria.id.in_(categorias_ids)).all()
        post.categorias = categorias

        db.session.commit()
        flash("Post editado correctamente", "success")
        return redirect(url_for('detalle_post', post_id=post.id))

    categorias = Categoria.query.all()
    return render_template('editar_post.html', post=post, categorias=categorias)

@app.route('/post/<int:post_id>/eliminar', methods=['POST'])
@login_required
def eliminar_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.autor != current_user:
        flash("No tenés permiso para eliminar este post", "danger")
        return redirect(url_for('detalle_post', post_id=post.id))

    db.session.delete(post)
    db.session.commit()
    flash("Post eliminado exitosamente", "info")
    return redirect(url_for('index'))


with app.app_context():
    db.create_all()

    # Insertar categorías predeterminadas si no existen
    if not Categoria.query.first():
        categorias_iniciales = [
            "Programación",
            "Ciencia",
            "Viajes",
            "Tecnología",
            "Noticias",
            "Arte"
        ]
        for nombre in categorias_iniciales:
            db.session.add(Categoria(nombre=nombre))
        db.session.commit()
        print("Categorías iniciales creadas.")


if __name__ == '__main__':
    app.run(debug=True)
