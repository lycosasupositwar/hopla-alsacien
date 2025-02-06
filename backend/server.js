const express = require('express');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

let points = [];

app.post('/add-point', (req, res) => {
    const { l, a, b, text } = req.body;
    points.push({ l, a, b, text });
    res.status(201).send('Point added');
});

app.get('/get-points', (req, res) => {
    res.json(points);
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});