import json
import sys
import os
from os import path
from datetime import timedelta
from client.ocrclient import *
from client.parsedata import *
from flask import Flask, request, render_template, session, redirect, url_for, jsonify, Markup
from flask.ext import excel
import numpy as np

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def validate_user():
    if request.method == "POST":
        user_name = request.form["username"]
        password = request.form["password"]
        protocol_no = request.form["protocol_no"]
        status, content = validate_protocol(user_name, password, protocol_no)
        if status != 200:
            return render_template('index.html',
                                   error="There was an error with your protocol no/username/password combination. Please try again.")
        decode_json = content.decode('utf8').replace("'", '"')
        data = json.loads(decode_json)
        if 'error' in data:
            return render_template('index.html',
                                   error=data['error'])
        if 'accrual_info_only' in data and not data["accrual_info_only"]:
            return render_template('index.html',
                                   error="Summary accrual is set to 'No' for the provided protocol. Please try another protocol.")
        session["user"] = user_name
        session["protocol"] = protocol_no
        session["title"] = data["title"]

        return redirect(url_for("user_home", user_name=user_name, protocol_no=protocol_no))
    if 'user' in session:
        return redirect(url_for("user_home", user_name=session.get('user'), protocol_no=session.get('protocol')))
    return render_template('index.html')


@app.route("/about", methods=['GET'])
def about():
    return render_template('about.html')


@app.route("/user/<user_name>/<protocol_no>")
def user_home(user_name, protocol_no):
    if "user" not in session or session["user"] is None:
        if session.get("user") != user_name:
            return redirect(url_for("validate_user"))
    return render_template("user_home.html", user_name=user_name, protocol_no=protocol_no, title=session["title"])


def get_rows(data, offset=0, per_page=10):
    l = list(data)[offset: offset + per_page]
    result = {key: data[key] for key in l}
    return result


@app.route("/logout")
def logout():
    if path.exists("results_"+session["protocol"]+"_"+session["user"]+".npy"):
        os.remove("results_"+session["protocol"]+"_"+session["user"]+".npy")
    if path.exists("store_"+session["protocol"]+"_"+session["user"]+ ".npy"):
        os.remove("store_"+session["protocol"]+"_"+session["user"]+ ".npy")
    session.clear()
    return redirect(url_for("validate_user"))


@app.route("/data/<user_name>/<protocol_no>", methods=['GET', 'POST'])
def upload_file(user_name, protocol_no):
    if request.method == 'POST':
        try:
            if 'total_accruals' in session:
                session.pop("total_accruals")
                session.pop("columns")
                session.pop("invalid_rows")
                session.pop("modified_rows")
                np.save('store_'+protocol_no+'_'+user_name+'.npy', "")

            ignore_mapping_tabs= request.form.get('ignore_mapping_tabs')

            received_data = request.get_array(field_name='file')
            if received_data is None:
                return render_template('user_home.html', user_name=user_name, protocol_no=protocol_no,
                                       error="File not received. Please upload the file before proceeding.")

            gender_data = None
            ethnicity_data = None
            race_data = None
            disease_site_data = None

            if not ignore_mapping_tabs:
                try:
                    gender_data = request.get_array(field_name='file', sheet_name="Gender")

                except:
                    return render_template('user_home.html', user_name=user_name, protocol_no=protocol_no, error="Gender mapping tab not found.")

                try:
                    ethnicity_data = request.get_array(field_name='file', sheet_name="Ethnicity")

                except:
                    return render_template('user_home.html', user_name=user_name, protocol_no=protocol_no,
                                           error="Ethnicity mapping tab not found.")

                try:
                    race_data = request.get_array(field_name='file', sheet_name="Race")

                except:
                    return render_template('user_home.html', user_name=user_name, protocol_no=protocol_no,
                                           error="Race mapping tab not found.")

                try:
                    disease_site_data = request.get_array(field_name='file', sheet_name="Disease Site")

                except:
                    return render_template('user_home.html', user_name=user_name, protocol_no=protocol_no,
                                           error="Disease site mapping tab not found.")

            modified_rows, on_study_date_missing_rows, cols, excluded_rows_dict, error = excluded_rows(received_data, gender_data, ethnicity_data, race_data, disease_site_data)

            if excluded_rows_dict is None:
                return render_template('user_home.html', user_name=user_name, protocol_no=protocol_no, error=error)

            total = len(excluded_rows_dict)

            session['columns'] = cols
            session['total_accruals'] = total
            np.save('store_'+protocol_no+'_'+user_name+'.npy', excluded_rows_dict)
            session['invalid_rows'] = on_study_date_missing_rows
            session['modified_rows'] = modified_rows

            return render_template('data.html', protocol_no=protocol_no, excluded_rows=excluded_rows_dict, columns=cols,
                                   total_rows=total, on_study_date_missing_rows=on_study_date_missing_rows,
                                   modified_rows=modified_rows,
                                   user_name=user_name)
        except IOError as err:
            if 'total_accruals' in session:
                session.pop("total_accruals")
                session.pop("columns")
                session.pop("invalid_rows")
                session.pop("modified_rows")
                np.save('store_'+protocol_no+'_'+user_name+'.npy', "")
            return render_template('user_home.html', user_name=user_name, protocol_no=protocol_no,
                                   error="File not received. Please upload the file before proceeding.")
        except OSError as err:
            if 'total_accruals' in session:
                session.pop("total_accruals")
                session.pop("columns")
                session.pop("invalid_rows")
                session.pop("modified_rows")
                np.save('store_'+protocol_no+'_'+user_name+'.npy', "")
            return render_template('user_home.html', user_name=user_name, protocol_no=protocol_no,
                                   error="OS error: {0}".format(err))
        except:
            if 'total_accruals' in session:
                session.pop("total_accruals")
                session.pop("columns")
                session.pop("invalid_rows")
                session.pop("modified_rows")
                np.save('store_'+protocol_no+'_'+user_name+'.npy', "")
            return render_template('user_home.html', user_name=user_name, protocol_no=protocol_no,
                                   error="Unexpected error:" + str(sys.exc_info()))


    if ('error' in session) or ('total_accruals' in session):
        error = None
        if 'error' in session:
            error = session.get('error')
        if 'total_accruals' in session:
            # Load
            if path.exists("store_" + session["protocol"] + "_" + session["user"] + ".npy"):
                rows = np.load('store_'+protocol_no+'_'+user_name+'.npy', allow_pickle='TRUE').item()
                return render_template('data.html', protocol_no=protocol_no, excluded_rows=rows, columns=session.get('columns'),
                                       total_rows=session.get('total_accruals'), on_study_date_missing_rows=session.get('invalid_rows'),
                                       modified_rows=session.get('modified_rows'),
                                       user_name=user_name, error=error)

    return redirect(url_for("user_home", user_name=user_name, protocol_no=protocol_no))


