# Spotify Song Recommendations

## Definition

An app that allows a user to receive recommendations from a playlist of their choosing.

## Installation

I am using Python 3.9.1 with this project. Use the package manager [pip](https://pip.pypa.io/en/stable/) to install all dependencies. I would recommend using a virtual environment before installing dependencies. Navigate to the main directory (where `manage.py` is) and run the below command:
```bash
pip install -r requirements.txt
```

## Usage

In the same directory, use the below commands to intialise and start the application

```python
python manage.py migrate  # creates and loads database schema
python manage.py runserver  # runs application
```

Your terminal will then generate a url to paste into your browser where the app is ran.

Use the following steps to use the app:
1. Click "Login with Spotify", and enter your Spotify credentials
2. Choose a playlist from the Featured Playlist grid, or copy the Spotify URI from the Playlist detail in the Spotify desktop app
3. Click "Get recommendations" (keep in mind that if it's the first time you've requested recommendations it will take significantly longer as the model has to be trained)
4. Click on any of the songs that are generated to be redirected to Spotify's website to give the song a listen!

## Demo (click the thumbnail to be redirected)

[![Watch the video](https://i.imgur.com/zQpMsDZ.jpg)](https://www.youtube.com/watch?v=pUMX5-VyBaw&t=)

## Analysis

Please refer to the Jupyter notebook for required analysis

## Conclusion

Please refer to Jupyter notebook for required conclusion

## License
[MIT](https://choosealicense.com/licenses/mit/)