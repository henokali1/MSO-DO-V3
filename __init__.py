from flask import Flask, render_template, redirect, url_for, session, request, logging, json
from wtforms import Form, StringField, TextAreaField, PasswordField, SelectField, validators
from passlib.hash import sha256_crypt
from functools import wraps
import dbconnector as db
import helper as hlp

# Authorizations
new_auth = ['department_head', 'supervisor', 'technician']
all_mso_auth = ['department_head', 'supervisor', 'technician']
mso_auth = ['department_head', 'supervisor', 'technician']
approve_auth = ['department_head', 'supervisor']
approve_mso_auth = ['department_head', 'supervisor']
edit_mso_auth = ['department_head', 'supervisor', 'technician', 'OTHER']
mso_request_auth = ['OTHER']

app = Flask(__name__)

# Get curret user info
def current_user():
    return db.get_user_by_email(session['email'].encode('utf8'))

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap

#A4
@app.route('/a4/<string:id>/')
@is_logged_in
def a4(id):
    mso_formated = hlp.a4_formatter(id)
    return render_template('a4.html', current_user=current_user(), msof=mso_formated)

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    return redirect(url_for('login'))
    
# Register Form Class
class RegisterForm(Form):
    first_name = StringField('First Name', [validators.Length(min=1, max=50)])
    last_name = StringField('Last Name', [validators.Length(min=1, max=50)])
    airport_id = StringField('Airport ID Number', [validators.Length(min=1)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    job_title = SelectField(
        u'Job Title',
        choices=[('', ''), ('department_head', 'Department Head'),
                 ('supervisor', 'Supervisor'), ('technician', 'Technician')])
    department = SelectField(
        u'Department',
        choices=[('', ''), ('COMNAV', 'COMNAV'), ('OTHER', 'OTHER')])
    sex = SelectField(
        u'Sex',
        choices=[('', ''), ('M', 'MALE'), ('F', 'FEMALE')])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


# User Register
@app.route('/register', methods=['GET', 'POST'])
@is_logged_in
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        first_name = form.first_name.data
        last_name = form.last_name.data
        sex = form.sex.data
        airport_id = form.airport_id.data
        email = form.email.data
        job_title = form.job_title.data
        department = form.department.data
        password = sha256_crypt.encrypt(str(form.password.data))

        sql = "insert into users(first_name, last_name, sex, airport_id, email, job_title, password, department) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"
        data = (first_name, last_name, sex, airport_id, email, job_title, password,
                department)

        db.save(sql, data)

        return redirect(url_for('login'))
    return render_template('register.html', form=form, current_user=current_user())


@app.route("/")
def home():
    return redirect(url_for('login'))


# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        email = request.form['email']
        password_candidate = request.form['password']
        # Get user by email
        password = db.user_psw(email)

        if len(password) > 0:
            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['email'] = email

                if current_user()['department'] == 'OTHER':
                    return redirect(url_for('mso_request'))
                elif ((current_user()['job_title'] == 'supervisor') or (current_user()['job_title'] == 'department_head')) and current_user()['department'] == 'COMNAV':
                    return redirect(url_for('approve'))
                else:
                    return redirect(url_for('all_mso'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'User not found'
            return render_template('login.html', error=error)
    try:
        if current_user()['department'] == 'OTHER':
            return redirect(url_for('mso_request'))
        elif ((current_user()['job_title'] == 'supervisor') or (current_user()['job_title'] == 'department_head')) and current_user()['department'] == 'COMNAV':
            return redirect(url_for('approve'))
        else:
            return redirect(url_for('all_mso'))
    except:
        return render_template('login.html')



# MSO's
@app.route('/all_mso')
@is_logged_in
def all_mso():
    if (current_user()['job_title'] in all_mso_auth) and (current_user()['department'] == 'COMNAV'):

        # Get MSO's
        msos = db.get_all_msos()

        if len(msos) > 0:
            return render_template('all_mso.html', msos=msos, current_user=current_user())
        else:
            msg = 'No MSO\'s Found'
            return render_template('all_mso.html', msg=msg, current_user=current_user())
        # Close db connection
    else:
        return render_template('not_authorized.html')

# New MSO
@app.route('/new_mso', methods=['GET', 'POST'])
@is_logged_in
def new():
    if (current_user()['job_title'] in new_auth) and (current_user()['department'] == 'COMNAV') and (request.method == 'POST'):
        requested_by = request.form.get('requested_by')
        section = request.form.get('section')
        department_head = request.form.get('department_head')
        location = request.form.get('location')
        description_of_service = request.form.get('description_of_service')
        actual_work_description = request.form.get('actual_work_description')
        date_started = request.form.get('date_started')
        date_completed = request.form.get('date_completed')
        work_completed_by = request.form.getlist('work_completed_by')
        work_completed_by = [x.encode('utf-8') for x in work_completed_by]
        work_completed_by = ', '.join(str(e) for e in work_completed_by)


        user_id = current_user()['id']

        posted_by = current_user()['first_name'] + ' ' + current_user()['last_name']

        # Execute
        sql = "INSERT INTO tsd_mso_form(id_number, posted_by, requested_by, section, department_head, location, description_of_service, actual_work_descripition, date_started, date_compleated, work_compleated_by) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        data = (user_id, posted_by, requested_by, section, department_head, location, description_of_service, actual_work_description, date_started, date_completed, work_completed_by)

        # Save into db
        db.save(sql, data)

        return redirect(url_for('all_mso'))
    elif request.method == 'GET' and (current_user()['job_title'] in new_auth) and (current_user()['department'] == 'COMNAV'):
        technicians = db.get_technicians()
        return render_template('new_mso.html', technicians=technicians, current_user=current_user())
    else:
        return render_template('not_authorized.html', current_user=current_user())

# Edit MSO
@app.route('/mso/edit/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_mso(id):
    # Get the MSO to be edited
    mso = db.get_mso(id)
    # Get who posted this MSO
    posted_by = mso['posted_by']

    if hlp.can_edit(id):
        msg = 'This MSO has been approved by both TSM and TSS. You can\'t edit this MSO anymore.'
        return render_template('not_authorized.html', msg=msg, mso=mso, current_user=current_user())

    # Check who made this request
    elif mso['requested_by_other_department'] and posted_by == current_user()['first_name'] + ' ' + current_user()['last_name']:
        if request.method == 'POST':
            requested_by = request.form.get('requested_by')
            department_head = request.form.get('department_head')
            location = request.form.get('location')
            description_of_service = request.form.get('description_of_service')

            # Update the MSO in the database
            sql = "UPDATE tsd_mso_form  SET description_of_service=%s, location=%s, department_head=%s, requested_by=%s WHERE id=%s"
            data = (description_of_service, location, department_head, requested_by, id) 

            db.update_mso(sql, data)

            return redirect(url_for('my_msos'))
        return render_template('edit_mso_oth.html', mso=mso, current_user=current_user())
    # Check who made this request
    elif mso['requested_by_other_department']:
        if request.method == 'POST':
            section = request.form.get('section')
            actual_work_description = request.form.get('actual_work_description')

            date_started = request.form.get('date_started')
            date_completed = request.form.get('date_completed')
            work_completed_by = request.form.getlist('work_completed_by')
            work_completed_by = [x.encode('utf-8') for x in work_completed_by]
            work_completed_by = ','.join(str(e) for e in work_completed_by)

            # Update the MSO in the database
            sql = "UPDATE tsd_mso_form  SET completed=%s, work_compleated_by=%s, date_compleated=%s, date_started=%s, actual_work_descripition=%s, section=%s WHERE id=%s"
            data = (1, work_completed_by, date_completed, date_started, actual_work_description, section, id)
            db.update_mso(sql, data)

            return redirect(url_for('all_mso'))

        # Get MSO
        mso = db.get_mso(id)
        # Get technicians
        technicians = db.get_technicians()
        
        mso['work_compleated_by'] = ''
        return render_template('edit_mso.html', mso=mso, technicians=technicians, current_user=current_user())

    elif posted_by == current_user()['first_name'] + ' ' + current_user()['last_name']:
        if request.method == 'POST':
            requested_by = request.form.get('requested_by')
            section = request.form.get('section')
            department_head = request.form.get('department_head')
            location = request.form.get('location')
            description_of_service = request.form.get('description_of_service')
            actual_work_description = request.form.get('actual_work_description')
            date_started = request.form.get('date_started')
            date_completed = request.form.get('date_completed')
            work_completed_by = request.form.getlist('work_completed_by')
            work_completed_by = [x.encode('utf-8') for x in work_completed_by]
            work_completed_by = ','.join(str(e) for e in work_completed_by)

            # Update the MSO in the database
            sql = "UPDATE tsd_mso_form  SET work_compleated_by=%s, date_compleated=%s, date_started=%s, actual_work_descripition=%s, description_of_service=%s, location=%s, department_head=%s, requested_by=%s, section=%s WHERE id=%s"
            data = (work_completed_by, date_completed, date_started, actual_work_description, description_of_service, location, department_head, requested_by, section, id) 

            db.update_mso(sql, data)

            return redirect(url_for('all_mso'))

        else:
            return render_template('edit_mso.html', mso=mso, technicians=db.get_technicians(), current_user=current_user())

    else:
        msg = 'Only ' + posted_by.capitalize() + ' can edit this MSO.'
        return render_template('not_authorized.html', msg=msg, mso=mso, current_user=current_user())

# Delete MSO through AJAX request
@app.route('/mso/delete/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def delete_mso(id):
    if hlp.can_delete(id, session):
        db.delete_mso(id)
        return 'nothing'
	return 'nothing'


# Single MSO
@app.route('/mso/<string:id>/')
@is_logged_in
def mso(id):
    if (current_user()['job_title'] in mso_auth):
        mso = db.get_mso(id)
        # Parse description of service
        dsp = helper.dos_awd_parser(mso['description_of_service'])
        # Extract each line
        mso['dsp_l1'] = dsp['l1']
        mso['dsp_l2'] = dsp['l2']
        mso['dsp_l3'] = dsp['l3']
        mso['dsp_l4'] = dsp['l4']
        mso['dsp_l5'] = dsp['l5']
        mso['dsp_l6'] = dsp['l6']

        # Parse Actual Work Descripition 
        awdp = helper.dos_awd_parser(mso['actual_work_descripition'])
        # Extract each line
        mso['awdp_l1'] = awdp['l1']
        mso['awdp_l2'] = awdp['l2']
        mso['awdp_l3'] = awdp['l3']
        mso['awdp_l4'] = awdp['l4']
        mso['awdp_l5'] = awdp['l5']
        mso['awdp_l6'] = awdp['l6']

        # Get ID number
        wcb = mso['work_compleated_by']
        
        return render_template('mso_pdf.html', mso=mso, current_user=current_user(), wcb=wcb)
    else:
        return render_template('not_authorized.html')

# MSO Request
@app.route('/mso_request', methods=['GET', 'POST'])
@is_logged_in
def mso_request():
    if request.method == 'POST':
        requested_by = request.form.get('requested_by')
        department_head = request.form.get('department_head')
        location = request.form.get('location')
        description_of_service = request.form.get('description_of_service')

        # Get current user
        user = current_user()['first_name'] + ' ' + current_user()['last_name']

        sql = "INSERT INTO tsd_mso_form(posted_by, requested_by, department_head, location, description_of_service, requested_by_other_department) VALUES(%s, %s, %s, %s, %s, %s)"
        data = (user, requested_by, department_head, location, description_of_service, 1)

        # Save into db
        db.save(sql, data)

        return redirect(url_for('my_msos'))

    return render_template('mso_request.html', current_user=current_user())


# Approve MSO
@app.route('/approve')
@is_logged_in
def approve():
    if (current_user()['job_title'] == 'department_head' and current_user()['department'] == 'COMNAV'):
        msos = db.get_tsm_approval_msos()

        if len(msos) > 0:
            return render_template('approve.html', msos=msos, current_user=current_user())
        else:
            msg = 'No Pending MSO\'s for Approval.'
            return render_template('all_mso.html', msg=msg, current_user=current_user())

    elif (current_user()['job_title'] == 'supervisor' and current_user()['department'] == 'COMNAV'):
        msos = db.get_tss_approval_msos()

        if len(msos) > 0:
            return render_template('approve.html', msos=msos, current_user=current_user())
        else:
            msg = 'No Pending MSO\'s for Approval.'
            return render_template('all_mso.html', msg=msg, current_user=current_user())
    else:
        msg = 'Only TSM or TSS can approve MSO\'s'
        return render_template('not_authorized.html', msg=msg, current_user=current_user())


# Approve MSO through AJAX request.
@app.route('/approve_mso/<string:id>')
@is_logged_in
def approve_mso(id):
    id = id.replace('MSO-', '')
    if (current_user()['job_title'] == 'department_head'):
        # Update the MSO in the database
        sql = "UPDATE tsd_mso_form  SET tsm_approval=%s, tsm_approval_date=CURRENT_TIMESTAMP WHERE id=%s"
        data = (1, id)
        db.update_mso(sql, data)

        return 'nothing'
    elif (current_user()['job_title'] == 'supervisor'):
        # Update the MSO in the database
        sql = "UPDATE tsd_mso_form  SET supervisor_approval=%s, supervisor_approval_date=CURRENT_TIMESTAMP WHERE id=%s"
        data = (1, id)
        db.update_mso(sql, data)

        return 'nothing'

    else:
        pass

# MSO's by the given user
@app.route('/my_msos')
@is_logged_in
def my_msos():
    user_info = current_user()
    user = user_info['first_name'] + ' ' + user_info['last_name']
    # Get MSO's
    msos = db.all_msos_by_user(user)

    if len(msos) > 0:
        return render_template('my_msos.html', msos=msos, current_user=user_info)
    else:
        msg = 'No MSO\'s Found'
        return render_template('my_msos.html', msg=msg, current_user=user_info)

# MSO's requested by other departments and the given user
@app.route('/mso_requests')
@is_logged_in
def mso_requests():
    return 'mso requests'


if __name__ == "__main__":
    app.run()