@app.route("/summary/<user_name>/<protocol_no>", methods=['GET', 'POST'])
def parse_summary_accruals(user_name, protocol_no):
    if request.method == 'POST':
        if 'error' in session:
            session.pop('error')
            np.save('results_'+protocol_no+'_'+user_name+'.npy', '')

        if 'total_accruals' in session:
            if path.exists("store_" + session["protocol"] + "_" + session["user"] + ".npy"):
                rows = np.load('store_'+protocol_no+'_'+user_name+'.npy', allow_pickle='TRUE').item()
                total_accruals, parsed_rows = accrual_summary(rows)
                if total_accruals < 0:
                    session['error'] = 'Sorry!! We are unable to process your request' + parsed_rows
                    return redirect(url_for("upload_file", user_name=user_name, protocol_no=protocol_no))

                password = request.form["password"]
                json_data = {
                    "credentials": {"username": user_name, "password": password},
                    "protocol_no": protocol_no,
                    "total_accruals": total_accruals,
                    "accrual_data": json.loads(parsed_rows)
                }

                status, content = post_accruals(json_data)

                if status != 200:
                    error = Markup(content.decode("utf-8") )
                    session['error'] = error
                    rows = np.load('store_'+protocol_no+'_'+user_name+'.npy', allow_pickle='TRUE').item()
                    return render_template('data.html', protocol_no=protocol_no,
                                           excluded_rows=rows, columns=session.get('columns'),
                                           total_rows=session.get('total_accruals'),
                                           on_study_date_missing_rows=session.get('invalid_rows'),
                                           modified_rows=session.get('modified_rows'),
                                           user_name=user_name, error=error)

                data = json.loads(content.decode('utf8'))
                np.save('results_'+protocol_no+'_'+user_name+'.npy', data)
                session['total_accruals_imported'] = total_accruals
                return render_template('accrual_data.html', total_accruals=total_accruals, protocol_no=protocol_no,
                                       response=data, user_name=user_name)
        if 'error' in session:
            return redirect(url_for("upload_file", user_name=user_name, protocol_no=protocol_no))
    if 'total_accruals_imported' in session:
        if path.exists("results_" + session["protocol"] + "_" + session["user"] + ".npy"):
            rows = np.load('results_'+protocol_no+'_'+user_name+'.npy', allow_pickle='TRUE').item()
            return render_template('accrual_data.html', total_accruals=session.get('total_accruals_imported'),
                                    protocol_no=protocol_no, response=rows, user_name=user_name)

    return redirect(url_for("user_home", user_name=user_name, protocol_no=protocol_no))

if __name__ == '__main__':
    excel.init_excel(app)
    app.secret_key = '/'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)
    app.run(debug=True, host='0.0.0.0')
