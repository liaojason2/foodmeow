# foodmeow

## Diagram

![Diagram](assets/diagram.jpeg)

## Demo

/* TODO */

## Story

I runaway from home when I was 18 because we have different opinion on education. A week later my dad said he would give me money for meals as pocket money. He created a group and asked me to report the amount by typing "previously accumulated money + this time's money" each time. I found this too troublesome, so I wrote a bot to do the calculations.

It was too difficult to create a bot from scratch suddenly, so at that time, I just modified from [CBFHSS](https://github.com/CBFHSS). The code was so ugly that I didn't even want to admit I wrote it, and maintaining this infrastructure cost NT$300 a month. You can found the oldest version in [here (moneycalaulater)](https://github.com/liaojason2/moneycalaulater).

In 2021, I discovered that MongoDB Atlas is free, so I decided to rewrite the code and migrate the data to MongoDB Atlas. I don't rally liked Heroku and I found GCP Cloud Run to be fantastic. Currently, both application and database are hosted on Google Cloud's asia-east1 (Taiwan).

In 2024, After years of working in software industry, I decided to refactor this project to makes it meet industry standard. I am trying to clean code and add testing into this project.

## How to use

/* TODO */

## Features

- Expense Tracking
  - Add food expenses
  - Add general expenses
  - View unsettled total
  - Delete unsettled total
  - View historical data
  - Exit and delete temporary data

## Contributing

Contributions for new features are welcome!  
As long as the variable names and code are clear, I will review all pull requests ❤️

## Terms of Use

Just provide credit to the source.
