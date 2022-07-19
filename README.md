<br/>
<p align="center">
  <a href="https://github.com/makeme-a-bug/synerticsOS">
    <img src="https://synertics.io/staticfiles/img/logo-vector.svg" alt="Logo" width="200" height="80">
  </a>

  <h3 align="center">OS Driver Deployment Solution</h3>

  <p align="center">
    Automate Dispatching Activities
    <br/>
    <br/>
    <a href="https://github.com/makeme-a-bug/synerticsOS/issues">Report Bug</a>
    .
    <a href="https://github.com/makeme-a-bug/synerticsOS/issues">Request Feature</a>
  </p>
</p>

![Contributors](https://img.shields.io/github/contributors/makeme-a-bug/synerticsOS?color=dark-green) ![Forks](https://img.shields.io/github/forks/makeme-a-bug/synerticsOS?style=social) ![Stargazers](https://img.shields.io/github/stars/makeme-a-bug/synerticsOS?style=social) ![Issues](https://img.shields.io/github/issues/makeme-a-bug/synerticsOS) ![License](https://img.shields.io/github/license/makeme-a-bug/synerticsOS) 

## Table Of Contents

* [About the Project](#about-the-project)
* [Built With](#built-with)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Roadmap](#roadmap)
* [Contributing](#contributing)
* [License](#license)
* [Authors](#authors)
* [Acknowledgements](#acknowledgements)

## About The Project

This project make use of Synertics.io dispatching and disposition API to provide you with out of the box solution to your logistics managements problems with route optimization. it provides you with a simple way to easily import your excel or csv files. a table view of all your deliveries and drivers and a map that shows you the trips that were created and optimized and a lot more :). if you don't like anything or are facing issues don't worry it is open source you can modify it how ever you like and if you are not on the technical side no worries ;) we are here for you. just open an issue and we will solve it as soon as possible.

## Built With

The solution is made with Django framework. All the packages you will need to install in order to run it are all mentioned is requirements.txt
you can install it by running
```sh
python -m pip install -r requirements.txt
```
in your shell

## Getting Started



### Prerequisites

it is recommended that you first create a python virtual environment. and the clone the project in it.
After cloning the project. you will need to run in the root folder
```sh
python -m pip install -r requirements.txt
```
to install all the dependences 

and make sure you have the following API keys available.
1. Synertics_api [synertics.io](https://synertics.io)
2. Google (for geocoding and autocomplete) [setting up google services]()
3. Mapbox (for map visualization)[setting up mapbox services]()

we will be using the following API keys in the next step



### Installation

first you will need create an .env file inside the root folder of the project
and write the following lines to your .env file
```sh
SYN_API=<your_api_key>
GOOGLE_API_KEY=<your_api_key>
MAPBOX_API_KEY=<your_api_key>
SECRET_KEY=<your_secret_key>
GOOGLE_EMAIL=<your_google_email_address>
GOOGLE_PASSWORD=<google_email_password>
```

you can generate django SECRET_KEY from [here](https://djecrety.ir/)

then in shell you will need to run
```sh
1. python manage.py makemigrations account delivery excelImport
2. python manage.py migrate
3. python manage.py runserver
 ```

to create a super user you will need to run
```sh
python manage.py createsuperuser
```


## Roadmap

See the [open issues](https://github.com/makeme-a-bug/synerticsOS/issues) for a list of proposed features (and known issues).

## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.
* If you have suggestions for adding or removing projects, feel free to [open an issue](https://github.com/makeme-a-bug/synerticsOS/issues/new) to discuss it, or directly create a pull request after you edit the *README.md* file with necessary changes.
* Please make sure you check your spelling and grammar.
* Create individual PR for each suggestion.

### Creating A Pull Request

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License.

## Authors

* **Muhammad Usama** - *Software Engineer* - [Muhammad Usama](https://github.com/makeme-a-bug/) - **

## Acknowledgements

* [Manuel Pessanha](https://github.com/SEAPessanha)
