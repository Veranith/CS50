# CS50

# Meals on Wheels Reporting and Tools
#### Video Demo: https://youtu.be/o_szaANxuAk
#### Description:

This project is a website to add some needed functionality for a local charity Meals on Wheels. The current application allows the staff to track clients and plan individual daily meals. While this tool was a great improvement to what they had before, it is a bit lacking in the form of reporting and some tools. The existing app uses a MySQL DB and I use a connection directly to the DB to help generate the needed reports and to add tools to expand the usability of the existing app.

This web app is written using python with the flask framework. I wanted to be able to deploy this application in the Microsoft Azure cloud and use the Azure Active Directory (AAD) authentication that is already in use onsite. This did add some challenges that I had to learn regarding how to securely authenticate the users to AAD as well as to authenticate the app to the DB hosted in Azure as well. Another goal I had was to not include any secret information in the code. I was able to achieve this by using environment variables and when deployed to Azure it will pull these variables from a secure Azure key vault.

The tools functionality of this app was added to the existing app using an Azure Function App which directly modifies the DB data. The tools page here is the front end for that script and it uses an API which was created through the function app. The function app uses the similar Azure helper scripts and added main script to handle DB lookups and updates. All updates are thoroughly validated and verified with the user through the function app API and the front end web site to ensure that there are no errors or duplication of data. The intent here is to seamlessly integrate with the main application without causing any issues.

One of my largest challenges with this project was finding the correct modules to allow me to connect to an Azure MySQL database. I had tried many different ones and formats until I found a combination that worked. I then moved these into the AzureHelpers.py file so I could reuse them as needed and ensure that I would not have to recreate this work.

Summary of files:
Static: This folder holds all the static parts of the website.
Templates: This folder contains all the templates to generate the webpages through the flask framework.
AzureAuthHelpers.py: This file contains functions to help with authentication to Azure.
AzureHelpers.py: This file contains functions to help with communications with the Azure DB.
BaltimoreCyberTrustRoot.crt.pem: This is the certificate file needed to authenticate with Azure.
application.py: This is the initial python file which holds the flask code to run this tool.
helpers.py: This file holds all the custom functions used within this app.
requirements.txt: This file includes a list of all the Python modules needed to run this app.

