from flask import Flask, request, jsonify
from github import Github
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
github = Github(GITHUB_TOKEN)

@app.route('/github/webhook', methods=['POST'])
def github_webhook():
    data = request.json
    if 'pull_request' in data:
        pr_data = data['pull_request']
        repo_full_name = data['repository']['full_name']
        pr_number = pr_data['number']

        repo = github.get_repo(repo_full_name)
        pr = repo.get_pull(pr_number)

        files = pr.get_files()
        changed_files = [file.filename for file in files]

        # Print pull request details to the console
        print(f"Pull request title: {pr.title}")
        print(f"Pull request author: {pr.user.login}")
        print(f"Pull request URL: {pr.html_url}")
        print("Changed files:")
        for file in changed_files:
            print(f"  - {file}")

        response = {
            "title": pr.title,
            "author": pr.user.login,
            "url": pr.html_url,
            "changed_files": changed_files
        }

        return jsonify(response), 200

    return jsonify({"message": "Not a pull request event"}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
