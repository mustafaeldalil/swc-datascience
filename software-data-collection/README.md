# Software Club - Scrapping

## Introduction
This repository aims at : 
- Launch linkedin scrapping via Phantombuster and synchronize result to airtables
- Scrap companies webpage and use GPT to answer questions about them 

Here is the architecture and workflow : 
https://docs.google.com/presentation/d/1uUGVTD6911Nyh73JMiItIhQLm-ERY3FgopnM8UNSz30/edit?usp=sharing

## Installation
We use python 3.10 and Django Rest API to perform this process. 
1. Create and activate virtual environment
```
virtualenv .venv -p python3`
source .venv/bin/activate
```
2. Install requirements
```
pip install -r requirements.txt
```
3. Create environment file into the api/ folder:
`.env` (on .env-default model)
4. Copy the google api credentials
`software-google-api-key.json` into the api/api/ folder
4. Add encoding model
To do this, create a models/ fodler wherever you want and clone the all-mpnet-base-v2 repo (https://huggingface.co/sentence-transformers/all-mpnet-base-v2) using 
```
git lfs install 
git clone https://huggingface.co/sentence-transformers/all-mpnet-base-v2
```
On mac if you encounter an error saying that git lfs is not available, run `brew install git-lfs` 
Then update the .env variable `SIMILARITY_MODEL_PATH` with the model path
6. Launch process via 
```
python manage.py runserver
```
7. Launch asynchronous celery tasks via 
```
celery -A api worker -Q software_default -l info
```
and 
```
celery -A api worker -Q software_slow -l info
```

## Test it
First to launch a celery asynchronous tasks (let's say for example the planify scrapping tasks), you can run 
```
python manage.py shell
```
```
from company.tasks import planify_scrap_companies_website
planify_scrap_companies_website.delay()
```
This will connect to airtable table (depending on your env variables) and launch scrapping for all companies not scrapped.
You can have access to scheduled tasks in the file 
```
api/celery.py
```

Then, if you want Phantombuster to send the result to your local machine instead of production server, you can use localtunnel
Install it : `npm install -g localtunnel`
Then launch it on the port your webserver is running on `lt --port 8000`

You wil have and address, you can modify the webhook address in phantombuster by using this domain. Phantombuster will send results to your local machine.

## Deployment
The server is on OVH (ubuntu). To deploy, you need to have access to this server with a "username" and a "password". Once you get it, copy your ssh key by running : 
```
ssh-copy-id <username>@<IP>
```
Try to log to the server by running : `ssh <username>@<IP>`

Then go back to your git folder and run : 
```
git remote add production <username>@<IP>:software-data-project.git
```
Then once you have commited change, you can deploy to production by running 
```
git push production master
```
