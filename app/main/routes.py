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
import sys
from gvm.connections import UnixSocketConnection
from gvm.protocols.latest import Gmp
from gvm.transforms import EtreeCheckCommandTransform
from PyPDF2 import PdfReader, PdfWriter
from lxml import etree
import base64
import gvm.protocols.gmpv208
@bp.route('/',methods=['GET'])
@login_required
def index():
    return  render_template('index.html')


@bp.route('/zimbra-form',methods=['POST'])
@login_required
def zimbra():
    if request.method == 'POST':
        check=False
        report_folder = Config.REPORT_FOLDER
        outputs=[]
        upload_folder = Config.UPLOAD_FOLDER
        smtpdomain = request.form.get('smtpDomain')
        targetdomain = request.form.get('targetdomain')
        user_internal=request.form.get('username')
        pass_internal=request.form.get('password')
        port_range=request.form.get('port')
        if request.form.get("email"):
                email=request.form.get("email")
            
        
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
        
        
        if 'spfDkimDmarc' in request.form:
            try:
                output = subprocess.check_output(['python3', 'app/scripts/check_domain.py', '-d', smtpdomain, '-v'])
                output = output.decode('utf-8').replace('\n', '<br>')
                outputs.append(('Check Domain', ansi_to_html(output)))
            except Exception as e:
                outputs.append(('Check Domain', f'Failed to execute: {e}.'))


        if 'spam' in request.form:
            try:
                output = subprocess.check_output(['python3', 'app/scripts/magicspoofmail.py', '-d', smtpdomain, '-t', '-e', email, '-s', targetdomain])
                outputs.append(('Spoof', ansi_to_html(output.decode('utf-8').replace('\n', '<br>'))))
            except Exception as e:
                outputs.append(('Spoof', f'Failed to execute: {e}.'))

        if 'webAuth' in request.form :
            try:
                if users_wordlist and pass_wordlist:
                    output = subprocess.check_output(['python3', 'app/scripts/webauth.py', 'https://'+targetdomain,users_upload,pass_upload])
                    
                if inputwordlist:
                    output = subprocess.check_output(['python3', 'app/scripts/webauth.py', 'https://'+targetdomain,users,passwords])
                output = output.decode('utf-8').replace('\n', '<br>')
                output=  ansi_to_html(output)  
                outputs.append(('WebAuth Bruteforce',output))
            except Exception as e:
                flash(f"Error Performing Bruteforce On Web Login: {e}", 'error')
        if 'protbruteforce' in request.form :
            try:
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
            except Exception as e:
                outputs.append(('Protocols Bruteforce', f'Failed to execute: {e}.'))
                

        if 'capabilities' in request.form :
            try:
                output = subprocess.check_output(['nmap','--script', 'imap-capabilities', '-p','143',targetdomain])
                output = output.decode('utf-8').replace('\n', '<br>')
                output += subprocess.check_output(['nmap','--script', 'pop3-capabilities', '-p','110',targetdomain]).decode().replace('\n', '<br>')
                output=  ansi_to_html(output)  
                outputs.append(('Imap/pop3 capabilities',output))
            except Exception as e :
                outputs.append(('Imap/pop3 capabilities', f'Failed to execute: {e}.'))
        
        if 'scanner' in request.form :
            try:
                path = None
                connection = UnixSocketConnection(path=path)
                transform = EtreeCheckCommandTransform()
                  
                credential_id = '9afe1aea-538f-49df-8923-2bd46ec605e8'
                with Gmp(connection=connection, transform=transform) as gmp:
                                            
                    gmp.authenticate('admin', 'eb01050e-87f5-4ab1-bbf8-597b6f4b5b3e')
                    
                    myTest = gvm.protocols.gmpv208.AliveTest('Consider Alive')
                    response = gmp.create_target(
                    name=smtpdomain,
                    hosts=[targetdomain],
                    port_range=port_range,
                    alive_test=myTest
                    )
                    target_id = response.get('id')
                    response = gmp.create_task(name=smtpdomain, config_id="daba56c8-73ec-11df-a475-002264764cea", target_id=target_id, scanner_id="08b69003-5fc2-4037-a479-93b440211c73")
                    task = response.get('id')
                    
                    
                    gmp.start_task(task)
                    response = gmp.get_task(task)
                    report_element = response.find('.//current_report/report')
                    report_id = report_element.get('id')
                    print("Report ID:", report_id)
                    
                                   
                    while True:
                        response = gmp.get_task(task)
                        status_element = response.find('.//status')
                        status_text = status_element.text
                        
                        
                        if status_text== 'Done':
                            
                            break
                            
                    
                    
                    report = gmp.get_report(report_id, report_format_id="c402cc3e-b531-11e1-9163-406186ea4fc5")
                    xml_str = etree.tostring(report, pretty_print=True).decode('utf-8')
                    if report :
                        check=True
                    
                    

                    download_pdf_from_xml(xml_str)
            except Exception as e :
                outputs.append(('Openvas', f'Failed to execute: {e}.'))

        if 'enumeration' in request.form :
            try:

                if users_wordlist and pass_wordlist:
                    output = subprocess.check_output(['smtp-user-enum','-U',users_upload ,'-t',targetdomain,'-v','-D',smtpdomain])
                if inputwordlist:
                    output = subprocess.check_output(['smtp-user-enum','-U',users ,'-t',targetdomain,'-v','-D',smtpdomain])
                output = output.decode('utf-8').replace('\n', '<br>')
                output=  ansi_to_html(output)  
                outputs.append(('Smtp Enumeration',output))
            except Exception as e :
                outputs.append(('Enumeration', f'Failed to execute: {e}.'))

        if 'internal' in request.form :
            try:
                output = subprocess.check_output(['python3','app/scripts/spoof/spoof.py', 'cli','--host' ,targetdomain,'--port','587','--username',user_internal,'--password',pass_internal,'--sender','spoof@test.com','--name','test_internal_spoof','--recipients',email,'--subject','test_internal_spoof','--filename','app/scripts/spoof/example.html'])
                output = output.decode('utf-8').replace('\n', '<br>')
                output=  ansi_to_html(output)  
                outputs.append(('Internal Spoof',output))
            except Exception as e:
                    outputs.append(('Internal Spoof', f'Failed to execute: {e}.'))
        if 'relay' in request.form :
            try:
                output=subprocess.check_output(['nmap','--script','smtp-open-relay',targetdomain,'-p25,465,587'])
                output=output.decode('utf-8').replace('\n','<br>')
                output= ansi_to_html(output)
                outputs.append(('Open Relay',output))
            except Exception as e:
                outputs.append(('Open Relay', f'Failed to execute: {e}.'))


        current_time = datetime.now().strftime("%Y-%m-%d")  
        filename = f'{smtpdomain}_{current_time}.pdf' 
        save_path = os.path.join(report_folder, filename)
        if outputs:
            
             
            
            html_output = ''
            for title, output in outputs:
                html_output += f'<h1>{title}</h1><p>{output}</p>'
           
            
            pdfkit.from_string(html_output, save_path)
            final_report=save_path
            new_report = Report(name=smtpdomain, date=datetime.now(), analyst=current_user.username,pdf_data=html_output)
            db.session.add(new_report)
        else:
            flash(f"Empty Form", 'error')
        if check and outputs :
                
                final_report=os.path.join(report_folder, 'final_report.pdf')
                merge_pdfs([save_path, os.path.join(report_folder, f'openvas_{current_time}.pdf')], final_report)
        elif check and not outputs:
            final_report= os.path.join(report_folder, 'openvas.pdf')
        try:
                
                db.session.commit()
                
        except Exception as e:
                db.session.rollback()
               
        return send_file(final_report, as_attachment=True)
        

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

def download_pdf_from_xml(xml_data):
        # Parse the XML
        root = etree.fromstring(xml_data)
        report_folder = Config.REPORT_FOLDER
        # Attempt to extract the base64-encoded PDF content
        try:
            encoded_pdf = root.xpath('//report/text()')[0]
            pdf_data = base64.b64decode(encoded_pdf)
        except IndexError:
            print("Failed to locate PDF data in the XML.")
            return
        except base64.binascii.Error as e:
            print(f"Error decoding base64 content: {e}")
            return

        current_time = datetime.now().strftime("%Y-%m-%d")  
         
        pdf_file_path = os.path.join(report_folder, f'openvas_{current_time}.pdf')
        with open(pdf_file_path, 'wb') as file:
            file.write(pdf_data)
        
def merge_pdfs(paths, output_path):
    pdf_writer = PdfWriter()
    
    for path in paths:
        if path :
            pdf_reader = PdfReader(path)
            for page in range(len(pdf_reader.pages)):
                pdf_writer.add_page(pdf_reader.pages[page])

    with open(output_path, 'wb') as out:
        pdf_writer.write(out)
        