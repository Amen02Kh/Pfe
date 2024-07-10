from flask import render_template, request,jsonify,json
from app.cve import bp
import requests
from flask_login import login_required, current_user
import os 
import subprocess
import shutil
from config import Config

OPENCVE_API_URL = "https://www.opencve.io/api/vendors/zimbra/cve"
USERNAME = "amenpfe"
PASSWORD = "Fafani123;"
RESULTS_PER_PAGE = 5 

@bp.route('/',methods=['GET'])
@login_required
def index():
    try:
        page = request.args.get("page", default=1, type=int)
        offset = (page - 1) * RESULTS_PER_PAGE

        # Make a GET request to the OpenCVE API with Basic Authentication
        response = requests.get(OPENCVE_API_URL, params={"limit": RESULTS_PER_PAGE, "offset": offset}, auth=(USERNAME, PASSWORD))

        # Check if the request was successful
        if response.status_code == 200:
            cve_entries = response.json()
            i=0
            for entry in cve_entries :
               
               #entry['has_executable'] = check_executability(entry['id'])
               entry['has_executable'] = True
              
            return render_template("cve/index.html", cve_entries=cve_entries, page=page)
        else:
            # Return an error message if the request failed
            return jsonify({"error": "Failed to fetch CVE data"}), response.status_code

    except Exception as e:
        # Handle exceptions that occur during the request
        return jsonify({"error": str(e)}), 500

    
def check_executability(cve_id):
    try:
        result = subprocess.run(['searchsploit', cve_id, '--json'], capture_output=True, text=True)
        data = json.loads(result.stdout)
        # Check if the results contain any executable content
        return any("exploit" in entry['Title'].lower() for entry in data['RESULTS_EXPLOIT'])
    except Exception as e:
        print(f"Error checking executability: {str(e)}")
        return False


@bp.route('/execute_cve/<cve_id>', methods=['GET', 'POST'])
@login_required
def execute_cve(cve_id):
    #exploit_path = get_exploit(cve_id)
    exploit_path="/usr/share/exploitdb/exploits/php/webapps/38436.txt"
    base_exploit_script = ""
    output = ""
    upload_folder = Config.UPLOAD_FOLDER

    # Create a copy of the exploit file for the user to edit
    temp_exploit_path = os.path.join(upload_folder, "exploit.sh")

    if request.method == 'POST':
        # Get the edited exploit from the form
        edited_exploit = request.form.get('exploit').replace('\r\n', '\n')
        
        # Write the edited exploit back to a new copy of the exploit file
        with open(temp_exploit_path, 'w') as file:
            file.write(edited_exploit)
        
        
        try:
            os.chmod(temp_exploit_path, os.stat(temp_exploit_path).st_mode | 0o111)
            # Ensure that the command is correct
            res = subprocess.check_output([temp_exploit_path],text=True)
            output = res  # As you have `text=True`, stdout is directly returned as a string
            
        except subprocess.CalledProcessError as e:
            
            return render_template('cve/run_exploit.html', exploit=edited_exploit, output="Error", cve_id=cve_id)
        except Exception as e:
            return render_template('cve/run_exploit.html', exploit=edited_exploit, output="Error", cve_id=cve_id)
        # Load the edited script for possible further editing
        exploit_script = edited_exploit
    else:
        # If it's a GET request, make a temporary copy of the exploit script for initial editing
          # Check if the temporary file already exists
        shutil.copy(exploit_path, temp_exploit_path)
        with open(temp_exploit_path, 'r') as file:
            exploit_script = file.read()

    return render_template('cve/run_exploit.html', exploit=exploit_script, output=output, cve_id=cve_id)

def get_exploit(cve_id):
    try:    
        # Run the searchsploit command and capture the output
        print("searching")
        result = subprocess.run(['searchsploit', cve_id, '--json'], capture_output=True, text=True)
        data = json.loads(result.stdout)
        
        # Check if the results contain any executable content
        exploits = [entry for entry in data['RESULTS_EXPLOIT'] if "exploit" in entry['Title'].lower()]

        if exploits:
            return exploits[0]['Path']
    except Exception as e:
        print(f"Error getting exploit: {str(e)}")