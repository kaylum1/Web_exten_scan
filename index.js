const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const axios = require('axios');
const cheerio = require('cheerio');

const app = express();
const PORT = 3000;

app.use(bodyParser.json());

// MongoDB connection
const DB_URL = 'mongodb+srv://kaylumsmith:HS0KKaCbX4pbFiMM@diss-server.beqfh.mongodb.net/urlLogger?retryWrites=true&w=majority';
mongoose.connect(DB_URL, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => console.log('Connected to MongoDB'))
  .catch((err) => console.error('MongoDB connection error:', err));

// Define URL schema
const urlSchema = new mongoose.Schema({
  url: { type: String, required: true },
  name: { type: String, default: '' },
  isSecure: { type: Boolean, default: null },
  checkedAt: { type: Date, default: null },
});

const UrlLog = mongoose.model('UrlLog', urlSchema);

// Route to log URL
app.post('/log-url', async (req, res) => {
  const { url } = req.body;

  try {
    const isSecure = url.startsWith('https://');
    let name = '';

    // Fetch the webpage title
    try {
      const response = await axios.get(url);
      const $ = cheerio.load(response.data);
      name = $('title').text();
    } catch (error) {
      console.error(`Error fetching title for ${url}:`, error.message);
    }

    // Store or update the URL log in MongoDB
    await UrlLog.findOneAndUpdate(
      { url },
      { url, name, isSecure, checkedAt: new Date() },
      { upsert: true, new: true }
    );

    res.json({ message: 'URL logged successfully', url, name, isSecure });
  } catch (error) {
    console.error('Error logging URL:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});



// Route to get URL info for popup
app.get('/get-url-info', async (req, res) => {
  const { url } = req.query;
  try {
    const urlInfo = await UrlLog.findOne({ url });
    if (urlInfo) {
      res.json({
        url: urlInfo.url,
        name: urlInfo.name,
        isSecure: urlInfo.isSecure,
      });
    } else {
      res.status(404).json({ message: 'URL not found' });
    }
  } catch (error) {
    console.error('Error fetching URL info:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/*
const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const app = express();
const PORT = process.env.PORT || 3000;

// MongoDB connection string
const DB_URL = 'mongodb+srv://kaylumsmith:HS0KKaCbX4pbFiMM@diss-server.beqfh.mongodb.net/urlLogger?retryWrites=true&w=majority';




mongoose.connect(DB_URL, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => console.log('Connected to MongoDB'))
  .catch(err => console.error('MongoDB connection error:', err));

// Define URL log schema and model
const urlLogSchema = new mongoose.Schema({
  url: String,
  timestamp: { type: Date, default: Date.now }
});

const UrlLog = mongoose.model('UrlLog', urlLogSchema);

// Middleware
app.use(bodyParser.json());

// Route to log URLs
app.post('/log-url', async (req, res) => {
  const { url } = req.body;
  if (!url) {
    return res.status(400).send('URL is required');
  }

  try {
    const log = new UrlLog({ url });
    await log.save();
    res.status(200).send('URL logged successfully');
  } catch (error) {
    console.error('Error saving log:', error);
    res.status(500).send('Internal server error');
  }
});

// Route to get all logged URLs
app.get('/logs', async (req, res) => {
  try {
    const logs = await UrlLog.find().sort({ timestamp: -1 });
    res.status(200).json(logs);
  } catch (error) {
    console.error('Error fetching logs:', error);
    res.status(500).send('Internal server error');
  }
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

*/


