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

        # Gather the Username, Password and Protocol Number from the HTML form
        user_name = request.form["username"]
        password = request.form["password"]
        protocol_no = request.form["protocol_no"]

        # Check to see if the Protocol Number is Valid and if the Username has access to the Protocol Number
        # Saves the content from the validation. The content will have sections for 'accrual_info_only', 'protocol_no', and 'title'
        status, content = validate_protocol(user_name, password, protocol_no)

        # If the Protocol Validation was unsuccessful alert the user that there was a problem
        if status != 200:
            return render_template('index.html',
                                   error="There was an error with your protocol no/username/password combination. Please try again.")

        # Format the content returned from the Protocol Validation to JSON
        decode_json = content.decode('utf8').replace("'", '"')
        data = json.loads(decode_json)

        # Runs if content could not be formatted as JSON
        if 'error' in data:
            return render_template('index.html',
                                   error=data['error'])

        # Checks to see if the Protocol Number provided allows for Summary Accrual
        if 'accrual_info_only' in data and not data["accrual_info_only"]:
            return render_template('index.html',
                                   error="Summary accrual is set to 'No' for the provided protocol. Please try another protocol.")

        # Stores the Username, protocol, and title in the Session
        session["user"] = user_name
        session["protocol"] = protocol_no
        session["title"] = data["title"]

        # Passes the Username and Protocol Number to the user_home function located at endpoint
        # "/user/<user_name>/<protocol_no>"
        return redirect(url_for("user_home", user_name=user_name, protocol_no=protocol_no))

    # If there is an active session pull the information from the stored session data instead of prompting the user
    if 'user' in session:
        # Passes the Username and Protocol Number to the user_home function located at endpoint
        # "/user/<user_name>/<protocol_no>"
        return redirect(url_for("user_home", user_name=session.get('user'), protocol_no=session.get('protocol')))

    # Loads the index.html when the page is first loaded and there is no active session
    # index.html will prompt the user to enter Username, Password, and Protocol Number
    return render_template('index.html')


@app.route("/about", methods=['GET'])
def about():
    # Loads the about.html when the page is loaded
    # about.html does not prompt the user for any information
    return render_template('about.html')


@app.route("/user/<user_name>/<protocol_no>")
def user_home(user_name, protocol_no):

    # Runs if there is no value for user in the session or the value for user in the session is null
    if "user" not in session or session["user"] is None:
        # Runs if the value in the session for user is not equal to the user_name value passed into the function
        if session.get("user") != user_name:
            # Calls the validate_user function located at endpoint "/"
            return redirect(url_for("validate_user"))

    # Loads the user_home.html when the page is first loaded and there is an active session
    # user_home.html will prompt the user to upload an Excel document and select an Ignore Mapping Tabs value
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

            # Get the user provided value for ignore_mapping_tabs from user_home.html
            ignore_mapping_tabs= request.form.get('ignore_mapping_tabs')

            # Open the Excel document the user uploaded and parse it to get an two dimensional array
            # Each row in the Excel document is an array
            received_data = request.get_array(field_name='file')

            # If received_data is null prompt the user to upload an Excel document
            if received_data is None:
                return render_template('user_home.html', user_name=user_name, protocol_no=protocol_no,
                                       error="File not received. Please upload the file before proceeding.")

            # Initialize the OnCore Mappings to Null
            gender_data = None
            ethnicity_data = None
            race_data = None
            disease_site_data = None

            # Runs if the user provided custom mapping tabs in the Gender, Ethnicity, Race, Disease Site Excel sheets
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

            # excluded_rows function is located in parsedata.py
            # excluded_rows takes in the data from the Excel document and the Mapping Sheets. Both are passed as arrays
            #
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
