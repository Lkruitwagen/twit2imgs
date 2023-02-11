# twit2imgs
A basic containerisable library to scrape images from twitter and post them to cloud storage and various targets such as a Google Photos album. A blog write-up is available [here](https://medium.com/p/fa9bf666b0e9/).

![s2_cover](cover.png)

This library is in production retrieving [Sentinel-2](https://sentinel.esa.int/web/sentinel/missions/sentinel-2) images from [@betatim's](https://twitter.com/betatim).  [Sentinel-2 Bot](https://twitter.com/Sentinel2Bot) ([Github](https://github.com/wildtreetech/sentinel2-bot)). The images are stored in a [public Google Storage bucket](https://console.cloud.google.com/storage/browser/beautiful-s2), cropped to 16:9, annotated, and posted to a public [Google Photos Album](https://photos.app.goo.gl/5rj1ji5xseNo8pn59). This album is also cleared daily, so that entirely new images are available every day. The Google Photos client uses components from [@eshmu's](https://twitter.com/eshmu) [gphotos-upload](https://github.com/eshmu/gphotos-upload).


## Installation

This library can be simply pip-installed:

    pip install .

This package also uses the font `FreeMonoBold.ttf`. It can be installed with:

    sudo install -m644 FreeMonoBold.ttf /usr/share/fonts/truetype/freefont

### Development

To install for development, use the `-e` option and the `dev` extras, and install the font as above.

    pip install -e .[dev]
    sudo install -m644 FreeMonoBold.ttf /usr/share/fonts/truetype/freefont

To setup pre-commit:

    pre-commit install
    pre-commit autoupdate

## Useage

This package is installed with a command line utility that executes the computational graph at [src/twit2imgs/cli.py]. The configuration `.yaml` file can be specified as the argument to the cli utility.

    scrape-tweets {config}

## Docker

This library can be deployed using Docker. To build the docker image:

    docker build -t twit2img .

To run the docker container a number of environment variables will need to be set. These can be written to an `env.list` file:

    # env.list
    TWITTER_API_BEARER_TOKEN=<your-twitter-api-bearer-token>
    TOKEN=<your-google-photos-access-token>
    REFRESH_TOKEN=<your-google-photos-refresh-token>
    TOKEN_URI=https://oauth2.googleapis.com/token
    CLIENT_ID=<your-google-app-client-id>
    CLIENT_SECRET=<your-google-app-client-secret>
    SLACKBOT_TOKEN=<your-optional-slackbot-token>
    SLACKBOT_CHANNEL=<slack-channel-to-post-to>

Google application credentials will also be needed. These can be set in the development environment `export GOOGLE_APPLICATION_CREDENTIALS=<path-to-credentials.json` and then used with `env.list` to run the docker image:

    docker run \
    -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/keys/[FILE_NAME].json \
    -v $GOOGLE_APPLICATION_CREDENTIALS:/tmp/keys/[FILE_NAME].json:ro \
    --env-file=env.list \
    twit2img
