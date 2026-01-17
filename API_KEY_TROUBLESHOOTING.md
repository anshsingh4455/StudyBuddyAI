# API Key Troubleshooting Guide

## Current Error: "Authentication failed"

If you're seeing "Authentication failed. Please check your API key in the .env file", follow these steps:

### Step 1: Verify Your API Key Format

Your `.env` file should contain:
```
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
```

**Important:**
- ✅ No quotes around the key
- ✅ No spaces before or after the `=`
- ✅ Key should start with `sk-or-v1-` or `sk-`
- ✅ Key should be on a single line

### Step 2: Get a Valid API Key

1. Go to https://openrouter.ai/keys
2. Sign in or create an account
3. Create a new API key
4. Copy the key (it will start with `sk-or-v1-`)
5. Paste it in your `.env` file

### Step 3: Check Your .env File Location

The `.env` file should be in the project root:
```
StudyBuddyAI/
  ├── .env          ← Should be here
  ├── app.py
  ├── backend/
  └── ...
```

### Step 4: Verify the Key is Loading

After updating your `.env` file:
1. Restart your Streamlit app (stop and run `streamlit run app.py` again)
2. The app should now work without authentication errors

### Common Issues:

**Issue:** Key format is wrong
- **Solution:** Make sure the key starts with `sk-or-v1-` and has no extra characters

**Issue:** Key is expired or invalid
- **Solution:** Get a new key from https://openrouter.ai/keys

**Issue:** .env file not being read
- **Solution:** Make sure the file is named exactly `.env` (with the dot) and is in the project root

**Issue:** Extra spaces or quotes
- **Solution:** Remove any quotes or spaces around the key value

### Still Having Issues?

1. Double-check your API key at https://openrouter.ai/keys
2. Make sure you're using the correct key (not a test key or expired key)
3. Try creating a new API key
4. Restart the Streamlit app after making changes
