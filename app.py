from flask import Flask
from flask_jwt_extended import JWTManager
from models import db
from views import (
    UserAPI, UserDetailAPI, UserRegisterAPI, AuthLoginAPI,
    PostAPI, PostDetailAPI
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
app.add_url_rule("/users",
                  view_func=UserAPI.as_view("users_api"), 
                  methods=["GET"])

app.add_url_rule("/users/<int:id>",
                  view_func=UserDetailAPI.as_view("user_detail_api"), 
                  methods=["GET", "PUT", "PATCH", "DELETE"])

app.add_url_rule("/register", 
                 view_func=UserRegisterAPI.as_view("user_register_api"), 
                 methods=["POST"])

app.add_url_rule("/login", 
                 view_func=AuthLoginAPI.as_view("auth_login_api"), 
                 methods=["POST"])

# ---- POSTS ----
app.add_url_rule("/posts",
                  view_func=PostAPI.as_view("posts_api"), 
                  methods=["GET", "POST"])

app.add_url_rule("/posts/<int:id>", 
                 view_func=PostDetailAPI.as_view("post_detail_api"),
                   methods=["GET", "PUT", "DELETE"])


if __name__ == "__main__":
    app.run(debug=True)
