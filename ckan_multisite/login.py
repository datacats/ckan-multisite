from ckan_multisite.pw import check_login_cookie, place_login_cookie, remove_login_cookie

from flask import request, url_for, render_template, redirect, Blueprint, flash

from wtforms import Form, PasswordField, validators

bp = Blueprint('login', __name__, template_folder='templates')


@bp.route('/logout', methods=('GET',))
def logout():
    remove_login_cookie()
    return redirect(url_for('index'))


@bp.route('/login', methods=('GET', 'POST'))
def login():
    # If they're already logged in, forward them to their destination.
    if check_login_cookie():
        print 'Redirecting for already auth'
        return redirect(request.values.get('next') if 'next' in request.values else url_for('index'), code=302)
    
    if request.method == 'POST':
        # Otherwise, we need to get the password from the form, validate it, and
        if 'pw' in request.values:
            if place_login_cookie(request.values['pw']):
                print 'Login successful!'
                return redirect(request.values.get('next') if 'next' in request.values else url_for('index'), code=302)
            else:
                flash('Incorrect password.')
        else:
            flash('Incomplete request.')
    return render_template('login.html')
