# Overview
A command-line interface to scrape jobs from Indeed.com with search terms. It is configured to look for jobs in Israel.  
**Note:** the tags in Indeed website can change and if it does you will see that no results are being found and the Dataframe
that comes back is `None`.

Currently this version works with Unix-based systems only (tested on MacOS with python 3.7) 

# Installation
1. This package uses `Selenium` which can emulate browser usage within python, with 
Google Chrome browser. You need to install Chrome and the correct driver to use with Selenium in addition to the `selenium` package.
Please refer to https://pypi.org/project/selenium/ for further details.
2. Clone the repo to your local machine.
3. Give execution permissions to `jobs.py` like so: `$ chmod +x jobs.py`

# Usage
You can always issue `$ ./jobs.py -h` for help and usage instructions.  

For example, in order to grab the 30 first (sorted by date with newest first) jobs for "data scientist" query
and keep only the jobs that have at least one of "machine learning, engineer, python" keywords (separated by `,`) inside
the (description + requirements) text you would type:  
`$ ./jobs.py "data scientist" -t "machine learning, engineer, python" -n 30`  
If you wanted the first 30 jobs to be sorted by relevance instead, you would add `-sbr` to the former.  
And if you wanted to keep only the jobs that have **all** the keywords in the text you would add `-a` to the command above.

## Output and Logs
### Output
The output is an HTML table with job title, company, text, and a clickable link as its columns. This table is being saved as
`jobs_[Current_Date].html` to your main folder where you cloned the repo to.
Current_Date is the current date like so: 2020-03-14.

### Logs
The command keeps logs for different stages of the process. There is one log file for each date so if you run this couple of
times at the same day, the logs get appended to the same file. The logs are saved in the `logs` folder under you main folder
where you cloned the repo to.

# TODO
1. Specify the country in which to look. This could possibly have issues with html tags compatibility across different indeed
country-specific sites.
2. Add option to send jobs file to email. Potential problem (for the free options) when using Gmail is a trade-off
between allowing non-secure connections to your Gmail or generating a refresh token that will expire once in a while,
so the solution is not robust enough.
3. Optional - install the `jobs.py` script to system PATH.
4. Add example for usage with cron
5. Make the code work with Windows
  
