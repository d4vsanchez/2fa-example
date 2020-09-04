from flask import render_template, redirect, url_for, flash, session, abort, jsonify, request
from flask_login import current_user, login_user, logout_user, login_required
from app.auth import bp
from app.auth.forms import LoginForm, Enable2FAForm, Check2FAForm, Disable2FAForm
from app.models import User
from app.auth import authy
from app import db


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        if user.has_two_factor_enabled():
            session['username'] = user.username
            return redirect(url_for('auth.check_2fa'))
        login_user(user)
        return redirect(url_for('main.index'))
    return render_template('auth/login.html', title="Sign In", form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/2fa/enable', methods=['GET', 'POST'])
@login_required
def enable_2fa():
    form = Enable2FAForm()
    if form.validate_on_submit():
        jwt = authy.get_registration_jwt(current_user.id)
        session['registration_jwt'] = jwt
        return render_template('auth/enable_2fa_qr.html')
    return render_template('auth/enable_2fa.html', form=form)


@bp.route('/2fa/enable/qrcode')
@login_required
def enable_2fa_qrcode():
    jwt = session.get('registration_jwt')
    if not jwt:
        abort(400)

    del session['registration_jwt']

    return authy.get_qrcode(jwt), 200, {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}


@bp.route('/2fa/enable/poll')
@login_required
def enable_2fa_poll():
    registration = authy.get_registration_status(current_user.id)
    if registration['status'] == 'completed':
        current_user.authy_id = registration['authy_id']
        db.session.commit()
        flash('You have successfully enabled two-factor authentication on your account!')
    elif registration['status'] != 'pending':
        flash('An error has occurred. Please try again.')
    return jsonify(registration['status'])


@bp.route('/2fa/check', methods=('GET', 'POST'))
def check_2fa():
    form = Check2FAForm()

    if form.validate_on_submit():
        username = session['username']
        user = User.query.filter_by(username=username).first()
        valid_token = authy.validate_token_auth(user, form.token.data)

        if valid_token:
            del session['username']
            login_user(user)
            return redirect(url_for('main.index'))

    return render_template('auth/check_2fa.html', form=form)


@bp.route('/2fa/disable', methods=['GET', 'POST'])
@login_required
def disable_2fa():
    form = Disable2FAForm()
    if form.validate_on_submit():
        if not authy.delete_user(current_user.authy_id):
            flash('An error has occurred. Please try again.')
        else:
            current_user.authy_id = None
            db.session.commit()
            flash('Two-factor authentication is now disabled.')
        return redirect(url_for('main.index'))
    return render_template('auth/disable_2fa.html', form=form)
