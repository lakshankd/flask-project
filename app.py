from flask import Flask, request, jsonify
import requests
import hmac
import hashlib

app = Flask(__name__)

# Configuration variables
GITHUB_SECRET = 'your_github_webhook_secret'  # Replace with your actual secret
GITHUB_TOKEN = 'your_github_token'  # Replace with your actual GitHub token


@app.route('/webhook', methods=['POST'])
def webhook():
    if GITHUB_SECRET:
        signature = request.headers.get('X-Hub-Signature-256')
        if not verify_github_signature(request.data, signature):
            return jsonify({'error': 'Invalid signature'}), 400

    data = request.json

    if data['action'] == 'opened' and 'pull_request' in data:
        pr = data['pull_request']
        pr_url = pr['url']

        # Get the code from the pull request
        pr_files_url = pr_url + '/files'
        headers = {'Authorization': f'token {GITHUB_TOKEN}'}
        response = requests.get(pr_files_url, headers=headers)

        files = response.json()
        code = ""
        for file in files:
            code += requests.get(file['raw_url']).text

        # Send code to Vertex AI
        feedback = send_code_to_vertex_ai(code)

        # Post feedback to GitHub
        post_feedback_to_github(pr['comments_url'], feedback, headers)

    return jsonify({'status': 'received'})


def verify_github_signature(payload, signature):
    expected_signature = 'sha256=' + hmac.new(GITHUB_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected_signature, signature)


def send_code_to_vertex_ai(code):
    # Replace with actual code to send data to Vertex AI
    feedback = "Code review feedback from Vertex AI"
    return feedback


def post_feedback_to_github(comments_url, feedback, headers):
    comment = {"body": feedback}
    requests.post(comments_url, json=comment, headers=headers)


if __name__ == '__main__':
    app.run(port=5000)
