# Google Gemini AI Setup Guide for TrabahoPH

This guide explains how to set up the AI-powered job recommendation feature using Google's Gemini API (free tier).

## What's New

The job seeker dashboard now includes **AI-powered job recommendations** based on the skills you add to your profile. The AI analyzes your skills and recommends the most relevant jobs from available positions.

## Getting Started with Gemini API

### Step 1: Get Your Free Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account (create one if you don't have it)
3. Click on **"Create API Key"** button
4. Select **"Create API key in new project"** (or existing project)
5. Copy the generated API key

### Step 2: Configure the API Key in Your Django Application

#### Option A: Using Environment Variables (Recommended for Production)

1. Create a `.env` file in your project root directory:
```bash
# .env file in c:\Users\Administrator\Documents\TrabahoPH1\.env
GEMINI_API_KEY=your_api_key_here
```

2. Update your `settings.py` to load the environment variable:
```python
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
```

3. Install python-dotenv:
```bash
pip install python-dotenv
```

#### Option B: Direct Configuration (Development Only)

Add to `trabaho/settings.py`:
```python
GEMINI_API_KEY = 'your_api_key_here'
```

**⚠️ WARNING:** Never commit your API key to version control. Always use environment variables!

### Step 3: Verify the Installation

1. Start your Django server
2. Login as a job seeker
3. Go to your dashboard at `http://localhost:8000/seeker-dashboard/`
4. Add your skills to your profile: go to **"Edit Profile"** and add your skills (comma-separated)
5. Return to the dashboard and look for the **"Recommended for You"** section
6. The AI should now recommend jobs based on your skills

## How It Works

1. **Profile Skills**: When you add skills to your profile (e.g., "Communication, Leadership, Programming"), the system includes them
2. **AI Analysis**: The Gemini API analyzes available jobs and matches them with your skills
3. **Smart Recommendations**: Jobs are ranked based on skill relevance and job requirements
4. **Real-time Updates**: Recommendations update each time you view your dashboard

## Features

- ✅ **Free Tier**: Uses Google's free Gemini API tier (no credit card required initially)
- ✅ **Skill-Based**: Matches jobs to your specific skills
- ✅ **Smart Matching**: Considers job requirements and your experience
- ✅ **Fallback Support**: If AI is unavailable, shows recent active jobs instead
- ✅ **Privacy**: Your data is only sent to Google's API, not stored externally

## Troubleshooting

### "Profile Incomplete" Still Shows

Make sure you have completed:
- ✓ First Name
- ✓ Last Name
- ✓ Mobile Number
- ✓ Barangay (Location)

### AI Recommendations Not Showing

1. **Check API Key**: Verify your `GEMINI_API_KEY` is correctly set
2. **Add Skills**: Make sure you've added skills to your profile
3. **Check Console**: Look for error messages in your Django server logs
4. **Try Again**: Sometimes the API needs a moment - refresh the page

### "No module named google.generativeai"

Run:
```bash
.venv\Scripts\python.exe -m pip install google-generativeai==0.3.0
```

## API Limits (Free Tier)

- **Requests per minute**: 60
- **Requests per day**: 1,500
- **Tokens per minute**: 1,000,000

For most users, these limits are more than sufficient.

## File Modifications

The following files were modified to add AI recommendations:

1. **requirements.txt** - Added `google-generativeai==0.3.0`
2. **trabaho/settings.py** - Added `GEMINI_API_KEY` configuration
3. **jobs/views.py** - Added `get_ai_recommended_jobs()` function
4. **jobs/dashboard_views.py** - Updated `SeekerDashboardView` to use AI recommendations

## For Production

Before deploying to production:

1. Use environment variables for the API key
2. Add error handling and logging
3. Consider caching recommendations (if using the same profile)
4. Monitor API usage to stay within free tier limits
5. Add rate limiting if you expect high traffic

## Support

If you encounter issues:

1. Check the Django server logs for error messages
2. Verify your API key is valid at [Google AI Studio](https://aistudio.google.com/app/apikey)
3. Ensure your internet connection is stable
4. Check that skills are properly formatted in your profile

Enjoy your AI-powered job recommendations! 🚀
