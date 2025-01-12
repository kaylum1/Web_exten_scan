// index.js
const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const axios = require('axios');
const cheerio = require('cheerio');
const cors = require('cors');

const app = express();
const PORT = 3000;

app.use(bodyParser.json());
app.use(cors());

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
