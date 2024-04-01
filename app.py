from flask import Flask, render_template, request, send_file
import pdfkit
import os
import subprocess
from datetime import datetime
import re
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        ip = request.form.get('ip')
        port = request.form.get('port')

        
        output1 = subprocess.check_output(['python3','scripts/magicspoofmail.py', '-d', 'google.com'])
        # output2 = subprocess.check_output(['python', '', ip, port])

        # Execute shell commands
        # output3 = subprocess.check_output(['nmap', '-p', port, ip])
        output2 = subprocess.check_output(['ping', '-c','4',ip]) 

        
        output1 = output1.decode('utf-8').replace('\n', '<br>')
        output1=ansi_to_html(output1)
        output2 = output2.decode('utf-8').replace('\n', '<br>')
        outputs = [
             ('Output of script 1', output1),
            # ('Output of script 2', output2),
            # ('Output of nmap command', output3),
            ('Output of ping command', output2),
        ]
        # Generate PDF
        
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  #
        filename = f'{ip}_{current_time}.pdf'  
        html_output = ''
        for title, output in outputs:
            html_output += f'<h1>{title}</h1><p>{output}</p>'
        pdfkit.from_string(html_output, filename)

        return send_file(filename, as_attachment=True)

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