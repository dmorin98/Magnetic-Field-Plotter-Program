import os
import requests
import zipfile
import shutil
import subprocess
import tempfile

# Replace with your GitHub repository details
GITHUB_REPO = 'dmorin98/Magnetic-Field-Plotter-Program'
GITHUB_BRANCH = 'main'

def get_latest_commit_sha(repo, branch):
    url = f'https://api.github.com/repos/{repo}/commits/{branch}'
    response = requests.get(url)
    response.raise_for_status()
    commit_sha = response.json()['sha']
    return commit_sha

def download_latest_version(repo, branch, dest_dir):
    url = f'https://github.com/{repo}/archive/refs/heads/{branch}.zip'
    response = requests.get(url)
    response.raise_for_status()

    with tempfile.TemporaryDirectory() as tmpdirname:
        zip_path = os.path.join(tmpdirname, 'latest.zip')
        with open(zip_path, 'wb') as f:
            f.write(response.content)

        # Unzip the downloaded file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdirname)

        # Move the files from the unzipped directory to the destination directory
        unzipped_dir = os.path.join(tmpdirname, f'{repo.split("/")[1]}-{branch}')
        program_files_source = os.path.join(unzipped_dir, 'ProgramFiles')
        if os.path.exists(dest_dir):
            shutil.rmtree(dest_dir)
        shutil.move(program_files_source, dest_dir)

def run_script(script_path):
    try:
        result = subprocess.run(['python', script_path], check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running script {script_path}")
        print(e.stdout)
        print(e.stderr)
        raise

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    program_files_dir = os.path.join(current_dir, 'ProgramFiles')
    local_script_path = os.path.join(program_files_dir, 'main.py')
    
    try:
        with open(os.path.join(program_files_dir, 'commit_sha.txt'), 'r') as f:
            local_commit_sha = f.read().strip()
    except FileNotFoundError:
        local_commit_sha = ''

    latest_commit_sha = get_latest_commit_sha(GITHUB_REPO, GITHUB_BRANCH)

    if latest_commit_sha != local_commit_sha:
        print("New version found, updating...")
        download_latest_version(GITHUB_REPO, GITHUB_BRANCH, program_files_dir)
        with open(os.path.join(program_files_dir, 'commit_sha.txt'), 'w') as f:
            f.write(latest_commit_sha)
    else:
        print("No new version found.")

    run_script(local_script_path)

if __name__ == '__main__':
    main()
