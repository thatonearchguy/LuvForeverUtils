# LuvForeverUtils

### A collection of web-accessible utilities
These are a set of python scripts accessible over a basic Flask front end that automate mundane spreadsheet tasks.

These will eventually be turned into a Shopify extension and have periodic runs. 


### Installation
Clone this repository, then set up a venv
```
python3 -m venv .venv
```

Activate the venv

```
. .venv/bin/activate
```

Install dependencies

```
pip install -r requirements.txt
```

Make sure no applications are using port 5000:

```
sudo netstat -nlp | grep :5000
```

Run the development server

```
python app.py
```
