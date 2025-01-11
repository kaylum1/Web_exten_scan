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

