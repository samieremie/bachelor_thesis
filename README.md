# bachelor_thesis

My project for the bachelor thesis.

## How to run

**STEP 1:**  
Clone the repo locally and navigate to the folder.

**STEP 2:**  
Install the mvtec anomaly detection dataset locally. You can find it on following page.
https://www.mvtec.com/research-teaching/datasets/mvtec-ad

Note: You need to fill some information to get access to the download link.

**STEP 3:**  
Make a folder called datasets.

**STEP 4:**  
Extract the dataset you just downloaded inside of that folder.

**STEP 5:**  
Once you have downloaded the dataset you can run following commands:

```
python -m venv .venv
source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

**STEP 6:**  
Create a .env file

**STEP 7:**  
Go to OpenRouter and do all the steps to create an API key.

**STEP 8:**  
Now put the API key inside of the .env file like this:
OPENROUTER_API_KEY=hereComesTheKey

The key self starts with something like this:
sk-or-v1.....

Now you are ready to run the jupyter notebook.
