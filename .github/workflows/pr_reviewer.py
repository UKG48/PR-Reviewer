import requests
import sys
import openai
import os
import subprocess

#Reading repository variables set in github.
ACCOUNT_GITHUB_TOKEN = os.getenv('ACCOUNT_GITHUB_TOKEN')
REPO_NAME = os.getenv('REPO_NAME')
REPO_OWNER = os.getenv('REPO_OWNER')

#Reading repository secrets set in github.
SECRET_OPENAI_TOKEN = os.environ['SECRET_OPENAI_TOKEN']
SECRET_GITHUB_KEY = os.environ['SECRET_GITHUB_KEY']

#curl command to get details of the lastest pull request raised.
mycmd=subprocess.run(f'curl -v --silent https://{ACCOUNT_GITHUB_TOKEN}:x-oauth-basic@api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls 2>&1 | grep -E -w "url|head|ref|base" | head -n 12', shell=True, capture_output=True, text=True)
print(mycmd)


def chat_with_chatgpt(prompt):
    conversation = []
    conversation.append({'role':'user','content':str({prompt})})
    review = openai.ChatCompletion.create(model=model_id, messages=conversation)
    return review.choices[0].message.content

def post_review(headers, url2, chatgpt_response, fileName):
    pull_response = requests.get(url2, headers=headers)
    pr_info = pull_response.json()

    # Post review as a comment on the Github PR
    comment_url = pr_info['comments_url']
    comment_body = "Automated review using OpenAI for file {}:\n {}\n".format(fileName,chatgpt_response)
    git_response = requests.post(comment_url, headers=headers, json={'body': comment_body})
    if git_response.status_code == 201:
        print('\nReview posted successfully')
    else:
        print('\nError posting review: {}'.format(git_response.text))

def pr_review_prompt(original_file, fileName, added_changes, removed_changes):
    comment_p = f"Evalute the changes on the basis of the provided information and please help me do a brief code review. The programmimg language used is JAVA. Please check for any syntax or logical errors present in the code or if any bug risk and improvement suggestions are welcome and tell if the code is meeting the coding standards and quality. 3 variables will be provided namely originalFile, added_changes and removed_changes. originalFile will contain the current contents of the file present in the branch for which PR is being raised. added_changes will contain the changes being added to the originalFile as part of PR and removed_changes will contain the changes removed from this file. If added_changes is empty means nothing is added or if removed_changes is empty means nothing is removed from the file. Similarly if originalFile is empty it means the entire file is new. Below provided information is related to only {fileName} file."
        
    prompt = f"{comment_p} \n originalFile: {original_file} \n added_changes: {added_changes} \n removed_changes: {removed_changes}"
    return prompt

def custom_training_prompt(copyright, without_copyright, copyright_ukg, new_file):
    comment_p_1 = f"Providng you a file, you act as a copywrite checker and tell whether there is any copyright present for ukg organisation in the file Input or not"
    prompt_1 = f"{comment_p_1} \n Input: {copyright} \n Output: 'The file Input contains copyright but not for UKG organization.' \n Input: {without_copyright} \n Output: 'Your file does not have copyright. Please add copyrights before merging'\n Input: {copyright_ukg} \n Output: 'The file contains copyright for UKG organization.' \n  Input: {new_file} \n Output: "
    return prompt_1
        
#Details required for OpenAI API
openai.api_key = SECRET_OPENAI_TOKEN
model_id="gpt-3.5-turbo"

# Authenticate with Github API
headers = {'Authorization':'Token ' + SECRET_GITHUB_KEY}

#PR details
owner = f'{REPO_OWNER}'
repo = f'{REPO_NAME}'
base = mycmd.stdout.split('ref')[3].split('"')[2]
head = mycmd.stdout.split('ref')[1].split('"')[2]
pull_number = mycmd.stdout.split('url')[1].split('/')[7].split('"')[0]

#Endpoints
url1 = f'https://api.github.com/repos/{owner}/{repo}/compare/{base}...{head}'
url2 = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}"

#files for training chatgpt
file1 = open(".github/workflows/copyright_nonukg.txt","r+")
copyright = file1.read()

file2 = open(".github/workflows/without_copyright.txt","r+")
without_copyright = file2.read()

file3 = open(".github/workflows/copyright_ukg.txt","r+")
copyright_ukg = file3.read()

#PR details
pr_response = requests.get(url1, headers=headers)

if pr_response.status_code == 200:
    diffs = pr_response.json()["files"]
    for i, diff in enumerate(diffs):
        chatgpt_response = ''
        add_changes = []
        delete_changes = []
        original_file = ''
        patch = diff["patch"]
        fileName = diff["filename"]
        if(diff["status"] == 'modified' or diff["status"] == 'deleted'):
            print(f'\nModified or deleted file :{fileName}');
            url4 = f"https://raw.githubusercontent.com/{owner}/{repo}/{base}/{fileName}"
            response = requests.get(url4, headers=headers)
            original_file= response.text

            url4_newfile = f"https://raw.githubusercontent.com/{owner}/{repo}/{head}/{fileName}"
            response_newfile = requests.get(url4_newfile, headers=headers)
            new_file = response_newfile.text
        else:
            print(f'\nNew file is being added :{fileName}')
            url4_newfile = f"https://raw.githubusercontent.com/{owner}/{repo}/{head}/{fileName}"
            response_newfile = requests.get(url4_newfile, headers=headers)
            new_file = response_newfile.text  
          
        for line in patch.split('\n'):
            if line.startswith('+'):
                add_changes.append(line[1:])
            elif line.startswith('-'):
                delete_changes.append(line[1:]) 

        added_changes = '\n'.join(add_changes)
        removed_changes = '\n'.join(delete_changes)

        #Prepare data and get response from chatgpt for custom training prompt.
        prompt_trainng = custom_training_prompt(copyright, without_copyright, copyright_ukg, new_file)
        print(f"prompt_trainng: {prompt_trainng}")
        chatgpt_training_response = chat_with_chatgpt(prompt_trainng)
        print("ChatGPT Training Response:::",end='\n')
        for i in chatgpt_training_response:
            sys.stdout.write(i)
        post_review(headers, url2, chatgpt_training_response, fileName)
        
        #Prepare data and get response from chatgpt for pr review.
        prompt = pr_review_prompt(original_file, fileName, added_changes, removed_changes)
        print(f"prompt: {prompt}")
        chatgpt_response = chat_with_chatgpt(prompt)
        print("ChatGPT PR Review Response:::",end='\n')
        for i in chatgpt_response:
            sys.stdout.write(i)
        post_review(headers, url2, chatgpt_response, fileName)
        
else:
    print(f"Failed to get diff, status code: {pr_response.status_code}")