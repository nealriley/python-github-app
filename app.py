from flask import Flask, request, abort
import hashlib
import hmac
import json
import requests

app = Flask(__name__)
WEBHOOK_SECRET = 'your-webhook-secret-here'  # Set your GitHub Webhook secret here

@app.route('/', methods=['GET'])
def return_status():
    return 'alive'

@app.route('/webhook', methods=['POST'])
def github_webhook():
    signature = request.headers.get('X-Hub-Signature')
    if signature is None:
        abort(400, 'Missing X-Hub-Signature')

    sha_name, signature = signature.split('=')
    if sha_name != 'sha1':
        abort(400, 'Signature must be sha1')

    mac = hmac.new(WEBHOOK_SECRET.encode(), msg=request.data, digestmod='sha1')
    if not hmac.compare_digest(str(mac.hexdigest()), str(signature)):
        abort(400, 'Invalid signature')

    payload = request.get_json()
    if payload['action'] == 'push':
        repo = payload['repository']['full_name']
        commit_sha = payload['after']
        api_url = f'https://api.github.com/repos/{repo}/commits/{commit_sha}'
        headers = {'Authorization': 'token your-github-access-token-here'}

        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            commit_data = response.json()
            changed_files = [file['filename'] for file in commit_data['files']]
            print(f'Changed files: {changed_files}')
        else:
            print(f'Failed to retrieve commit data: {response.status_code}')

    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
