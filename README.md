<img align="center" height="400" src="https://github.com/Raghav-Bajaj/My-Programs/blob/main/pic1111.png"/>

## Introduction
- This project aims to utilize OpenAI's natural language processing capabilities to assist PR reviewers in analyzing code changes and providing feedback to developers on GitHub pull requests.

## THE IDEA - OPTIMIZE OUR WAYS OF WORKING
- A PR code review takes anywhere between 6 hours to 48 hours depending on the volume and complexity of changes
- We need a solution which can review files which are added or updated as part of a PR (as a whole and specific code that has changed) and provide review comments and recommendation for merge.

## Our Approch 
- Rely on existing OpenAI model to get a feedback on the code.
- Add custom rules and train model to catch any deviations to that rulecomments and recommendation for merge.
- Large Language Model evaluated
 - 1. Open AI (text-davinci-003 AKA GPT-3)
 - Large Language Model used
 - 1. Open AI (gpt-3.5-turbo)
 
 ## Its Impact
 - The solution will have an immediate impact by catching common problems as listed below:
   - Language specific syntactical errors
   - Adherence to coding standards
   - Provide code performance, complexity and provide suggestions to improve code style and structure
   - Provide errors and also lists suggestions to fix them
 - Custom validation can be added by training the model. Some use cases can be –
   - Check for Copyright
 - There are some solutions available in market, but we could not find a production ready solution. Also, given the fact that we would like to add customized rules, we need a customized training of the model.
- The solution can be adopted across the complete development community.

## What features in MVP 
- Review JAVA
- Custom rule to check for Copyright
- Does not reuse conversations

## Future enhancements
- Support for more programming languages
- Translate the diff of pull request into a summary that can be pasted into changelog
- Generate comments on-demand
- Notifications in Slack, per email or via a custom webhook

## How to integrate with any github repo ?
- Checkout the main branch of this repo and add **.github/workflows`** folder in any desired github repo.
- 3 repository secrets and 2 variables also need to be added in each github repo for this action to work.
 - Secrets:
	- ACCOUNT_GITHUB_TOKEN
	- SECRET_GITHUB_KEY
	- SECRET_OPENAI_TOKEN
 - Variables:
	- REPO_NAME
	- REPO_OWNER
- Once all the above changes are done, now raise a PR and the action will be triggered automatically.

## How to execute the python file locally ?
- Checkout the main branch of this repo.
- Install all the dependencies required by python project.
- The python file needs to be executed on an ubuntu platform like wsl command line.
- Command: **python3 .github/workflows/pr_reviewer.py**