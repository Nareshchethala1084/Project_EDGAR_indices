# Phase 1:
EDGAR Indices project
This project entails writing Python code that efficiently processes EDGAR index files to construct a data frame, enabling users to perform basic searches and analysis.
It has two main purposes:
  Produce Python code that addresses a specific institutional need.
  Learn about an important financial data repository and its contents as well as access.
Here with this, individual can:
  Learn about EDGAR index files, their structure and content.
  Download index files (daily, quarterly) directly from the SEC's EDGAR site (https://www.sec.gov/os/accessing-edgar-data). 
  For this project, we excluded the XBRL filings.
  Parse index files, and create a data frame that will have all the content from index files. (Save the dataframe for access in the future without resorting to EDGAR again.)
  Allow users query the dataframe based on Form type / CIK / Company Name to generate a list of filings for the filters the user entered.
  The user interface for this could be very basic.
  The goal is to be able to get a certain filing or a list of filings.
  Display a filing with a given/chosen URL.
