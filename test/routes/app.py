from flask import Flask, jsonify, render_template, request, send_file
import pdfkit
import os
import sqlite3
import re
#from db import create_tables
import subprocess
from datetime import datetime
import requests

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/uploads'

#CVE API
OPENCVE_API_URL = "https://www.opencve.io/api/vendors/zimbra/cve"
USERNAME = "amenpfe"
PASSWORD = "Fafani123;"
RESULTS_PER_PAGE = 10  # Number of results to display per page

@app.route("/cve",methods=['GET'])
def get_cve_data():
    try:
        page = request.args.get("page", default=1, type=int)
        
        # Calculate offset for pagination
        offset = (page - 1) * RESULTS_PER_PAGE

        # Make a GET request to the OpenCVE API with Basic Authentication
        response = requests.get(OPENCVE_API_URL, params={"limit": RESULTS_PER_PAGE, "offset": offset}, auth=(USERNAME, PASSWORD))

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            cve_entries = response.json()

            return render_template("cve.html", cve_entries=cve_entries, page=page)
        else:
            # Return an error message if the request was not successful
            return jsonify({"error": "Failed to fetch CVE data"}), response.status_code

    except Exception as e:
        # Handle any exceptions that occur during the request
        return jsonify({"error": str(e)}), 500













"""
@app.before_first_request
def before_first_request_func():
    create_tables()
"""
@app.route('/history',methods=['GET'])
def home2():
    return render_template("history.html")




@app.route('/zimbra-form',methods=['GET','POST'])
def zimbra():
    if request.method == 'POST':
        outputs=[]
        domain = request.form.get('domain')
        email= request.form.get('email')
        if request.form.get('dkim'):
            dkim=request.form.get('dkim')
        if 'spam' in request.form :
            output = subprocess.check_output(['python3','scripts/spam.py', domain, email])
            output = output.decode('utf-8').replace('\n', '<br>')
            output=  ansi_to_html(output)  
            outputs.append(('Email Spam',output))
        if 'check' in request.form :
            output = subprocess.check_output(['python3','scripts/check_domain.py', '-d', domain,'-v'])
            output = output.decode('utf-8').replace('\n', '<br>')
            output=  ansi_to_html(output)  
            outputs.append(('',output))
        if 'bruteforce' in request.form :
            output = subprocess.check_output(['python3','scripts/spam.py', '-d', 'google.com'])
            output = output.decode('utf-8').replace('\n', '<br>')
            output=  ansi_to_html(output)  
            outputs.append(('Email Spam',output))
        if 'capabilities' in request.form :
            output = subprocess.check_output(['nmap','--script', 'imap-capabilities', '-p','143',domain])
            output = output.decode('utf-8').replace('\n', '<br>')
            output += subprocess.check_output(['nmap','--script', 'pop3-capabilities', '-p','110',domain]).decode().replace('\n', '<br>')
            output=  ansi_to_html(output)  
            outputs.append(('Imap/pop3 capabilities',output))
        if 'spoof' in request.form :
            output = subprocess.check_output(['python3','scripts/magicspoofmail.py', '-d', domain,'-t','-e',email,'-s',domain])
            output = output.decode('utf-8').replace('\n', '<br>')
            output=  ansi_to_html(output)  
            outputs.append(('Spoof',output))





        #output1 = subprocess.check_output(['python3','scripts/magicspoofmail.py', '-d', 'google.com'])
        # output2 = subprocess.check_output(['python', '', ip, port])

        # Execute shell commands
        # output3 = subprocess.check_output(['nmap', '-p', port, ip])
        #output2 = subprocess.check_output(['ping', '-c','4',ip]) 

        
        #output1 = output1.decode('utf-8').replace('\n', '<br>')
        #output1=ansi_to_html(output1)
        #output2 = output2.decode('utf-8').replace('\n', '<br>')
        
        # Generate PDF
        
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  #
        filename = f'{domain}_{current_time}.pdf'  
        html_output = ''
        for title, output in outputs:
            html_output += f'<h1>{title}</h1><p>{output}</p>'
        pdfkit.from_string(html_output, filename)

        return send_file(filename, as_attachment=True)
    return render_template('index.html')






@app.route('/', methods=['GET'])
def home():
 
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)




def parse_mail(output):
    # Define the pattern
    pattern = r'mail\..*?\..*?'

    
    match = re.search(pattern, output)

    
    if match:
        return match.group()

    
    return ''
def ansi_to_html(text):
    
    colors = {
        '0;30': 'black',
        '0;31': 'red',
        '0;32': 'green',
        '0;33': 'yellow',
        '0;34': 'blue',
        '0;35': 'magenta',
        '0;36': 'cyan',
        '0;37': 'black',  
        '1;30': 'black',
        '1;31': 'red',
        '1;32': 'green',
        '1;33': 'yellow',
        '1;34': 'blue',
        '1;35': 'magenta',
        '1;36': 'cyan',
        '1;37': 'black',  
    }

    
    for ansi, html in colors.items():
        text = re.sub('\x1B\[' + ansi + 'm', '<span style="color: ' + html + '">', text)

    
    text = re.sub('\x1B\[00m', '', text)
    text = re.sub('\x1B\[40m', '', text)

    return text