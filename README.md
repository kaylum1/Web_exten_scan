# web_exten_scan



Node.js Installation Details
Node.js Version: v22.13.0
Installed Path: /usr/local/bin/node
npm Version: v10.9.2
npm Installed Path: /usr/local/bin/npm
Important Note: Ensure that /usr/local/bin is in your $PATH.


MongoDB Atlas Connection Details
Connection IP Address:
Current IP: 77.101.13.248 (added for local connectivity)
Only IPs added to the Access List will be able to connect.
Database User Details:
Username: kaylumsmith
Password: HS0KKaCbX4pbFiMM
Driver Information:
Driver: Node.js
Driver Version: 6.7 or later
Command to Install the Driver:
npm install mongodb
Connection String for Application Code:
mongodb+srv://kaylumsmith:HS0KKaCbX4pbFiMM@diss-server.beqfh.mongodb.net/?retryWrites=true&w=majority&appName=Diss-Server
Note: The password will not be available again after this setup.



Additional Resources
Get started with the Node.js Driver
Node.js Starter Sample App
Access your Database Users
Troubleshoot Connections
This should cover all the key information needed for your setup. Let me know if you need further assistance! ​​





Checklist: Terminal Downloads for the Server Environment
1. Install Node.js and npm

If you haven't already installed Node.js, follow these steps:
Mac/Linux:

curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

Windows:
Download the latest LTS version of Node.js from Node.js Official Website.
During installation, ensure that the option "Add to PATH" is selected.


2. Verify Installation: After installing Node.js, verify the installation:

node -v
npm -v

This should print the versions of Node.js and npm.


3. Initialize the Node.js Project: In your project directory, initialize a Node.js project:

npm init -y

4. Install Required Packages: Install the necessary packages:

npm install express mongoose body-parser

express: For creating the server.
mongoose: For connecting to MongoDB.
body-parser: For parsing JSON request bodies.


5. Check if MongoDB is Accessible: Since you already have a MongoDB Atlas server, ensure that it’s accessible by testing it with a simple connection script:

Create a file named testMongoConnection.js with the following content:
const mongoose = require('mongoose');

const DB_URL = 'mongodb+srv://kaylumsmith:HS0KKaCbX4pbFiMM@diss-server.beqfh.mongodb.net/urlLogger?retryWrites=true&w=majority';

mongoose.connect(DB_URL, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => {
    console.log('Connected to MongoDB');
    process.exit(0);
  })
  .catch(err => {
    console.error('MongoDB connection error:', err);
    process.exit(1);
  });


Run the script:

node index.js

If the connection is successful, you should see:

Connected to MongoDB



to see the logs of the URLS

http://localhost:3000/logs
