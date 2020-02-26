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

Follow these steps to start a Twitter bot for one of the locations in the [stations spreadsheet](https://github.com/istheweatherweird/istheweatherweird-data-hourly/blob/master/csv/stations.csv):

1. Start a new Twitter account for your desired city. Give it a cover image, profile picture, and bio.
2. Visit https://developer.twitter.com/en/apps, and go through the steps there to Create a New App for your new account.
3. Once you've completed Twitter's application, you'll be prompted to create Consumer API keys and an Access Token and Access Token Secret. Add those to your local `secrets.py` file with the city's ICAO code as a prefix.
4. Change the `cities` variable in `bots.py` to include the name of your city. This should match the way it's written in [the station spreadsheet's](https://github.com/istheweatherweird/istheweatherweird-data-hourly/blob/master/csv/stations.csv) `place` column.
5. Log into this repo's Heroku app and go to `Settings` -> `Config Variables`. Copy over your 4 new keys from step 3.

That's it! Your bot should now tweet every day at 6pm local time!
