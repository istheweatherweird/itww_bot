# ⛈ Is the Weather Weird in Chicago?

A Twitter bot for [istheweatherweird.com](http://www.istheweatherweird.com/), keeping an eye on Chicago.

Uses Python, tweepy, and Heroku. S/o to [this post](https://dev.to/emcain/how-to-set-up-a-twitter-bot-with-python-and-heroku-1n39) by [Emily Cain](https://emcain.github.io/) for the guiding method. Current data is pulled from the [National Weather Service API](https://www.weather.gov/documentation/services-web-api).

This is a bot by [Bea Malsky](https://beamalsky.fyi/). [istheweatherweird.com](http://www.istheweatherweird.com/) was made by [Jonah Bloch-Johnson](http://www.jonah.org/) and [Eric Potash](http://k2co3.net/).

## Requirements

- [Docker](https://www.docker.com/)

## Deployment

This app is deployed on Heroku. To deploy what's on the `master` branch:

  ```bash
  git push heroku master
  ```

To check out the logs:

  ```bash
  heroku logs --tail
  ```

## Running the app locally

To get started, run the following from your terminal:

1. Clone this repository and `cd` into your local copy.

  ```bash
  git clone git@github.com:istheweatherweird/itww_chicago.git
  cd nytquestions
  ```

2. Switch the `LOCAL_DEVELOPMENT` variable in `bot.py` to `True`

3. Rename `secrets_example.py` to `secrets.py`:

  ```bash
  mv secrets_example.py secrets.py
  ```

4. You'll need your own [Twitter API key](https://dototot.com/how-to-write-a-twitter-bot-with-python-and-tweepy/). Get it and fill it in to your new `secrets.py` file.

5. Run the app locally!

To preview your tweet(s) locally:

  ```bash
  docker-compose run --rm app python tweets.py
  ```

If successful, you'll see them in the terminal.

To test posting to Twitter:

  ```bash
  docker-compose run --rm app python bot.py
  ```

If successful, you'll see them posted to the Twitter account whose keys you specified in `secrets.py`.

## Setting up a bot for a new location

This Twitter bot is easy to set up for any location with an entry in [this spreadsheet](https://github.com/istheweatherweird/istheweatherweird-data-hourly/blob/master/csv/stations.csv)! If you'd like to get another one added, you're welcome to open an issue in this repo with the request.

Follow these steps to start a Twitter bot for one of the locations in the above spreadsheet:

1. Update your local `secrets.py` file so `CITY` matches one of the values in [this sheet's](https://github.com/istheweatherweird/istheweatherweird-data-hourly/blob/master/csv/stations.csv) `place` column.
1. Start a new Twitter account with your desired name.
2. Logged in as that Twitter account, visit https://developer.twitter.com/en/apps and go through the steps there to Create a New App.
3. Once you've completed Twitter's application, you'll be prompted to create Consumer API keys and an Access Token and Access Token Secret. Add those to your local `secrets.py` file.
4. Log into Heroku and create a new app.
5. Go into Heroku `Settings` -> `Config Variables` and copy over your `secrets.py` file variables.
6. Back in your Heroku `Overview` tab, add a new Installed add-on. Select Heroku Scheduler, and set it to run `python bot.py` every hour on the hour.

That's it! Your bot should now tweet every day at 6pm local time!
