# foodmeow

## Diagram

![Diagram](assets/diagram.jpeg)

## Overview & Story

Foodmeow is a spending tracker bot founded in 2020. The idea came about after I ran away from home because I have a different opinion with my parents on education. A few weeks later, my dad offered to cover some of my expenses, especially for meals.

Originally, he asked me to send him a message with each new expense and a running total. I found this process tedious. Since I was already working on another project, [CBFHSS](https://github.com/CBFHSS), and learning about software development, I was inspired to build a bot to automate this task.

Initially, Foodmeow was built with Django, used MySQL on Google Cloud SQL as its database, and was deployed on Heroku. However, due to cost, I migrated the project to MongoDB Atlas and Google Cloud Run to take advantage of their free tiers. I also switched to the lightweight Flask framework.

After gaining several years of experience in the software industry, I began refactoring the codebase to meet professional standards. This involved improving the project structure, writing cleaner code, and implementing tests. Foodmeow has evolved beyond a simple text-based CRUD app; it now features a more user-friendly experience, currency conversion capabilities, with more features planned for the future.


## Requirements

- [Python 3.11](https://www.python.org/download)
- [Flask](https://flask.palletsprojects.com/)  
- [MongoDB](https://www.mongodb.com/)
  - Create a [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) instance for free.  
- [LINE bot Python SDK](https://developers.line.biz/en/reference/)
  - Create a LINE bot from LINE Developer console.
- [currencyapi.com](https://www.currencyapi.com/)  
  - Create a new account and get API key from currencyapi.com

### Deployment

- [ngrok](https://ngrok.com/)
  - For local development.
  - Create a [ngrok](https://ngrok.com/) account and install ngrok on your computer
- [Google Cloud Run](https://cloud.google.com/run) 
  - For hosting a service.
  - Initialize a [Google Cloud](https://cloud.google.com/) service from Google account.

## How to use

### Create .env file

```shell
MONGODB_CONNECTION="" // MongoDB Link
CHANNEL_TOKEN="" // LINE Channel Token
CHANNEL_SECRET="" // LINE Channel Secret
CURRENCY_COM_API_KEY="" // currencyapi.com API Key
```

### Install `requirement.txt`

```shell
pip install -r requirements.txt
```

### Run

```shell
# Start flask app 
flask --app main run --port 3000 # flask default port is 5000, but it will cause conflict on MacOS

or 

# Start flask app with debug mode (If you want to monitor log in development)
flask --app main run --port 3000 --debug
```

### Expose to internet with ngrok


```shell
# ngrok
# Use ngrok to expose the Flask app to the internet
ngrok http 3000

# Paste back to LINE Developer Console
# https://developers.line.biz/console/
# https:/<link provide from ngrok>/callback
https:/abcdefg.ngrok-free.app/callback
```

### Deploy to Google Cloud Run

[Deploy to Cloud Run from a Git repository](https://cloud.google.com/run/docs/quickstarts/deploy-continuously)

- Go to Google Cloud Console
- Select "Cloud Run"
- Select "Connect repo"
  - Connect github repo
  - Define service name
  - Allow all ingress
- In "Containers, Volumes, Networking, Security"
  - Select "container"
  - Add environment variable:

```shell
# environment variables
MONGODB_CONNECTION <value> // MongoDB Link
CHANNEL_TOKEN <value> // LINE Channel Token
CHANNEL_SECRET <value> // LINE Channel Secret
CURRENCY_COM_API_KEY <value> // currencyapi.com API Key
```

- Select "Create"



## Features

### Basic Expense Functionality

- Add expense data
  - Select category for each data for future analysis.
  - Calculate more or less depend on category.
- ~~View balance~~ Tempoary not available but can view in checkout function.
- Checkout and clear balance.
- ~~Delete unsettled total (todo after refactor)~~
- View historical data.

### Currency exchange

- Add data with data currency code while add new expense.
- Save different currency rate if user defined checkout currency is different currency.
- Checkout with different currency.

## Contributing

Contributions for new features are welcome! I will review all pull requests as I could ❤️

## Terms of Use

Just provide credit to the source.
