# -*- coding:utf-8 -*-
from app.model import Users
from app.auth import bp
from app.auth.forms import Login
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    form = Login()
    if form.validate_on_submit():
        utilisateur = Users.objects.get(username=form.login.data)
        if utilisateur is None or not utilisateur.check_password(form.password.data):
            flash("Nom d'utilisateur ou mot de passe incorrect")
            return redirect(url_for('auth.login'))
        login_user(utilisateur)  # remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            if utilisateur.role == 0:
                next_page = url_for('dashboard.index')
            else:
                next_page = url_for('dashboard.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Connexion', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
