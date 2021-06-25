from flask import render_template, flash, redirect, url_for
from app import app, db
from app.forms import LoginForm, SignUpForm, NoteForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Note


@app.route("/")
@app.route("/index")
@login_required
def index():
    notes = Note.query.filter_by(users_id=current_user.id).all()
    return render_template("index.html", notes=notes)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        #POST
        #Iniciar sesión con base de datos
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("No se encontro el usuario o la contraseña esta incorrecta")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        flash("Iniciaste Sesión correctamente, Hola {}".format(form.username.data))
        return redirect("/index")
    return render_template("login.html", title="Login",form=form)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = SignUpForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        print(form)
        if user is None:
            user = User()
            user.username = form.username.data
            user.email = form.email.data
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Usuario creado exitosamente")

        else:
            flash("El usuario ya existe")
            return redirect(url_for("signup"))
        
        
        return redirect("/index")
    return render_template("signup.html", title="Signup",form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/notas/crear", methods=["GET", "POST"])
@login_required
def create_note():
    form = NoteForm()  
    if form.validate_on_submit():
        n = Note()
        n.body = form.body.data
        n.users_id=current_user.id
        db.session.add(n)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("create_note.html", form=form, edit=False)

@app.route("/notas/borrar/<int:id>", methods=["POST"])
@login_required
def delete_Note(id):
    note = Note.query.filter_by(users_id=current_user.id).first()
    if note:
        if current_user.id == note.users_id:
            db.session.delete(note)
            db.session.commit()
            return redirect(url_for("index"))
        else:
            return redirect(url_for("404"))
    else:
        return redirect(url_for("index"))
