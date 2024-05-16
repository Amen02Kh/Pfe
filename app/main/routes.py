from app.main import bp
from app.extensions import db
from app.models.report import Report
from config import Config
from flask import render_template,request,send_file,current_app,flash,redirect,url_for
from flask_login import login_required, current_user
import pdfkit
import os
import re
import subprocess
from datetime import datetime
import requests
from werkzeug.utils import secure_filename

@bp.route('/',methods=['GET'])
@login_required
def index():
    return  render_template('index.html')


@bp.route('/zimbra-form',methods=['POST'])
@login_required
def zimbra():
    if request.method == 'POST':

        outputs=[]
        upload_folder = Config.UPLOAD_FOLDER
        smtpdomain = request.form.get('smtpDomain')
        print(smtpdomain)
        users_wordlist = request.files.get('usernamesWordlist')
        if users_wordlist and users_wordlist.filename != '':
            
            save_path = os.path.join(upload_folder, "users_upload.txt")
            users_wordlist.save(save_path)
            users_upload=save_path


        pass_wordlist = request.files.get('passwordsWordlist')
        if pass_wordlist and pass_wordlist.filename != '':
            save_path = os.path.join(upload_folder, "password_upload.txt")
            pass_wordlist.save(save_path)
            pass_upload=save_path
        inputwordlist=request.form.get('inputwordlist')
        if inputwordlist:
            users = []
            passwords = []
            for entry in inputwordlist.split('\n'):
              if ':' in entry:
                user, passw = entry.split(':', 1)
                users.append(user.strip())
                passwords.append(passw.strip())
        
            save_path = os.path.join(upload_folder, 'users.txt')
            with open(save_path, 'w') as f_users:
                f_users.write('\n'.join(users))
            users=save_path
            save_path = os.path.join(upload_folder, 'passwords.txt')
            with open(save_path, 'w') as f_passwords:
                f_passwords.write('\n'.join(passwords))            
            passwords=save_path
        
        
        if 'spfDkimDmarc' in request.form :
            print("in")
            if request.form.get('dkim'):
                dkim=request.form.get('dkim')
            output = subprocess.check_output(['python3','scripts/check_domain.py', '-d', smtpdomain,'-v'])
            output = output.decode('utf-8').replace('\n', '<br>')
            output=  ansi_to_html(output)  
            print(output)
            outputs.append(('Check Domain',output))

        if 'spam' in request.form :
            if request.form.get("email"):
                email=request.form.get("email")
            output = subprocess.check_output(['python3','app/scripts/magicspoofmail.py', '-d', smtpdomain,'-t','-e',email,'-s',smtpdomain])
            output = output.decode('utf-8').replace('\n', '<br>')
            output=  ansi_to_html(output)  
            outputs.append(('Spoof',output))

        if 'webAuth' in request.form :
            targetdomain = request.form.get('targetdomain')
            if users_wordlist and pass_wordlist:
                
                #output = subprocess.check_output(['hydra','-L',users_upload ,'-P',pass_upload,targetdomain,'https-post-form "/:username=^USER^&password=^PASS^:The username or password is incorrect. Verify that CAPS LOCK is not on, and then retype the current username and password."'])
                output = subprocess.check_output([
                        'hydra', 
                        '-L', users, 
                        '-P', passwords, 
                        targetdomain, 
                        'https-post-form', 
                        '"/:username=^USER^&password=^PASS^:The username or password is incorrect. Verify that CAPS LOCK is not on, and then retype the current username and password."'
                        ])

            if inputwordlist:
                output = subprocess.check_output(['hydra','-L',users ,'-P',passwords,targetdomain,'https-post-form "/:username=^USER^&password=^PASS^:The username or password is incorrect. Verify that CAPS LOCK is not on, and then retype the current username and password."'])
            output = output.decode('utf-8').replace('\n', '<br>')
            output=  ansi_to_html(output)  
            outputs.append(('WebAuth Bruteforce',output))

        if 'bruteforce' in request.form :
            targetdomain = request.form.get('targetdomain')
            if users_wordlist and pass_wordlist:
                output = subprocess.check_output(['hydra','-L',users_upload ,'-P',pass_upload,targetdomain,'smtp']).decode('utf-8').replace('\n', '<br>')
                output1 = subprocess.check_output(['hydra','-L',users_upload ,'-P',pass_upload,targetdomain,'imap']).decode('utf-8').replace('\n', '<br>')
                output2 = subprocess.check_output(['hydra','-L',users_upload ,'-P',pass_upload,targetdomain,'pop3']).decode('utf-8').replace('\n', '<br>')
            if inputwordlist:
                output = subprocess.check_output(['hydra','-L',users ,'-P',passwords,'-s','25',targetdomain,'smtp']).decode('utf-8').replace('\n', '<br>')
                output1 = subprocess.check_output(['hydra','-L',users ,'-P',passwords,targetdomain,'imap']).decode('utf-8').replace('\n', '<br>')
                output2 = subprocess.check_output(['hydra','-L',users ,'-P',passwords,targetdomain,'pop3']).decode('utf-8').replace('\n', '<br>')
            
            output=  ansi_to_html(output)  
            output1=  ansi_to_html(output1) 
            output2=  ansi_to_html(output2) 
            output=output+'<br>'+output1+'<br>'+output2
            outputs.append(('Bruteforce',output))

        if 'capabilities' in request.form :
            output = subprocess.check_output(['nmap','--script', 'imap-capabilities', '-p','143',smtpdomain])
            output = output.decode('utf-8').replace('\n', '<br>')
            output += subprocess.check_output(['nmap','--script', 'pop3-capabilities', '-p','110',smtpdomain]).decode().replace('\n', '<br>')
            output=  ansi_to_html(output)  
            outputs.append(('Imap/pop3 capabilities',output))
        
        if 'scanner' in request.form :
            targetdomain = request.form.get('targetdomain')
            output = subprocess.check_output(['python3','app/scripts/magicspoofmail.py', '-d', domain,'-t','-e',email,'-s',domain])
            output = output.decode('utf-8').replace('\n', '<br>')
            output=  ansi_to_html(output)  
            outputs.append(('Vulnerability Scanner',output))

        if 'enumeration' in request.form :
            if users_wordlist and pass_wordlist:
                output = subprocess.check_output(['smtp-user-enum','-U',users_upload ,'-t',smtpdomain,'-v','-D',])
            if inputwordlist:
                output = subprocess.check_output(['hydra','-U',users ,'-t',smtpdomain,'-v','-D',])
            output = output.decode('utf-8').replace('\n', '<br>')
            output=  ansi_to_html(output)  
            outputs.append(('Smtp Enumeration',output))

        if 'internal' in request.form :
            targetdomain = request.form.get('targetdomain')
            output = subprocess.check_output(['python3','scripts/magicspoofmail.py', '-d', domain,'-t','-e',email,'-s',domain])
            output = output.decode('utf-8').replace('\n', '<br>')
            output=  ansi_to_html(output)  
            outputs.append(('Internal Spoof',output))

        if 'relay' in request.form :
            output=subprocess.check_output(['nmap','--script','smtp-open-relay',smtpdomain,'-p25,465,587'])
            output=output.decode('utf-8').replace('\n','<br>')
            output= ansi_to_html(output)
            outputs.append(('Open Relay',output))

        #output1 = subprocess.check_output(['python3','scripts/magicspoofmail.py', '-d', 'google.com'])
        # output2 = subprocess.check_output(['python', '', ip, port])

        # Execute shell commands
        # output3 = subprocess.check_output(['nmap', '-p', port, ip])
        #output2 = subprocess.check_output(['ping', '-c','4',ip]) 

        
        #output1 = output1.decode('utf-8').replace('\n', '<br>')
        #output1=ansi_to_html(output1)
        #output2 = output2.decode('utf-8').replace('\n', '<br>')
        
        # Generate PDF
        report_folder = Config.REPORT_FOLDER
        current_time = datetime.now().strftime("%Y-%m-%d")  
        filename = f'{smtpdomain}_{current_time}.pdf'  
        save_path = os.path.join(report_folder, filename)
        html_output = ''
        for title, output in outputs:
            html_output += f'<h1>{title}</h1><p>{output}</p>'
       
        
        pdfkit.from_string(html_output, save_path)
        
        new_report = Report(name=smtpdomain, date=datetime.now(), analyst=current_user.username,pdf_data=html_output)
        db.session.add(new_report)
        try:
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
           
        return send_file(save_path, as_attachment=True)
    return render_template('index.html')


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