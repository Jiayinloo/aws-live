from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def employee():
    # return render_template('AddEmp.html')
    return render_template('employee.html')



@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')


@app.route("/", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    position = request.form['position']
    salary = request.form['salary']
    ot = request.form['ot']
    email = request.form['email']
    phone = request.form['phone']
    emp_image_file = request.files['emp_image_file']
    emp_resume = request.files['emp_resume']
    emp_certificate = request.files['emp_certificate']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %d, %d, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    if emp_resume == "":
        return "Please select a file"
    
    if emp_certificate == "":
        return "Please select a file"
    
    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, position, salary, ot, email, phone))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        emp_resume_name_in_s3 = "emp-id-" + str(emp_id) + "_resume"
        emp_certificate_name_in_s3 = "emp-id-" + str(emp_id) + "_certificate"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            s3.Bucket(custombucket).put_object(Key=emp_resume_name_in_s3, Body=emp_resume)
            s3.Bucket(custombucket).put_object(Key=emp_certificate_name_in_s3, Body=emp_certificate)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3,
                emp_resume_name_in_s3,
                emp_certificate_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
