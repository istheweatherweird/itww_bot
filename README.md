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
