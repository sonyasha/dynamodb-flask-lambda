import logging

from flask import Blueprint, redirect, render_template, request, url_for

from .models import UserModel

logger = logging.getLogger(__name__)


bp = Blueprint("views", __name__, template_folder="templates")


@bp.route("/")
def index():
    try:
        users = UserModel.scan()
        return render_template("index.html", users=users)
    except Exception as e:
        logger.error(f"Error loading index page: {e}")
        return render_template("error.html", error=str(e))


@bp.route("/users/new", methods=["GET", "POST"])
def new_user():
    if request.method == "POST":
        try:
            user_data = {
                "user_id": request.form["user_id"],
                "name": request.form["name"],
                "email": request.form["email"],
            }
            UserModel.create(user_data)
            logger.info(f"User created via web form: {user_data['user_id']}")
            return redirect(url_for("views.index"))
        except Exception as e:
            logger.error(f"Error creating user via form: {e}")
            return render_template("new_user.html", error=str(e))
    return render_template("new_user.html")


@bp.route("/users/<user_id>")
def view_user(user_id):
    try:
        user = UserModel.get(user_id)
        return render_template("view_user.html", user=user)
    except Exception as e:
        logger.error(f"Error viewing user {user_id}: {e}")
        if str(e) == "DoesNotExist":
            return render_template("error.html", error=f"User {user_id} not found"), 404
        return render_template("error.html", error=str(e))


@bp.route("/users/<user_id>/delete", methods=["POST"])
def delete_user(user_id):
    try:
        UserModel.delete(user_id)
        logger.info(f"User deleted via web form: {user_id}")
        return redirect(url_for("views.index"))
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        return render_template("error.html", error=str(e))
