from flask import render_template, request
from app.cve import bp
import requests
from flask_login import login_required, current_user


OPENCVE_API_URL = "https://www.opencve.io/api/vendors/zimbra/cve"
USERNAME = "amenpfe"
PASSWORD = "Fafani123;"
RESULTS_PER_PAGE = 5 

@bp.route('/',methods=['GET'])
@login_required
def index():
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

            return render_template("cve/index.html", cve_entries=cve_entries, page=page)
        else:
            # Return an error message if the request was not successful
            return jsonify({"error": "Failed to fetch CVE data"}), response.status_code

    except Exception as e:
        # Handle any exceptions that occur during the request
        return jsonify({"error": str(e)}), 500


    return render_template('cve/index.html')

