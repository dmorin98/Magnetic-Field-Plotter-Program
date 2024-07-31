import os
import requests
import zipfile
import shutil
import subprocess

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
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    url = f'https://github.com/{repo}/archive/refs/heads/{branch}.zip'
    response = requests.get(url)
    response.raise_for_status()
    zip_path = os.path.join(dest_dir, 'latest.zip')
    with open(zip_path, 'wb') as f:
        f.write(response.content)

    # Unzip the downloaded file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(dest_dir)
    
    os.remove(zip_path)  # Remove the zip file after extracting

    # Move the files from the unzipped directory to the destination directory
    unzipped_dir = os.path.join(dest_dir, f'{repo.split("/")[1]}-{branch}')
    for filename in os.listdir(unzipped_dir):
        src_file = os.path.join(unzipped_dir, filename)
        dest_file = os.path.join(dest_dir, filename)
        if os.path.isfile(src_file):
            os.replace(src_file, dest_file)
        elif os.path.isdir(src_file):
            if os.path.exists(dest_file):
                shutil.rmtree(dest_file)
            shutil.move(src_file, dest_file)

def run_script(script_path):
    subprocess.run(['python', script_path], check=True)

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    local_script_path = os.path.join(current_dir, 'main.py')
    local_script_dir = current_dir

    try:
        with open(os.path.join(local_script_dir, 'commit_sha.txt'), 'r') as f:
            local_commit_sha = f.read().strip()
    except FileNotFoundError:
        local_commit_sha = ''

    latest_commit_sha = get_latest_commit_sha(GITHUB_REPO, GITHUB_BRANCH)

    if latest_commit_sha != local_commit_sha:
        print("New version found, updating...")
        download_latest_version(GITHUB_REPO, GITHUB_BRANCH, local_script_dir)
        with open(os.path.join(local_script_dir, 'commit_sha.txt'), 'w') as f:
            f.write(latest_commit_sha)
    else:
        print("No new version found.")

    run_script(local_script_path)

if __name__ == '__main__':
    main()
