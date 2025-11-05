const express = require('express');
const axios = require('axios');
const path = require('path');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;
const API_URL = process.env.API_URL || 'http://localhost:5000/api';

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

// Set EJS as templating engine
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Helper function to make API calls
async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const config = {
            method,
            url: `${API_URL}${endpoint}`,
            headers: { 'Content-Type': 'application/json' }
        };

        if (data) {
            config.data = data;
        }

        const response = await axios(config);
        return response.data;
    } catch (error) {
        console.error(`API Error: ${error.message}`);
        throw error;
    }
}

// Routes

// Home page - display all posts
app.get('/', async (req, res) => {
    try {
        const data = await apiCall('/posts');
        res.render('index', {
            posts: data.posts || [],
            error: null
        });
    } catch (error) {
        res.render('index', {
            posts: [],
            error: 'Failed to load posts'
        });
    }
});

// About page
app.get('/about', (req, res) => {
    res.render('about');
});

// Users page - display all users
app.get('/users', async (req, res) => {
    try {
        const data = await apiCall('/users');
        res.render('users', {
            users: data.users || [],
            error: null
        });
    } catch (error) {
        res.render('users', {
            users: [],
            error: 'Failed to load users'
        });
    }
});

// Add user page
app.get('/user/add', (req, res) => {
    res.render('add_user', { error: null, success: null });
});

// Handle user creation
app.post('/user/add', async (req, res) => {
    try {
        const { username, email } = req.body;
        await apiCall('/users', 'POST', { username, email });
        res.redirect('/users');
    } catch (error) {
        res.render('add_user', {
            error: error.response?.data?.error || 'Failed to create user',
            success: null
        });
    }
});

// Add post page
app.get('/post/add', async (req, res) => {
    try {
        const data = await apiCall('/users');
        res.render('add_post', {
            users: data.users || [],
            error: null,
            success: null
        });
    } catch (error) {
        res.render('add_post', {
            users: [],
            error: 'Failed to load users',
            success: null
        });
    }
});

// Handle post creation
app.post('/post/add', async (req, res) => {
    try {
        const { title, content, user_id } = req.body;
        await apiCall('/posts', 'POST', {
            title,
            content,
            user_id: parseInt(user_id)
        });
        res.redirect('/');
    } catch (error) {
        const usersData = await apiCall('/users');
        res.render('add_post', {
            users: usersData.users || [],
            error: error.response?.data?.error || 'Failed to create post',
            success: null
        });
    }
});

// API proxy endpoints (optional - for frontend JavaScript to use)
app.get('/api/posts', async (req, res) => {
    try {
        const data = await apiCall('/posts');
        res.json(data);
    } catch (error) {
        res.status(500).json({ error: 'Failed to fetch posts' });
    }
});

app.get('/api/users', async (req, res) => {
    try {
        const data = await apiCall('/users');
        res.json(data);
    } catch (error) {
        res.status(500).json({ error: 'Failed to fetch users' });
    }
});

// Error handling
app.use((req, res) => {
    res.status(404).render('404', { error: 'Page not found' });
});

app.use((error, req, res, next) => {
    console.error(error);
    res.status(500).render('error', { error: 'Internal server error' });
});

// Start server
app.listen(PORT, () => {
    console.log(`Frontend server running on http://localhost:${PORT}`);
    console.log(`Connecting to API at ${API_URL}`);
});
