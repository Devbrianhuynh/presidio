# Presidio
Presidio collects options chains and Greeks data from Yahoo Finance and packages this data into one, simple UI/UX that can be downloaded by anyone for free and without any limitations on usage.  
- [Technologies Used](#technologies) - Frameworks and languages used
- [Installation](#installation) - How to install Presidio
- [Usage](#usage) - How to use Presidio
- [Tests](#tests) - How to test Presidio
- [Contributing](#contributing) - How to contribute in this project
- [License](#license) - MIT License  

https://github.com/Devbrianhuynh/presidio/assets/145720981/48de2453-1861-4c13-b3f4-3979608edb18

## Why did I build Presidio?
- My desire to turn something that requires payment and with limitations into something that is now free and limitless.
- Getting a taste of Flask, full-stack development, and how a software product works
- Desire to learn how to write code using 3-tier architecture 

## Why use Presidio?
- Before Presidio, people relied on CBOE and other options dataset providers and pay for datasets that otherwise could have been free
  - Otherwise, they would manually connect to a mulitple APIs to extract options data, create a CSV, and inject that CSV with the data extracted from the APIs
- With Presidio, users can enter their desired stock/ETF symbol and the expiration date, distract themselves with something for 2-5 min. (while the software is running), and come back to see a complete dataset of the stock/ETF's options chains and Greeks
- At no cost, downloadable, and with unlimited usage

<a name='technologies'></a>
## Built With
- ![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white) - Version 3.0.0
  - Connects the Python program to HTML
- ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) - Version 3.12.2
  - Logic for gathering and handling options data coming from the API
- ![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)
  - Logic for making the gathered options data downloadable and improve the UI/UX of the project
- ![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
  - The main structure of the web page
- ![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)
  - Styles to define the appearance of the web page

<a name='installation'></a>
## Installation
### Prerequisties  
To use Presidio, you will need:
- Flask 3.0.0 or later
- Python 3.11.2 or later
- yahoo_fin 0.8.9.1 or later
- conda (Anaconda) 23.7.4 or later (optional; however, if the software fails to function, download Anaconda)
- requests_html
  
### How to Install  
**Install Dependencies**  

1.  Flask
      ```bash
      pip install Flask
      ```
2. yahoo_fin
      ```bash
      pip install yahoo_fin
      ```
3. Anaconda
    ```txt
    https://www.anaconda.com/download/
    ```
5. reqeusts_html
    ```bash
    pip install requests_html
    ```

**Install Presidio**  

1. Fork this repository, then:

2. To clone and run this software, you'll need Git Bash. From your command line:
    ```bash
    # Clone this repository
    git clone https://github.com/Devbrianhuynh/presidio
    ```
3. Navigate into the repository
    ```bash
    # Go into the repository
    cd presidio
    ```
4. Open index.html in a browser
    ```txt
    Open the index.html file in your preferred web browser
    ```

<a name='usage'></a>
## Usage
1. Searching for an expiration date:
    - Scroll down to the Terminal or click on "TRY PRESIDIO SEARCH"
    - Enter the ticker of a stock/ETF that you want to research on
    - Click on "Search Expiration Dates" to see the list of expiration dates for the stock/ETF
    - The website will refresh and bring you back to the top of the page (you (if you contribute) or I will fix this issue later)
    - Simply scroll down again or click on "TRY PRESIDIO SEARCH"
      
2. Getting options chain and Greeks data
    - Enter the ticker of a stock/ETF that you want to research on
    - Enter the expiration date of that stock/ETF
    - There are 3 options:
        1. Search for the call options for that stock/ETF
        2. Search for the put options for that stock/ETF
        3. Search for BOTH call and put options for that stock/ETF
    - Distract yourself with something or someone for 2-5 minutes while the program runs
  
3. Retrieving the options chain and Greeks data
   - Once the data is loaded, the website will refresh and bring you back to the top of the page (you (if you contribute) or I will fix this issue later)
   - Scroll down or click on "TRY PRESIDIO SEARCH"
   - On the bottom of the Terminal:
        1. Click on "Calls" and "Call Greeks" if you are searching for call options
        2. Click on "Puts" and "Put Greeks" if you are searching for put options
        3. Click on "Calls and Puts" and both the "Call Greeks" and "Put Greeks" if you are searching for both call and put options
           
4. Downloading the options chain and Greeks data
   - Click on "Download CSV"
   - A download file will popup; double-click it to open the file
       - A CSV file will open in VS Code containing all of the options data you searched for
       - Do anything you want with this CSV file! It is all yours!

<a name='tests'></a>
## Tests
- To test data tier, go to the options_terminal.py file  
  1. Scroll to the bottom of the file
  2. Paste this code:
      ```python
      options_chain = Options_Chain('AAPL', 'March 1, 2024')
      options_chain.front_month_call_options() 
      ```

- To test the applciation tier, go to the options_application.py file
  1. Scroll to the bottom of the file
  2. Paste this code:
      ```python
      options_application = Options_Application('AAPL', 'March 1, 2024')
      options_application.lookup_expiration_dates()
      options_applciation.input_options_to_dataset('call')
      options_application.extract_options_from_dataset('call')
      ```
      
- Go to your PostgreSQL client and check out the data the software inserted into your database!

<a name='contributing'></a>
## Contributing
**IMPORTANT**: Everyone is welcome and encouraged to criticize and laugh at my project. It is my duty to listen to these criticisms and think about how I can reduce these in the future. Please, if you have something to say, say it. It will NOT hurt my feelings!

<a name='license'></a>
## License
This project is licensed under the <a href='https://opensource.org/license/MIT'>MIT License</a> and was originally developed by <a href='https://github.com/Devbrianhuynh'>@Devbrianhuynh</a>



























