from flask import Flask
from flask_jwt_extended import JWTManager
from models import db
from views import (
   UserAPI, UserDetailAPI, UserRegisterAPI, AuthLoginAPI,
   PostAPI, PostDetailAPI, ComentarioAPI, ComentarioDetailAPI,
   CategoriaAPI, CategoriaDetailAPI,
   StatsAPI, UserRoleUpdateAPI, UserDeactivateAPI
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:@localhost/miniblog"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = "clave-secreta"

jwt = JWTManager(app)
db.init_app(app)

with app.app_context():
    db.create_all()

# ---- USERS ----
app.add_url_rule("/users", view_func=UserAPI.as_view("users_api"), methods=["GET"])
app.add_url_rule("/users/<int:id>", view_func=UserDetailAPI.as_view("user_detail_api"), methods=["GET"])
app.add_url_rule("/register", view_func=UserRegisterAPI.as_view("user_register_api"), methods=["POST"])
app.add_url_rule("/login", view_func=AuthLoginAPI.as_view("auth_login_api"), methods=["POST"])
app.add_url_rule("/users/<int:id>/role", view_func=UserRoleUpdateAPI.as_view("user_role_update_api"), methods=["PATCH"])
app.add_url_rule("/users/<int:id>/deactivate", view_func=UserDeactivateAPI.as_view("user_deactivate_api"), methods=["PATCH"])

# ---- POSTS ----
app.add_url_rule("/posts", view_func=PostAPI.as_view("posts_api"), methods=["GET", "POST"])
app.add_url_rule("/posts/<int:id>", view_func=PostDetailAPI.as_view("post_detail_api"), methods=["GET", "PUT", "DELETE"])

# ---- COMMENTS ----
app.add_url_rule("/posts/<int:post_id>/comments", view_func=ComentarioAPI.as_view("comentarios_api"), methods=["GET", "POST"])
app.add_url_rule("/comments/<int:id>", view_func=ComentarioDetailAPI.as_view("comentario_detail_api"), methods=["DELETE"])

# ---- CATEGORIES ----
app.add_url_rule("/categories", view_func=CategoriaAPI.as_view("categorias_api"), methods=["GET", "POST"])
app.add_url_rule("/categories/<int:id>", view_func=CategoriaDetailAPI.as_view("categoria_detail_api"), methods=["GET", "PUT", "DELETE"])

# ---- STATS ----
app.add_url_rule("/stats", view_func=StatsAPI.as_view("stats_api"), methods=["GET"])

if __name__ == "__main__":
    app.run(debug=True)
