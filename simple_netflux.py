#!/usr/bin/env python3
"""
Simple Netflux - Minimal Netflix Clone
Works without external dependencies
"""

try:
    from flask import Flask, render_template_string, request, redirect, session, jsonify
    import json
    import os
    from datetime import datetime
    import hashlib
except ImportError:
    print("❌ Flask not installed!")
    print("📥 Install with: pip install flask")
    input("Press Enter to exit...")
    exit(1)

app = Flask(__name__)
app.secret_key = 'netflux_simple_key'

# Simple data storage with persistence
DATA_DIR = 'data'
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
FAVORITES_FILE = os.path.join(DATA_DIR, 'favorites.json')
CONTENT_FILE = os.path.join(DATA_DIR, 'content.json')
WATCH_HISTORY_FILE = os.path.join(DATA_DIR, 'watch_history.json')
WATCH_PROGRESS_FILE = os.path.join(DATA_DIR, 'watch_progress.json')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def load_data():
    """Load data from JSON files"""
    global users_data, favorites_data, content_data, watch_history_data, watch_progress_data
    
    # Load users
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                raw_users = json.load(f)
                # Convert to simple format for simple_netflux
                users_data = []
                for user in raw_users:
                    # Handle both 'type' and 'user_type' keys
                    user_type = user.get('type') or user.get('user_type', 'user')
                    
                    # Use the password as-is if it's simple, otherwise use default
                    password = user.get('password', 'user123')
                    if password.startswith('scrypt:'):
                        # Encrypted password, use default
                        password = 'admin123' if user_type == 'admin' else 'user123'
                    
                    # Handle name field
                    if 'name' in user:
                        name = user['name']
                    else:
                        name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
                    
                    users_data.append({
                        'id': user['id'],
                        'email': user['email'],
                        'password': password,
                        'name': name,
                        'type': user_type
                    })
        except Exception as e:
            print(f"Error loading users: {e}")
            users_data = [
                {'id': 1, 'email': 'admin@netflux.com', 'password': 'admin123', 'name': 'Admin', 'type': 'admin'}
            ]
    else:
        users_data = [
            {'id': 1, 'email': 'admin@netflux.com', 'password': 'admin123', 'name': 'Admin', 'type': 'admin'}
        ]
    
    # Load content
    if os.path.exists(CONTENT_FILE):
        try:
            with open(CONTENT_FILE, 'r', encoding='utf-8') as f:
                raw_content = json.load(f)
                # Convert to simple format
                content_data = []
                for item in raw_content:
                    content_data.append({
                        'id': item['id'],
                        'title': item['title'],
                        'year': item['year'],
                        'type': item['content_type'],
                        'category': item['category'],
                        'video_url': item['video_url'],
                        'rating': item['rating'],
                        'duration': item['duration'],
                        'description': item['description'],
                        'thumbnail': item.get('image_url', 'https://via.placeholder.com/300x450?text=No+Image')
                    })
        except Exception as e:
            print(f"Error loading content: {e}")
            content_data = [
                {
                    'id': 1, 'title': 'The Present', 'year': 2020, 'type': 'film', 'category': 'Drama',
                    'video_url': 'https://www.youtube.com/embed/WjqiU5FgsYc', 'rating': 8.7, 'duration': 7,
                    'description': 'A brilliant animated short film about a boy and his dog.',
                    'thumbnail': 'https://img.youtube.com/vi/WjqiU5FgsYc/maxresdefault.jpg'
                }
            ]
    else:
        content_data = [
            {
                'id': 1, 'title': 'The Present', 'year': 2020, 'type': 'film', 'category': 'Drama',
                'video_url': 'https://www.youtube.com/embed/WjqiU5FgsYc', 'rating': 8.7, 'duration': 7,
                'description': 'A brilliant animated short film about a boy and his dog.',
                'thumbnail': 'https://img.youtube.com/vi/WjqiU5FgsYc/maxresdefault.jpg'
            }
        ]
    
    # Load favorites
    if os.path.exists(FAVORITES_FILE):
        try:
            with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
                favorites_data = json.load(f)
        except:
            favorites_data = []
    else:
        favorites_data = []
    
    # Load watch history
    if os.path.exists(WATCH_HISTORY_FILE):
        try:
            with open(WATCH_HISTORY_FILE, 'r', encoding='utf-8') as f:
                watch_history_data = json.load(f)
        except:
            watch_history_data = []
    else:
        watch_history_data = []
    
    # Load watch progress
    if os.path.exists(WATCH_PROGRESS_FILE):
        try:
            with open(WATCH_PROGRESS_FILE, 'r', encoding='utf-8') as f:
                watch_progress_data = json.load(f)
        except:
            watch_progress_data = []
    else:
        watch_progress_data = []

def save_users():
    """Save users to JSON file"""
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving users: {e}")

def save_favorites():
    """Save favorites to JSON file"""
    try:
        with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
            json.dump(favorites_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving favorites: {e}")

def save_watch_history():
    """Save watch history to JSON file"""
    try:
        with open(WATCH_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(watch_history_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving watch history: {e}")

def save_watch_progress():
    """Save watch progress to JSON file"""
    try:
        with open(WATCH_PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(watch_progress_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving watch progress: {e}")

def save_content():
    """Save content to JSON file"""
    try:
        # Convert back to original format for storage
        content_to_save = []
        for item in content_data:
            content_to_save.append({
                'id': item['id'],
                'title': item['title'],
                'description': item['description'],
                'year': item['year'],
                'content_type': item['type'],
                'category': item['category'],
                'video_url': item['video_url'],
                'image_url': item['thumbnail'],
                'rating': item['rating'],
                'duration': item['duration'],
                'created_at': item.get('created_at', datetime.now().isoformat())
            })
        
        with open(CONTENT_FILE, 'w', encoding='utf-8') as f:
            json.dump(content_to_save, f, ensure_ascii=False, indent=2)
        print(f"✅ Content saved: {len(content_to_save)} items")
    except Exception as e:
        print(f"❌ Error saving content: {e}")

# Initialize data
load_data()

# Print loaded data for debugging
print("\n" + "="*50)
print("📊 LOADED DATA:")
print("="*50)
print(f"👥 Users loaded: {len(users_data)}")
for user in users_data:
    print(f"   - {user['email']} | Password: {user['password']} | Type: {user['type']}")
print(f"🎬 Content loaded: {len(content_data)}")
print("="*50 + "\n")

# HTML Templates
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Netflux - Giriş</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0a0a0a;
            color: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            position: relative;
            overflow: hidden;
        }
        
        /* Cinematic Background */
        body::before {
            content: '';
            position: fixed;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: 
                radial-gradient(circle at 30% 40%, rgba(229, 9, 20, 0.25) 0%, transparent 40%),
                radial-gradient(circle at 70% 60%, rgba(139, 0, 0, 0.2) 0%, transparent 40%),
                radial-gradient(circle at 50% 50%, rgba(255, 26, 26, 0.15) 0%, transparent 50%);
            animation: rotate 30s linear infinite;
            z-index: -2;
        }
        
        body::after {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                linear-gradient(135deg, rgba(10,10,10,0.9) 0%, rgba(26,10,10,0.85) 50%, rgba(10,10,10,0.9) 100%),
                repeating-linear-gradient(0deg, transparent, transparent 3px, rgba(229, 9, 20, 0.03) 3px, rgba(229, 9, 20, 0.03) 6px);
            z-index: -1;
        }
        
        @keyframes rotate {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Floating particles */
        .particle {
            position: fixed;
            width: 3px;
            height: 3px;
            background: rgba(229, 9, 20, 0.6);
            border-radius: 50%;
            animation: float 15s infinite;
            z-index: -1;
        }
        
        @keyframes float {
            0%, 100% {
                transform: translateY(0) translateX(0);
                opacity: 0;
            }
            10% {
                opacity: 1;
            }
            90% {
                opacity: 1;
            }
            100% {
                transform: translateY(-100vh) translateX(50px);
                opacity: 0;
            }
        }
        
        .container { 
            max-width: 480px;
            width: 100%;
            background: linear-gradient(145deg, rgba(30,30,30,0.95) 0%, rgba(42,42,42,0.9) 100%);
            padding: 60px 50px;
            border-radius: 25px;
            box-shadow: 
                0 30px 90px rgba(0, 0, 0, 0.7),
                0 0 80px rgba(229, 9, 20, 0.3),
                inset 0 0 0 1px rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px) saturate(180%);
            position: relative;
            z-index: 1;
        }
        
        .container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, transparent, #e50914, transparent);
            border-radius: 25px 25px 0 0;
        }
        
        .logo { 
            text-align: center;
            font-size: 56px;
            font-weight: 900;
            background: linear-gradient(135deg, #e50914 0%, #ff4444 50%, #e50914 100%);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 50px;
            animation: shimmer 3s linear infinite;
            letter-spacing: -3px;
            filter: drop-shadow(0 0 30px rgba(229, 9, 20, 0.6));
        }
        
        @keyframes shimmer {
            to { background-position: 200% center; }
        }
        
        h2 {
            text-align: center;
            margin-bottom: 35px;
            font-size: 30px;
            font-weight: 800;
            color: #fff;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .error {
            background: linear-gradient(135deg, rgba(229, 9, 20, 0.25) 0%, rgba(180, 7, 15, 0.25) 100%);
            color: #ff6b6b;
            padding: 18px;
            border-radius: 15px;
            margin-bottom: 25px;
            text-align: center;
            border: 1px solid rgba(229, 9, 20, 0.4);
            font-weight: 600;
            backdrop-filter: blur(10px);
        }
        
        input { 
            width: 100%;
            padding: 18px 24px;
            margin: 15px 0;
            background: rgba(255, 255, 255, 0.05);
            border: 2px solid rgba(255, 255, 255, 0.1);
            color: white;
            border-radius: 15px;
            font-size: 15px;
            transition: all 0.4s ease;
            font-weight: 500;
        }
        
        input:focus {
            outline: none;
            background: rgba(255, 255, 255, 0.08);
            border-color: #e50914;
            box-shadow: 0 0 30px rgba(229, 9, 20, 0.4), inset 0 0 20px rgba(229, 9, 20, 0.1);
            transform: translateY(-2px);
        }
        
        input::placeholder {
            color: rgba(255, 255, 255, 0.4);
        }
        
        button { 
            width: 100%;
            padding: 18px;
            background: linear-gradient(135deg, #e50914 0%, #b0070f 100%);
            color: white;
            border: none;
            border-radius: 15px;
            font-size: 17px;
            font-weight: 800;
            cursor: pointer;
            margin-top: 25px;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 10px 30px rgba(229, 9, 20, 0.5);
            text-transform: uppercase;
            letter-spacing: 1px;
            position: relative;
            overflow: hidden;
        }
        
        button::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }
        
        button:hover::before {
            width: 400px;
            height: 400px;
        }
        
        button:hover {
            background: linear-gradient(135deg, #ff1a1a 0%, #e50914 100%);
            transform: translateY(-3px);
            box-shadow: 0 15px 40px rgba(229, 9, 20, 0.7);
        }
        
        button:active {
            transform: translateY(-1px);
        }
        
        .back-link { 
            text-align: center;
            margin-top: 35px;
            color: #b3b3b3;
            font-size: 14px;
            font-weight: 500;
        }
        
        .back-link a { 
            color: #e50914;
            text-decoration: none;
            font-weight: 700;
            transition: all 0.3s ease;
            position: relative;
        }
        
        .back-link a::after {
            content: '';
            position: absolute;
            bottom: -2px;
            left: 0;
            width: 0;
            height: 2px;
            background: #e50914;
            transition: width 0.3s ease;
        }
        
        .back-link a:hover {
            color: #ff1a1a;
        }
        
        .back-link a:hover::after {
            width: 100%;
        }
    </style>
</head>
<body>
    <!-- Floating particles -->
    <div class="particle" style="left: 10%; animation-delay: 0s;"></div>
    <div class="particle" style="left: 20%; animation-delay: 2s;"></div>
    <div class="particle" style="left: 30%; animation-delay: 4s;"></div>
    <div class="particle" style="left: 40%; animation-delay: 1s;"></div>
    <div class="particle" style="left: 50%; animation-delay: 3s;"></div>
    <div class="particle" style="left: 60%; animation-delay: 5s;"></div>
    <div class="particle" style="left: 70%; animation-delay: 2.5s;"></div>
    <div class="particle" style="left: 80%; animation-delay: 4.5s;"></div>
    <div class="particle" style="left: 90%; animation-delay: 1.5s;"></div>
    
    <div class="container">
        <div class="logo">🎬 Netflux</div>
        <h2>Giriş Yap</h2>
        
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        
        <form method="POST">
            <input type="email" name="email" placeholder="E-posta adresinizi girin" required>
            <input type="password" name="password" placeholder="Şifrenizi girin" required>
            <button type="submit">Giriş Yap</button>
        </form>
        
        <div class="back-link">
            <p>Netflux'ta yeni misiniz? <a href="/register">Üye olun</a></p>
        </div>
    </div>
</body>
</html>
'''

INDEX_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Netflux - Ana Sayfa</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0a0a0a;
            color: white;
            min-height: 100vh;
            position: relative;
            overflow-x: hidden;
        }
        
        /* Animated Background */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 50%, rgba(229, 9, 20, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(139, 0, 0, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 40% 20%, rgba(255, 26, 26, 0.1) 0%, transparent 50%),
                linear-gradient(135deg, #0a0a0a 0%, #1a0a0a 50%, #0a0a0a 100%);
            z-index: -2;
            animation: backgroundShift 20s ease infinite;
        }
        
        body::after {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(255,255,255,0.01) 2px, rgba(255,255,255,0.01) 4px),
                repeating-linear-gradient(90deg, transparent, transparent 2px, rgba(255,255,255,0.01) 2px, rgba(255,255,255,0.01) 4px);
            z-index: -1;
            opacity: 0.3;
        }
        
        @keyframes backgroundShift {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.8; }
        }
        
        /* Header Styles */
        .header { 
            background: linear-gradient(180deg, rgba(10,10,10,0.98) 0%, rgba(10,10,10,0.95) 100%);
            padding: 20px 50px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 30px rgba(229, 9, 20, 0.2), 0 0 100px rgba(229, 9, 20, 0.1);
            backdrop-filter: blur(20px) saturate(180%);
            position: sticky;
            top: 0;
            z-index: 100;
            border-bottom: 1px solid rgba(229, 9, 20, 0.2);
        }
        
        .logo { 
            font-size: 36px;
            font-weight: 900;
            background: linear-gradient(135deg, #e50914 0%, #ff4444 50%, #e50914 100%);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: shimmer 3s linear infinite;
            letter-spacing: -2px;
            text-shadow: 0 0 40px rgba(229, 9, 20, 0.6);
            cursor: pointer;
            transition: transform 0.3s ease;
        }
        
        .logo:hover {
            transform: scale(1.05);
        }
        
        @keyframes shimmer {
            to { background-position: 200% center; }
        }
        
        .nav { 
            display: flex;
            gap: 8px;
            align-items: center;
            background: rgba(255, 255, 255, 0.03);
            padding: 8px;
            border-radius: 50px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .nav a { 
            color: #e0e0e0;
            text-decoration: none;
            font-weight: 600;
            font-size: 14px;
            padding: 12px 24px;
            border-radius: 50px;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        
        .nav a::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(229, 9, 20, 0.3), transparent);
            transition: left 0.5s ease;
        }
        
        .nav a:hover::before {
            left: 100%;
        }
        
        .nav a:hover {
            color: #fff;
            background: linear-gradient(135deg, rgba(229, 9, 20, 0.3) 0%, rgba(229, 9, 20, 0.1) 100%);
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(229, 9, 20, 0.4);
        }
        
        .nav a.active {
            background: linear-gradient(135deg, #e50914 0%, #b0070f 100%);
            color: white;
            box-shadow: 0 4px 20px rgba(229, 9, 20, 0.5);
        }
        
        /* Container */
        .container { 
            padding: 50px;
            max-width: 1800px;
            margin: 0 auto;
            position: relative;
        }
        
        .page-title { 
            font-size: 48px;
            font-weight: 900;
            margin: 40px 0 50px 0;
            text-align: center;
            background: linear-gradient(135deg, #fff 0%, #e50914 50%, #fff 100%);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: shimmer 4s linear infinite;
            letter-spacing: -2px;
            text-transform: uppercase;
            position: relative;
        }
        
        .page-title::after {
            content: '';
            position: absolute;
            bottom: -15px;
            left: 50%;
            transform: translateX(-50%);
            width: 100px;
            height: 4px;
            background: linear-gradient(90deg, transparent, #e50914, transparent);
            border-radius: 2px;
        }
        
        /* Content Grid */
        .content-grid { 
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 40px;
        }
        
        /* Content Card */
        .content-card { 
            background: linear-gradient(145deg, rgba(30,30,30,0.6) 0%, rgba(42,42,42,0.4) 100%);
            border-radius: 12px;
            overflow: hidden;
            transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
        }
        
        .content-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, rgba(229, 9, 20, 0.15) 0%, transparent 100%);
            opacity: 0;
            transition: opacity 0.5s ease;
            z-index: 1;
            pointer-events: none;
        }
        
        .content-card:hover {
            transform: translateY(-15px) scale(1.03);
            box-shadow: 
                0 25px 70px rgba(229, 9, 20, 0.4),
                0 0 60px rgba(229, 9, 20, 0.2),
                inset 0 0 0 1px rgba(229, 9, 20, 0.3);
            border-color: rgba(229, 9, 20, 0.6);
        }
        
        .content-card:hover::before {
            opacity: 1;
        }
        
        .content-thumbnail { 
            width: 100%;
            height: 280px;
            background: linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%);
            position: relative;
            overflow: hidden;
        }
        
        .content-thumbnail::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 70%;
            background: linear-gradient(to top, rgba(0,0,0,0.95) 0%, transparent 100%);
            z-index: 2;
        }
        
        .content-thumbnail img { 
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.7s cubic-bezier(0.4, 0, 0.2, 1);
            filter: brightness(0.9);
        }
        
        .content-card:hover .content-thumbnail img {
            transform: scale(1.2);
            filter: brightness(1.1);
        }
        
        .content-type-badge { 
            position: absolute;
            top: 15px;
            right: 15px;
            background: linear-gradient(135deg, rgba(229, 9, 20, 0.95) 0%, rgba(180, 7, 15, 0.95) 100%);
            color: white;
            padding: 8px 16px;
            border-radius: 25px;
            font-size: 12px;
            font-weight: 800;
            z-index: 3;
            box-shadow: 0 4px 20px rgba(229, 9, 20, 0.5);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .content-info { 
            padding: 25px;
            position: relative;
            z-index: 2;
        }
        
        .content-title { 
            font-size: 14px;
            font-weight: 700;
            margin-bottom: 8px;
            color: #fff;
            line-height: 1.3;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
        }
        
        .content-meta { 
            font-size: 11px;
            color: #b3b3b3;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
            font-weight: 500;
        }
        
        .content-meta span {
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }
        
        .content-actions { 
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .btn { 
            padding: 8px 14px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            font-size: 13px;
            font-weight: 700;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .btn-play { 
            background: linear-gradient(135deg, #e50914 0%, #b0070f 100%);
            color: white;
            flex: 1;
            position: relative;
            overflow: hidden;
        }
        
        .btn-play::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }
        
        .btn-play:hover::before {
            width: 300px;
            height: 300px;
        }
        
        .btn-play:hover {
            background: linear-gradient(135deg, #ff1a1a 0%, #e50914 100%);
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(229, 9, 20, 0.6);
        }
        
        .btn-fav { 
            background: linear-gradient(145deg, rgba(42,42,42,0.8) 0%, rgba(26,26,26,0.8) 100%);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .btn-fav:hover {
            background: linear-gradient(145deg, rgba(52,52,52,0.9) 0%, rgba(36,36,36,0.9) 100%);
            transform: translateY(-3px);
            border-color: rgba(229, 9, 20, 0.5);
            box-shadow: 0 8px 25px rgba(229, 9, 20, 0.3);
        }
        
        .btn-edit { 
            background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
            color: white;
        }
        
        .btn-edit:hover {
            background: linear-gradient(135deg, #0088ff 0%, #007bff 100%);
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0, 123, 255, 0.5);
        }
        
        .btn-delete { 
            background: linear-gradient(135deg, #666 0%, #444 100%);
            color: white;
        }
        
        .btn-delete:hover {
            background: linear-gradient(135deg, #777 0%, #555 100%);
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(100, 100, 100, 0.5);
        }
        
        /* Animations */
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
        
        /* Notification */
        .notification {
            position: fixed;
            top: 100px;
            right: 30px;
            background: linear-gradient(135deg, #e50914 0%, #b0070f 100%);
            color: white;
            padding: 18px 28px;
            border-radius: 15px;
            z-index: 1000;
            animation: slideIn 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 10px 40px rgba(229, 9, 20, 0.6);
            font-weight: 700;
            border: 1px solid rgba(255, 255, 255, 0.3);
            backdrop-filter: blur(10px);
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 12px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(10, 10, 10, 0.5);
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(180deg, #e50914 0%, #b0070f 100%);
            border-radius: 6px;
            border: 2px solid rgba(10, 10, 10, 0.5);
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(180deg, #ff1a1a 0%, #e50914 100%);
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">🎬 Netflux</div>
        <div class="nav">
            <a href="/">Ana Sayfa</a>
            <a href="/movies">Filmler</a>
            <a href="/series">Diziler</a>
            <a href="/favorites">Favoriler</a>
            <a href="/history">İzleme Geçmişi</a>
            <a href="/profile">Profil</a>
            {% if session.user_type == 'admin' %}
            <a href="/add">İçerik Ekle</a>
            {% endif %}
            <a href="/logout">Çıkış ({{ session.user_name }})</a>
        </div>
    </div>
    
    <div class="container">
        <h2 class="section-title">🔥 Popüler İçerikler</h2>
        
        <div class="content-grid">
            {% for content in content %}
            <div class="content-card">
                <div class="content-thumbnail">
                    <img src="{{ content.thumbnail }}" alt="{{ content.title }}" onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjgwIiBoZWlnaHQ9IjE2MCIgdmlld0JveD0iMCAwIDI4MCAxNjAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyODAiIGhlaWdodD0iMTYwIiBmaWxsPSIjMzMzIi8+Cjx0ZXh0IHg9IjE0MCIgeT0iODAiIGZpbGw9IiNjY2MiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiPk5vIEltYWdlPC90ZXh0Pgo8L3N2Zz4K'">
                    <div class="content-type-badge">
                        {% if content.type == 'dizi' %}📺 Dizi{% else %}🎬 Film{% endif %}
                    </div>
                </div>
                <div class="content-info">
                    <div class="content-title">{{ content.title }}</div>
                    <div class="content-meta">
                        {{ content.year }} • {{ content.category }} • {{ content.duration }} dk • ⭐ {{ content.rating }}
                    </div>
                    <div class="content-actions">
                        <a href="/watch/{{ content.id }}" class="btn btn-play">▶ Oynat</a>
                        <button class="btn btn-fav" id="fav-{{ content.id }}" onclick="toggleFavorite({{ content.id }}, this)">🤍 Favori</button>
                        {% if session.user_type == 'admin' %}
                        <a href="/edit/{{ content.id }}" class="btn btn-edit">✏️ Düzenle</a>
                        <button class="btn btn-delete" onclick="deleteContent({{ content.id }}, '{{ content.title }}')">🗑️ Sil</button>
                        {% endif %}
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    
    <script>
        // Load user favorites on page load
        window.addEventListener('DOMContentLoaded', function() {
            fetch('/api/favorites')
                .then(response => response.json())
                .then(data => {
                    data.favorites.forEach(contentId => {
                        const button = document.getElementById('fav-' + contentId);
                        if (button) {
                            button.innerHTML = '❤️ Favori';
                            button.style.background = '#e50914';
                        }
                    });
                });
        });
        
        function toggleFavorite(id, button) {
            fetch('/api/favorite', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({content_id: id})
            })
            .then(response => response.json())
            .then(data => {
                // Change button appearance based on favorite status
                if (data.is_favorite) {
                    button.innerHTML = '❤️ Favori';
                    button.style.background = '#e50914';
                } else {
                    button.innerHTML = '🤍 Favori';
                    button.style.background = '#333';
                }
                
                // Show notification
                showNotification(data.message);
            });
        }
        
        function showNotification(message) {
            // Create notification element
            const notification = document.createElement('div');
            notification.textContent = message;
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: #e50914;
                color: white;
                padding: 15px 25px;
                border-radius: 5px;
                z-index: 1000;
                animation: slideIn 0.3s ease-out;
            `;
            
            document.body.appendChild(notification);
            
            // Remove after 3 seconds
            setTimeout(() => {
                notification.style.animation = 'slideOut 0.3s ease-out';
                setTimeout(() => notification.remove(), 300);
            }, 3000);
        }
        
        function deleteContent(id, title) {
            if (!confirm(`"${title}" içeriğini silmek istediğinizden emin misiniz?`)) {
                return;
            }
            
            fetch(`/api/delete/${id}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'}
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification(data.message);
                    // Remove card from page
                    setTimeout(() => {
                        location.reload();
                    }, 1000);
                } else {
                    alert(data.message);
                }
            })
            .catch(error => {
                alert('Silme işlemi başarısız oldu!');
                console.error('Error:', error);
            });
        }
        
        // Add CSS animations
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(400px); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(400px); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    </script>
</body>
</html>
'''

WATCH_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>{{ content.title }} - Netflux</title>
    <meta charset="utf-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial; background: #000; color: white; overflow: hidden; }
        
        .video-container { position: relative; width: 100%; height: 100vh; background: #000; }
        
        video, iframe { width: 100%; height: 100%; object-fit: contain; border: none; }
        
        .back-btn { 
            position: absolute; top: 20px; left: 20px; background: rgba(0,0,0,0.8); 
            color: white; border: none; padding: 12px 24px; border-radius: 25px; 
            cursor: pointer; font-size: 16px; z-index: 100; transition: all 0.3s;
            font-weight: 500;
        }
        
        .back-btn:hover { background: #e50914; transform: scale(1.05); }
        
        .title-overlay {
            position: absolute; top: 20px; right: 20px; background: rgba(0,0,0,0.8);
            padding: 15px 25px; border-radius: 8px; z-index: 100; max-width: 400px;
        }
        
        .title-text { font-size: 18px; font-weight: bold; margin-bottom: 5px; }
        .meta-text { font-size: 12px; color: #ccc; }
        
        .progress-indicator {
            position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%);
            background: rgba(0,0,0,0.8); padding: 10px 20px; border-radius: 20px;
            z-index: 100; font-size: 14px; display: none;
        }
        
        .progress-indicator.show { display: block; }
        
        /* Resume Dialog - Netflix Style */
        .resume-dialog {
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.85); z-index: 1000;
            display: none; align-items: center; justify-content: center;
            backdrop-filter: blur(5px);
        }
        
        .resume-dialog.show { display: flex; }
        
        .resume-content {
            background: linear-gradient(145deg, #1a1a1a 0%, #2d2d2d 100%);
            border-radius: 15px; padding: 40px; max-width: 500px; width: 90%;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8);
            animation: slideIn 0.3s ease-out;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        @keyframes slideIn {
            from { transform: translateY(-50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        
        .resume-icon {
            text-align: center; font-size: 60px; margin-bottom: 20px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        
        .resume-title {
            font-size: 24px; font-weight: bold; text-align: center;
            margin-bottom: 15px; color: #fff;
        }
        
        .resume-message {
            text-align: center; color: #ccc; font-size: 16px;
            margin-bottom: 10px; line-height: 1.5;
        }
        
        .resume-time {
            text-align: center; font-size: 32px; font-weight: bold;
            color: #e50914; margin: 20px 0; text-shadow: 0 0 20px rgba(229, 9, 20, 0.5);
        }
        
        .resume-buttons {
            display: flex; gap: 15px; margin-top: 30px;
        }
        
        .resume-btn {
            flex: 1; padding: 15px 30px; border: none; border-radius: 8px;
            font-size: 16px; font-weight: 600; cursor: pointer;
            transition: all 0.3s; text-transform: uppercase; letter-spacing: 1px;
        }
        
        .resume-btn-primary {
            background: linear-gradient(135deg, #e50914 0%, #b20710 100%);
            color: white; box-shadow: 0 5px 15px rgba(229, 9, 20, 0.4);
        }
        
        .resume-btn-primary:hover {
            transform: translateY(-2px); box-shadow: 0 8px 25px rgba(229, 9, 20, 0.6);
        }
        
        .resume-btn-secondary {
            background: rgba(255, 255, 255, 0.1); color: white;
            border: 2px solid rgba(255, 255, 255, 0.3);
        }
        
        .resume-btn-secondary:hover {
            background: rgba(255, 255, 255, 0.2); border-color: rgba(255, 255, 255, 0.5);
        }
    </style>
</head>
<body>
    <button class="back-btn" onclick="goBack()">← Geri</button>
    
    <div class="title-overlay">
        <div class="title-text">{{ content.title }}</div>
        <div class="meta-text">{{ content.year }} • {{ content.category }} • {{ content.duration }} dakika</div>
    </div>
    
    <div class="progress-indicator" id="progressIndicator">
        💾 Kaydedildi...
    </div>
    
    <!-- Resume Dialog -->
    <div class="resume-dialog" id="resumeDialog">
        <div class="resume-content">
            <div class="resume-icon">⏯️</div>
            <div class="resume-message">Kaldığınız yer</div>
            <div class="resume-time" id="resumeTimeDisplay">0:00</div>
            <div class="resume-message">Kaldığınız yerden devam etmek ister misiniz?</div>
            <div class="resume-buttons">
                <button class="resume-btn resume-btn-primary" onclick="resumeFromSaved()">
                    ▶️ İzlemeye Devam Et
                </button>
                <button class="resume-btn resume-btn-secondary" onclick="startFromBeginning()">
                    🔄 Baştan Başla
                </button>
            </div>
        </div>
    </div>
    
    <div class="video-container">
        {% if 'youtube.com' in content.video_url or 'youtu.be' in content.video_url %}
            <!-- YouTube Video with API -->
            <div id="player"></div>
            <script src="https://www.youtube.com/iframe_api"></script>
            <script>
                const contentId = {{ content.id }};
                let player;
                let savedProgress = 0;
                let saveInterval;
                
                // Extract video ID from URL
                const videoUrl = "{{ content.video_url }}";
                const videoId = videoUrl.split('/').pop().split('?')[0];
                
                // Load saved progress
                fetch(`/api/progress/${contentId}`)
                    .then(r => r.json())
                    .then(data => {
                        if (data.progress && data.progress > 30) {
                            savedProgress = data.progress;
                            document.getElementById('resumeTimeDisplay').textContent = formatTime(savedProgress);
                            document.getElementById('resumeDialog').classList.add('show');
                        }
                    });
                
                // YouTube API ready
                function onYouTubeIframeAPIReady() {
                    player = new YT.Player('player', {
                        height: '100%',
                        width: '100%',
                        videoId: videoId,
                        playerVars: {
                            'autoplay': 0,
                            'controls': 1,
                            'rel': 0,
                            'modestbranding': 1
                        },
                        events: {
                            'onReady': onPlayerReady,
                            'onStateChange': onPlayerStateChange
                        }
                    });
                }
                
                function onPlayerReady(event) {
                    // Don't auto-play, wait for user choice
                    // Start auto-save every 10 seconds
                    saveInterval = setInterval(() => {
                        saveProgress();
                    }, 10000);
                }
                
                function resumeFromSaved() {
                    document.getElementById('resumeDialog').classList.remove('show');
                    if (player && player.seekTo) {
                        player.seekTo(savedProgress, true);
                        player.playVideo();
                    }
                }
                
                function startFromBeginning() {
                    document.getElementById('resumeDialog').classList.remove('show');
                    savedProgress = 0;
                    if (player && player.playVideo) {
                        player.playVideo();
                    }
                }
                
                function onPlayerStateChange(event) {
                    // Save when paused or ended
                    if (event.data == YT.PlayerState.PAUSED || event.data == YT.PlayerState.ENDED) {
                        saveProgress();
                    }
                }
                
                function saveProgress() {
                    if (player && player.getCurrentTime) {
                        const currentTime = Math.floor(player.getCurrentTime());
                        if (currentTime > 0) {
                            fetch('/api/progress', {
                                method: 'POST',
                                headers: {'Content-Type': 'application/json'},
                                body: JSON.stringify({
                                    content_id: contentId,
                                    progress: currentTime
                                })
                            }).then(() => {
                                showProgressIndicator();
                            });
                        }
                    }
                }
                
                function showProgressIndicator() {
                    const indicator = document.getElementById('progressIndicator');
                    indicator.classList.add('show');
                    setTimeout(() => {
                        indicator.classList.remove('show');
                    }, 2000);
                }
                
                function formatTime(seconds) {
                    const m = Math.floor(seconds / 60);
                    const s = Math.floor(seconds % 60);
                    return `${m}:${s.toString().padStart(2, '0')}`;
                }
                
                function goBack() {
                    saveProgress();
                    clearInterval(saveInterval);
                    window.location.href = '/';
                }
                
                // Save before leaving
                window.addEventListener('beforeunload', () => {
                    saveProgress();
                    clearInterval(saveInterval);
                });
            </script>
        {% else %}
            <!-- MP4 Video -->
            <video id="videoPlayer" controls autoplay>
                <source src="{{ content.video_url }}" type="video/mp4">
                متصفحك لا يدعم تشغيل الفيديو
            </video>
            <script>
                const contentId = {{ content.id }};
                const video = document.getElementById('videoPlayer');
                let savedProgress = 0;
                
                // Load saved progress
                fetch(`/api/progress/${contentId}`)
                    .then(r => r.json())
                    .then(data => {
                        if (data.progress && data.progress > 30) {
                            savedProgress = data.progress;
                            document.getElementById('resumeTimeDisplay').textContent = formatTime(savedProgress);
                            document.getElementById('resumeDialog').classList.add('show');
                        }
                    });
                
                function resumeFromSaved() {
                    document.getElementById('resumeDialog').classList.remove('show');
                    video.currentTime = savedProgress;
                    video.play();
                }
                
                function startFromBeginning() {
                    document.getElementById('resumeDialog').classList.remove('show');
                    video.currentTime = 0;
                    video.play();
                }
                
                function saveProgress() {
                    if (video.currentTime > 0) {
                        fetch('/api/progress', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({
                                content_id: contentId,
                                progress: Math.floor(video.currentTime)
                            })
                        }).then(() => {
                            showProgressIndicator();
                        });
                    }
                }
                
                function showProgressIndicator() {
                    const indicator = document.getElementById('progressIndicator');
                    indicator.classList.add('show');
                    setTimeout(() => {
                        indicator.classList.remove('show');
                    }, 2000);
                }
                
                function formatTime(seconds) {
                    const m = Math.floor(seconds / 60);
                    const s = Math.floor(seconds % 60);
                    return `${m}:${s.toString().padStart(2, '0')}`;
                }
                
                function goBack() {
                    saveProgress();
                    window.location.href = '/';
                }
                
                // Auto-save every 10 seconds
                setInterval(() => {
                    if (!video.paused && video.currentTime > 0) {
                        saveProgress();
                    }
                }, 10000);
                
                // Save on pause
                video.addEventListener('pause', saveProgress);
                
                // Save before leaving
                window.addEventListener('beforeunload', saveProgress);
            </script>
        {% endif %}
    </div>
</body>
</html>
'''

# Initialize data
load_data()

# Print loaded data for debugging
print("\n" + "="*50)
print("📊 LOADED DATA:")
print("="*50)
print(f"👥 Users loaded: {len(users_data)}")
for user in users_data:
    print(f"   - {user['email']} | Password: {user['password']} | Type: {user['type']}")
print(f"🎬 Content loaded: {len(content_data)}")
print("="*50 + "\n")

# ============================================
# FLASK ROUTES
# ============================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and handle login"""
    if request.method == 'GET':
        if 'user_id' in session:
            return redirect('/')
        return render_template_string(LOGIN_TEMPLATE, error=None)
    
    # POST - Handle login
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    
    # Find user
    user = None
    for u in users_data:
        if u['email'] == email and u['password'] == password:
            user = u
            break
    
    if user:
        session['user_id'] = user['id']
        session['user_email'] = user['email']
        session['user_name'] = user['name']
        session['user_type'] = user['type']
        return redirect('/')
    else:
        return render_template_string(LOGIN_TEMPLATE, error='E-posta veya şifre hatalı!')

@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect('/login')

@app.route('/')
@app.route('/index')
def index():
    """Main page"""
    if 'user_id' not in session:
        return redirect('/login')
    return render_template_string(INDEX_TEMPLATE, content=content_data, session=session)

@app.route('/watch/<int:content_id>')
def watch(content_id):
    """Watch content"""
    if 'user_id' not in session:
        return redirect('/')
    
    # Find content
    content = None
    for c in content_data:
        if c['id'] == content_id:
            content = c
            break
    
    if not content:
        return "Content not found", 404
    
    # Add to watch history
    watch_history_data.append({
        'user_id': session['user_id'],
        'content_id': content_id,
        'watched_at': datetime.now().isoformat()
    })
    save_watch_history()
    
    return render_template_string(WATCH_TEMPLATE, content=content)

@app.route('/api/favorites')
def get_favorites():
    """Get user favorites"""
    if 'user_id' not in session:
        return jsonify({'favorites': []})
    
    user_favorites = [f['content_id'] for f in favorites_data if f['user_id'] == session['user_id']]
    return jsonify({'favorites': user_favorites})

@app.route('/api/favorite', methods=['POST'])
def toggle_favorite():
    """Toggle favorite"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.get_json()
    content_id = data.get('content_id')
    user_id = session['user_id']
    
    # Check if already favorite
    existing = None
    for i, f in enumerate(favorites_data):
        if f['user_id'] == user_id and f['content_id'] == content_id:
            existing = i
            break
    
    if existing is not None:
        # Remove from favorites
        favorites_data.pop(existing)
        save_favorites()
        return jsonify({'message': 'Favorilerden çıkarıldı', 'is_favorite': False})
    else:
        # Add to favorites
        favorites_data.append({
            'user_id': user_id,
            'content_id': content_id,
            'added_at': datetime.now().isoformat()
        })
        save_favorites()
        return jsonify({'message': 'Favorilere eklendi', 'is_favorite': True})

@app.route('/api/progress/<int:content_id>')
def get_progress(content_id):
    """Get watch progress"""
    if 'user_id' not in session:
        return jsonify({'progress': 0})
    
    user_id = session['user_id']
    for p in watch_progress_data:
        if p['user_id'] == user_id and p['content_id'] == content_id:
            return jsonify({'progress': p['progress']})
    
    return jsonify({'progress': 0})

@app.route('/api/progress', methods=['POST'])
def save_progress_api():
    """Save watch progress"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.get_json()
    content_id = data.get('content_id')
    progress = data.get('progress', 0)
    user_id = session['user_id']
    
    # Update or create progress
    found = False
    for p in watch_progress_data:
        if p['user_id'] == user_id and p['content_id'] == content_id:
            p['progress'] = progress
            p['updated_at'] = datetime.now().isoformat()
            found = True
            break
    
    if not found:
        watch_progress_data.append({
            'user_id': user_id,
            'content_id': content_id,
            'progress': progress,
            'updated_at': datetime.now().isoformat()
        })
    
    save_watch_progress()
    return jsonify({'success': True})

@app.route('/api/delete/<int:content_id>', methods=['POST'])
def delete_content(content_id):
    """Delete content (admin only)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    if session.get('user_type') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    # Find and remove content
    for i, c in enumerate(content_data):
        if c['id'] == content_id:
            title = c['title']
            content_data.pop(i)
            save_content()
            return jsonify({'success': True, 'message': f'"{title}" silindi'})
    
    return jsonify({'success': False, 'message': 'İçerik bulunamadı'}), 404

@app.route('/movies')
def movies():
    """Movies page"""
    if 'user_id' not in session:
        return redirect('/')
    
    # Filter only movies
    movies_list = [c for c in content_data if c.get('type') == 'film' or c.get('content_type') == 'film']
    return render_template_string(INDEX_TEMPLATE, content=movies_list, session=session)

@app.route('/series')
def series():
    """Series page"""
    if 'user_id' not in session:
        return redirect('/')
    
    # Filter only series
    series_list = [c for c in content_data if c.get('type') == 'dizi' or c.get('content_type') == 'dizi']
    return render_template_string(INDEX_TEMPLATE, content=series_list, session=session)

@app.route('/favorites')
def favorites():
    """Favorites page"""
    if 'user_id' not in session:
        return redirect('/')
    
    # Get user's favorite content IDs
    user_id = session['user_id']
    favorite_ids = [f['content_id'] for f in favorites_data if f['user_id'] == user_id]
    
    # Filter content by favorite IDs
    favorites_list = [c for c in content_data if c['id'] in favorite_ids]
    return render_template_string(INDEX_TEMPLATE, content=favorites_list, session=session)

@app.route('/history')
def history():
    """Watch history page"""
    if 'user_id' not in session:
        return redirect('/')
    
    # Get user's watched content IDs (unique)
    user_id = session['user_id']
    watched_ids = list(set([h['content_id'] for h in watch_history_data if h['user_id'] == user_id]))
    
    # Filter content by watched IDs
    history_list = [c for c in content_data if c['id'] in watched_ids]
    return render_template_string(INDEX_TEMPLATE, content=history_list, session=session)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    """User profile page with edit functionality"""
    if 'user_id' not in session:
        return redirect('/')
    
    success_msg = None
    error_msg = None
    
    # Handle POST request (profile update)
    if request.method == 'POST':
        new_name = request.form.get('name', '').strip()
        new_password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        # Validate
        if not new_name:
            error_msg = "İsim boş olamaz!"
        elif new_password and new_password != confirm_password:
            error_msg = "Şifreler eşleşmiyor!"
        else:
            # Update user data
            user_id = session['user_id']
            for user in users_data:
                if user['id'] == user_id:
                    user['name'] = new_name
                    if new_password:
                        user['password'] = new_password
                    break
            
            # Update session
            session['user_name'] = new_name
            
            # Save to file
            save_users()
            success_msg = "Profil başarıyla güncellendi!"
    
    return render_template_string(PROFILE_TEMPLATE, session=session, success=success_msg, error=error_msg)

# Profile template with edit form
PROFILE_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Profil - Netflux</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0a0a0a;
            color: white;
            min-height: 100vh;
            position: relative;
            overflow-x: hidden;
        }
        
        /* Animated Background */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 50%, rgba(229, 9, 20, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(139, 0, 0, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 40% 20%, rgba(255, 26, 26, 0.1) 0%, transparent 50%),
                linear-gradient(135deg, #0a0a0a 0%, #1a0a0a 50%, #0a0a0a 100%);
            z-index: -2;
            animation: backgroundShift 20s ease infinite;
        }
        
        body::after {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(255,255,255,0.01) 2px, rgba(255,255,255,0.01) 4px),
                repeating-linear-gradient(90deg, transparent, transparent 2px, rgba(255,255,255,0.01) 2px, rgba(255,255,255,0.01) 4px);
            z-index: -1;
            opacity: 0.3;
        }
        
        @keyframes backgroundShift {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.8; }
        }
        
        /* Header */
        .header { 
            background: linear-gradient(180deg, rgba(10,10,10,0.98) 0%, rgba(10,10,10,0.95) 100%);
            padding: 20px 50px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 30px rgba(229, 9, 20, 0.2);
            backdrop-filter: blur(20px);
            position: sticky;
            top: 0;
            z-index: 100;
            border-bottom: 1px solid rgba(229, 9, 20, 0.2);
        }
        
        .logo { 
            font-size: 36px;
            font-weight: 900;
            background: linear-gradient(135deg, #e50914 0%, #ff4444 50%, #e50914 100%);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: shimmer 3s linear infinite;
            letter-spacing: -2px;
            cursor: pointer;
        }
        
        @keyframes shimmer {
            to { background-position: 200% center; }
        }
        
        .nav { 
            display: flex;
            gap: 8px;
            background: rgba(255, 255, 255, 0.03);
            padding: 8px;
            border-radius: 50px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .nav a { 
            color: #e0e0e0;
            text-decoration: none;
            font-weight: 600;
            font-size: 14px;
            padding: 12px 24px;
            border-radius: 50px;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .nav a:hover {
            color: #fff;
            background: linear-gradient(135deg, rgba(229, 9, 20, 0.3) 0%, rgba(229, 9, 20, 0.1) 100%);
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(229, 9, 20, 0.4);
        }
        
        /* Container */
        .container { 
            padding: 50px;
            max-width: 900px;
            margin: 0 auto;
        }
        
        .page-title { 
            font-size: 42px;
            font-weight: 900;
            margin: 30px 0 40px 0;
            text-align: center;
            background: linear-gradient(135deg, #fff 0%, #e50914 50%, #fff 100%);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: shimmer 4s linear infinite;
            letter-spacing: -2px;
        }
        
        /* Cards */
        .profile-card, .info-box { 
            background: linear-gradient(145deg, rgba(30,30,30,0.8) 0%, rgba(42,42,42,0.6) 100%);
            padding: 35px;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
        }
        
        .info-box {
            border-left: 4px solid #e50914;
        }
        
        /* Alerts */
        .alert { 
            padding: 18px 25px;
            border-radius: 15px;
            margin-bottom: 25px;
            text-align: center;
            font-weight: 600;
            backdrop-filter: blur(10px);
            border: 1px solid;
        }
        
        .alert-success { 
            background: linear-gradient(135deg, rgba(40, 167, 69, 0.3) 0%, rgba(40, 167, 69, 0.2) 100%);
            color: #4ade80;
            border-color: rgba(40, 167, 69, 0.4);
        }
        
        .alert-error { 
            background: linear-gradient(135deg, rgba(229, 9, 20, 0.3) 0%, rgba(229, 9, 20, 0.2) 100%);
            color: #ff6b6b;
            border-color: rgba(229, 9, 20, 0.4);
        }
        
        /* Form */
        .form-group { 
            margin-bottom: 25px;
        }
        
        .form-group label { 
            display: block;
            margin-bottom: 10px;
            color: #e0e0e0;
            font-size: 15px;
            font-weight: 600;
        }
        
        .form-group input { 
            width: 100%;
            padding: 16px 20px;
            background: rgba(255, 255, 255, 0.05);
            border: 2px solid rgba(255, 255, 255, 0.1);
            color: white;
            border-radius: 12px;
            font-size: 15px;
            transition: all 0.3s ease;
            font-weight: 500;
        }
        
        .form-group input:focus {
            outline: none;
            background: rgba(255, 255, 255, 0.08);
            border-color: #e50914;
            box-shadow: 0 0 25px rgba(229, 9, 20, 0.3);
            transform: translateY(-2px);
        }
        
        .form-group small { 
            color: #999;
            font-size: 13px;
            display: block;
            margin-top: 8px;
        }
        
        /* Buttons */
        .btn-group { 
            display: flex;
            gap: 15px;
            margin-top: 35px;
        }
        
        .btn { 
            padding: 16px 32px;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            font-size: 15px;
            font-weight: 700;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .btn-primary { 
            background: linear-gradient(135deg, #e50914 0%, #b0070f 100%);
            color: white;
            flex: 1;
            box-shadow: 0 8px 25px rgba(229, 9, 20, 0.4);
        }
        
        .btn-primary:hover {
            background: linear-gradient(135deg, #ff1a1a 0%, #e50914 100%);
            transform: translateY(-3px);
            box-shadow: 0 12px 35px rgba(229, 9, 20, 0.6);
        }
        
        .btn-secondary { 
            background: linear-gradient(145deg, rgba(102,102,102,0.8) 0%, rgba(68,68,68,0.8) 100%);
            color: white;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        }
        
        .btn-secondary:hover {
            background: linear-gradient(145deg, rgba(119,119,119,0.9) 0%, rgba(85,85,85,0.9) 100%);
            transform: translateY(-3px);
        }
        
        /* Info Items */
        .info-item { 
            margin: 18px 0;
            padding: 15px;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 10px;
        }
        
        .info-label { 
            color: #999;
            font-size: 13px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }
        
        .info-value { 
            color: white;
            font-size: 18px;
            font-weight: 700;
        }
        
        h2 {
            font-size: 24px;
            font-weight: 800;
            margin-bottom: 25px;
            color: #fff;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">🎬 Netflux</div>
        <div class="nav">
            <a href="/">Ana Sayfa</a>
            <a href="/movies">Filmler</a>
            <a href="/series">Diziler</a>
            <a href="/profile">Profil</a>
            {% if session.user_type == 'admin' %}
            <a href="/add">İçerik Ekle</a>
            {% endif %}
            <a href="/logout">Çıkış</a>
        </div>
    </div>
    
    <div class="container">
        <h1 class="page-title">👤 Profil Ayarları</h1>
        
        {% if success %}
        <div class="alert alert-success">✅ {{ success }}</div>
        {% endif %}
        
        {% if error %}
        <div class="alert alert-error">❌ {{ error }}</div>
        {% endif %}
        
        <div class="info-box">
            <div class="info-item">
                <div class="info-label">E-posta</div>
                <div class="info-value">{{ session.user_email }}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Hesap Tipi</div>
                <div class="info-value">{{ session.user_type }}</div>
            </div>
        </div>
        
        <div class="profile-card">
            <h2 style="margin-bottom: 20px;">✏️ Profili Düzenle</h2>
            <form method="POST">
                <div class="form-group">
                    <label>👤 İsim</label>
                    <input type="text" name="name" value="{{ session.user_name }}" required>
                </div>
                
                <div class="form-group">
                    <label>🔒 Yeni Şifre (İsteğe bağlı)</label>
                    <input type="password" name="password" placeholder="Değiştirmek istemiyorsanız boş bırakın">
                    <small>Şifrenizi değiştirmek istemiyorsanız bu alanı boş bırakın</small>
                </div>
                
                <div class="form-group">
                    <label>🔒 Yeni Şifre Tekrar</label>
                    <input type="password" name="confirm_password" placeholder="Yeni şifreyi tekrar girin">
                </div>
                
                <div class="btn-group">
                    <button type="submit" class="btn btn-primary">💾 Kaydet</button>
                    <a href="/" class="btn btn-secondary" style="text-align: center; text-decoration: none; line-height: 1.5;">❌ İptal</a>
                </div>
            </form>
        </div>
    </div>
</body>
</html>
'''

@app.route('/add', methods=['GET', 'POST'])
def add_content_page():
    """Add content page (admin only)"""
    if 'user_id' not in session:
        return redirect('/')
    
    if session.get('user_type') != 'admin':
        return "Access denied - Admin only", 403
    
    # Handle POST request (form submission)
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        year = int(request.form.get('year', 2024))
        content_type = request.form.get('content_type', 'film')
        category = request.form.get('category', '').strip()
        video_url = request.form.get('video_url', '').strip()
        image_url = request.form.get('image_url', '').strip()
        rating = float(request.form.get('rating', 7.0))
        duration = int(request.form.get('duration', 90))
        
        # Validate required fields
        if not title or not video_url:
            error_msg = "العنوان ورابط الفيديو مطلوبان!"
            return render_template_string(ADD_CONTENT_TEMPLATE, session=session, error=error_msg)
        
        # Get next ID
        next_id = max([c['id'] for c in content_data]) + 1 if content_data else 1
        
        # Create new content
        new_content = {
            'id': next_id,
            'title': title,
            'description': description,
            'year': year,
            'content_type': content_type,
            'category': category,
            'video_url': video_url,
            'image_url': image_url if image_url else 'https://via.placeholder.com/300x450/1a1a1a/e50914?text=' + title.replace(' ', '+'),
            'rating': rating,
            'duration': duration,
            'created_at': datetime.now().isoformat()
        }
        
        # Add to content data
        content_data.append(new_content)
        
        # Save to file
        save_content()
        
        # Redirect to home with success message
        return redirect('/')
    
    # GET request - show form
    return render_template_string(ADD_CONTENT_TEMPLATE, session=session, error=None)

# Add content template
ADD_CONTENT_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>İçerik Ekle - Netflux</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0a0a0a;
            color: white;
            min-height: 100vh;
            position: relative;
            overflow-x: hidden;
        }
        
        /* Animated Background */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 50%, rgba(229, 9, 20, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(139, 0, 0, 0.15) 0%, transparent 50%),
                linear-gradient(135deg, #0a0a0a 0%, #1a0a0a 50%, #0a0a0a 100%);
            z-index: -1;
        }
        
        /* Header */
        .header { 
            background: linear-gradient(180deg, rgba(10,10,10,0.98) 0%, rgba(10,10,10,0.95) 100%);
            padding: 20px 50px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 30px rgba(229, 9, 20, 0.2);
            backdrop-filter: blur(20px);
            position: sticky;
            top: 0;
            z-index: 100;
            border-bottom: 1px solid rgba(229, 9, 20, 0.2);
        }
        
        .logo { 
            font-size: 32px;
            font-weight: 900;
            background: linear-gradient(135deg, #e50914 0%, #ff4444 50%, #e50914 100%);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: shimmer 3s linear infinite;
            letter-spacing: -2px;
        }
        
        @keyframes shimmer {
            to { background-position: 200% center; }
        }
        
        .nav { 
            display: flex;
            gap: 8px;
            align-items: center;
            background: rgba(255, 255, 255, 0.03);
            padding: 8px;
            border-radius: 50px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .nav a { 
            color: #e0e0e0;
            text-decoration: none;
            font-weight: 600;
            font-size: 14px;
            padding: 12px 24px;
            border-radius: 50px;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .nav a:hover {
            color: #fff;
            background: linear-gradient(135deg, rgba(229, 9, 20, 0.3) 0%, rgba(229, 9, 20, 0.1) 100%);
            transform: translateY(-2px);
        }
        
        /* Container */
        .container { 
            padding: 50px;
            max-width: 900px;
            margin: 0 auto;
        }
        
        .page-title { 
            font-size: 42px;
            font-weight: 900;
            margin-bottom: 15px;
            background: linear-gradient(135deg, #fff 0%, #e50914 50%, #fff 100%);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: shimmer 4s linear infinite;
            letter-spacing: -2px;
        }
        
        .page-subtitle { 
            color: #b3b3b3;
            margin-bottom: 40px;
            font-size: 16px;
        }
        
        /* Form Card */
        .form-card { 
            background: linear-gradient(145deg, rgba(30,30,30,0.8) 0%, rgba(42,42,42,0.6) 100%);
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
        }
        
        .form-group { 
            margin-bottom: 25px;
        }
        
        .form-group label { 
            display: block;
            margin-bottom: 10px;
            color: #e0e0e0;
            font-size: 14px;
            font-weight: 600;
        }
        
        .form-group input, .form-group select, .form-group textarea { 
            width: 100%;
            padding: 14px 18px;
            background: rgba(255, 255, 255, 0.05);
            border: 2px solid rgba(255, 255, 255, 0.1);
            color: white;
            border-radius: 12px;
            font-size: 14px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            transition: all 0.3s ease;
        }
        
        .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
            outline: none;
            border-color: #e50914;
            background: rgba(255, 255, 255, 0.08);
            box-shadow: 0 0 20px rgba(229, 9, 20, 0.3);
        }
        
        .form-group textarea { 
            min-height: 120px;
            resize: vertical;
        }
        
        .form-group small { 
            color: #999;
            font-size: 12px;
            display: block;
            margin-top: 8px;
        }
        
        .form-row { 
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
        }
        
        /* Error Message */
        .error-message { 
            background: linear-gradient(135deg, #e50914 0%, #b0070f 100%);
            color: white;
            padding: 18px 25px;
            border-radius: 15px;
            margin-bottom: 25px;
            text-align: center;
            font-weight: 600;
            box-shadow: 0 5px 20px rgba(229, 9, 20, 0.4);
        }
        
        /* Buttons */
        .btn-group { 
            display: flex;
            gap: 15px;
            margin-top: 35px;
        }
        
        .btn { 
            padding: 16px 32px;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .btn-primary { 
            background: linear-gradient(135deg, #e50914 0%, #b0070f 100%);
            color: white;
            flex: 1;
            box-shadow: 0 5px 20px rgba(229, 9, 20, 0.4);
        }
        
        .btn-primary:hover { 
            transform: translateY(-3px);
            box-shadow: 0 8px 30px rgba(229, 9, 20, 0.6);
        }
        
        .btn-secondary { 
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: 2px solid rgba(255, 255, 255, 0.2);
        }
        
        .btn-secondary:hover { 
            background: rgba(255, 255, 255, 0.15);
            transform: translateY(-2px);
        }
        
        /* Info Box */
        .info-box {
            background: linear-gradient(135deg, rgba(229, 9, 20, 0.1) 0%, rgba(229, 9, 20, 0.05) 100%);
            border-left: 4px solid #e50914;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 30px;
        }
        
        .info-box h3 { 
            color: #e50914;
            margin-bottom: 12px;
            font-size: 16px;
            font-weight: 700;
        }
        
        .info-box ul { 
            margin-left: 20px;
            color: #ccc;
        }
        
        .info-box li { 
            margin: 8px 0;
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">🎬 Netflux</div>
        <div class="nav">
            <a href="/">Ana Sayfa</a>
            <a href="/movies">Filmler</a>
            <a href="/series">Diziler</a>
            <a href="/add">İçerik Ekle</a>
            <a href="/logout">Çıkış</a>
        </div>
    </div>
    
    <div class="container">
        <h1 class="page-title">➕ Yeni İçerik Ekle</h1>
        <p class="page-subtitle">Film veya dizi eklemek için aşağıdaki formu doldurun</p>
        
        {% if error %}
        <div class="error-message">{{ error }}</div>
        {% endif %}
        
        <div class="info-box">
            <h3>📝 Önemli Notlar:</h3>
            <ul>
                <li><strong>YouTube videoları:</strong> https://www.youtube.com/embed/VIDEO_ID formatında olmalı</li>
                <li><strong>MP4 videoları:</strong> Doğrudan .mp4 dosya linki kullanın</li>
                <li><strong>Resim URL:</strong> Boş bırakırsanız otomatik oluşturulur</li>
            </ul>
        </div>
        
        <div class="form-card">
            <form method="POST">
                <div class="form-group">
                    <label>📺 Başlık *</label>
                    <input type="text" name="title" required placeholder="Örn: Recep İvedik 7">
                </div>
                
                <div class="form-group">
                    <label>📝 Açıklama</label>
                    <textarea name="description" placeholder="Film veya dizi hakkında kısa açıklama..."></textarea>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label>📅 Yıl</label>
                        <input type="number" name="year" value="2024" min="1900" max="2030">
                    </div>
                    
                    <div class="form-group">
                        <label>🎬 Tip</label>
                        <select name="content_type">
                            <option value="film">Film</option>
                            <option value="dizi">Dizi</option>
                        </select>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>🎭 Kategori</label>
                    <input type="text" name="category" placeholder="Örn: Komedi, Aksiyon, Drama">
                </div>
                
                <div class="form-group">
                    <label>🎥 Video URL *</label>
                    <input type="url" name="video_url" required placeholder="https://www.youtube.com/embed/... veya https://...video.mp4">
                    <small>YouTube için: https://www.youtube.com/embed/VIDEO_ID</small>
                </div>
                
                <div class="form-group">
                    <label>🖼️ Resim URL (İsteğe bağlı)</label>
                    <input type="url" name="image_url" placeholder="https://...image.jpg">
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label>⭐ Puan (0-10)</label>
                        <input type="number" name="rating" value="7.0" min="0" max="10" step="0.1">
                    </div>
                    
                    <div class="form-group">
                        <label>⏱️ Süre (dakika)</label>
                        <input type="number" name="duration" value="90" min="1">
                    </div>
                </div>
                
                <div class="btn-group">
                    <button type="submit" class="btn btn-primary">✅ İçeriği Ekle</button>
                    <a href="/" class="btn btn-secondary">❌ İptal</a>
                </div>
            </form>
        </div>
    </div>
</body>
</html>
'''


@app.route('/edit/<int:content_id>', methods=['GET', 'POST'])
def edit_content(content_id):
    """Edit content page (admin only)"""
    if 'user_id' not in session:
        return redirect('/')
    
    if session.get('user_type') != 'admin':
        return "Access denied - Admin only", 403
    
    # Find content
    content = None
    for c in content_data:
        if c['id'] == content_id:
            content = c
            break
    
    if not content:
        return "Content not found", 404
    
    # Handle POST request (update)
    if request.method == 'POST':
        content['title'] = request.form.get('title', '').strip()
        content['description'] = request.form.get('description', '').strip()
        content['year'] = int(request.form.get('year', 2024))
        content['type'] = request.form.get('content_type', 'film')
        content['category'] = request.form.get('category', '').strip()
        content['video_url'] = request.form.get('video_url', '').strip()
        image_url = request.form.get('image_url', '').strip()
        if image_url:
            content['image_url'] = image_url
        content['rating'] = float(request.form.get('rating', 7.0))
        content['duration'] = int(request.form.get('duration', 90))
        
        # Save
        save_content()
        return redirect('/')
    
    # GET request - show form
    return render_template_string(EDIT_CONTENT_TEMPLATE, content=content, session=session)

# Edit content template
EDIT_CONTENT_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>İçeriği Düzenle - Netflux</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0a0a0a;
            color: white;
            min-height: 100vh;
            position: relative;
            overflow-x: hidden;
        }
        
        /* Animated Background */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 50%, rgba(229, 9, 20, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(139, 0, 0, 0.15) 0%, transparent 50%),
                linear-gradient(135deg, #0a0a0a 0%, #1a0a0a 50%, #0a0a0a 100%);
            z-index: -1;
        }
        
        /* Header */
        .header { 
            background: linear-gradient(180deg, rgba(10,10,10,0.98) 0%, rgba(10,10,10,0.95) 100%);
            padding: 20px 50px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 30px rgba(229, 9, 20, 0.2);
            backdrop-filter: blur(20px);
            position: sticky;
            top: 0;
            z-index: 100;
            border-bottom: 1px solid rgba(229, 9, 20, 0.2);
        }
        
        .logo { 
            font-size: 32px;
            font-weight: 900;
            background: linear-gradient(135deg, #e50914 0%, #ff4444 50%, #e50914 100%);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: shimmer 3s linear infinite;
            letter-spacing: -2px;
        }
        
        @keyframes shimmer {
            to { background-position: 200% center; }
        }
        
        .nav { 
            display: flex;
            gap: 8px;
            align-items: center;
            background: rgba(255, 255, 255, 0.03);
            padding: 8px;
            border-radius: 50px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .nav a { 
            color: #e0e0e0;
            text-decoration: none;
            font-weight: 600;
            font-size: 14px;
            padding: 12px 24px;
            border-radius: 50px;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .nav a:hover {
            color: #fff;
            background: linear-gradient(135deg, rgba(229, 9, 20, 0.3) 0%, rgba(229, 9, 20, 0.1) 100%);
            transform: translateY(-2px);
        }
        
        /* Container */
        .container { 
            padding: 50px;
            max-width: 900px;
            margin: 0 auto;
        }
        
        .page-title { 
            font-size: 42px;
            font-weight: 900;
            margin-bottom: 15px;
            background: linear-gradient(135deg, #fff 0%, #e50914 50%, #fff 100%);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: shimmer 4s linear infinite;
            letter-spacing: -2px;
        }
        
        .page-subtitle { 
            color: #b3b3b3;
            margin-bottom: 40px;
            font-size: 16px;
        }
        
        /* Form Card */
        .form-card { 
            background: linear-gradient(145deg, rgba(30,30,30,0.8) 0%, rgba(42,42,42,0.6) 100%);
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
        }
        
        .form-group { 
            margin-bottom: 25px;
        }
        
        .form-group label { 
            display: block;
            margin-bottom: 10px;
            color: #e0e0e0;
            font-size: 14px;
            font-weight: 600;
        }
        
        .form-group input, .form-group select, .form-group textarea { 
            width: 100%;
            padding: 14px 18px;
            background: rgba(255, 255, 255, 0.05);
            border: 2px solid rgba(255, 255, 255, 0.1);
            color: white;
            border-radius: 12px;
            font-size: 14px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            transition: all 0.3s ease;
        }
        
        .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
            outline: none;
            border-color: #e50914;
            background: rgba(255, 255, 255, 0.08);
            box-shadow: 0 0 20px rgba(229, 9, 20, 0.3);
        }
        
        .form-group textarea { 
            min-height: 120px;
            resize: vertical;
        }
        
        .form-group small { 
            color: #999;
            font-size: 12px;
            display: block;
            margin-top: 8px;
        }
        
        .form-row { 
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
        }
        
        /* Buttons */
        .btn-group { 
            display: flex;
            gap: 15px;
            margin-top: 35px;
        }
        
        .btn { 
            padding: 16px 32px;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            text-decoration: none;
            text-align: center;
            display: inline-block;
        }
        
        .btn-primary { 
            background: linear-gradient(135deg, #e50914 0%, #b0070f 100%);
            color: white;
            flex: 1;
            box-shadow: 0 5px 20px rgba(229, 9, 20, 0.4);
        }
        
        .btn-primary:hover { 
            transform: translateY(-3px);
            box-shadow: 0 8px 30px rgba(229, 9, 20, 0.6);
        }
        
        .btn-secondary { 
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: 2px solid rgba(255, 255, 255, 0.2);
        }
        
        .btn-secondary:hover { 
            background: rgba(255, 255, 255, 0.15);
            transform: translateY(-2px);
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">🎬 Netflux</div>
        <div class="nav">
            <a href="/">Ana Sayfa</a>
            <a href="/movies">Filmler</a>
            <a href="/series">Diziler</a>
            <a href="/add">İçerik Ekle</a>
            <a href="/logout">Çıkış</a>
        </div>
    </div>
    
    <div class="container">
<!DOCTYPE html>
<html>
<head>
    <title>İçeriği Düzenle - Netflux</title>
    <meta charset="utf-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial; background: #141414; color: white; }
        
        .header { background: #000; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 24px; color: #e50914; font-weight: bold; }
        .nav { display: flex; gap: 20px; }
        .nav a { color: white; text-decoration: none; transition: color 0.3s; }
        .nav a:hover { color: #e50914; }
        
        .container { padding: 40px; max-width: 700px; margin: 0 auto; }
        .page-title { font-size: 32px; margin-bottom: 10px; color: #e50914; }
        .page-subtitle { color: #999; margin-bottom: 30px; }
        
        .form-card { background: #222; padding: 30px; border-radius: 10px; }
        
        .form-group { margin-bottom: 20px; }
        .form-group label { 
            display: block; margin-bottom: 8px; color: #ccc; font-size: 14px; font-weight: 500;
        }
        .form-group input, .form-group select, .form-group textarea { 
            width: 100%; padding: 12px; background: #333; border: 1px solid #444; 
            color: white; border-radius: 5px; font-size: 14px; font-family: Arial;
        }
        .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
            outline: none; border-color: #e50914; background: #3a3a3a;
        }
        .form-group textarea { min-height: 100px; resize: vertical; }
        .form-group small { color: #999; font-size: 12px; display: block; margin-top: 5px; }
        
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        
        .btn-group { display: flex; gap: 15px; margin-top: 30px; }
        .btn { 
            padding: 12px 30px; border: none; border-radius: 5px; 
            cursor: pointer; font-size: 16px; font-weight: 500; transition: all 0.3s;
            text-decoration: none; text-align: center;
        }
        .btn-primary { background: #e50914; color: white; flex: 1; }
        .btn-primary:hover { background: #b0070f; transform: translateY(-2px); }
        .btn-secondary { background: #666; color: white; }
        .btn-secondary:hover { background: #888; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">🎬 Netflux</div>
        <div class="nav">
            <a href="/">Ana Sayfa</a>
            <a href="/add">İçerik Ekle</a>
            <a href="/logout">Çıkış</a>
        </div>
    </div>
    
    <div class="container">
        <h1 class="page-title">✏️ İçeriği Düzenle</h1>
        <p class="page-subtitle">{{ content.title }} - Bilgileri güncelleyin</p>
        
        <div class="form-card">
            <form method="POST">
                <div class="form-group">
                    <label>📺 Başlık *</label>
                    <input type="text" name="title" value="{{ content.title }}" required>
                </div>
                
                <div class="form-group">
                    <label>📝 Açıklama</label>
                    <textarea name="description">{{ content.description }}</textarea>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label>📅 Yıl</label>
                        <input type="number" name="year" value="{{ content.year }}" min="1900" max="2030">
                    </div>
                    
                    <div class="form-group">
                        <label>🎬 Tip</label>
                        <select name="content_type">
                            <option value="film" {% if content.type == 'film' %}selected{% endif %}>Film</option>
                            <option value="dizi" {% if content.type == 'dizi' %}selected{% endif %}>Dizi</option>
                        </select>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>🎭 Kategori</label>
                    <input type="text" name="category" value="{{ content.category }}">
                </div>
                
                <div class="form-group">
                    <label>🎥 Video URL *</label>
                    <input type="url" name="video_url" value="{{ content.video_url }}" required>
                </div>
                
                <div class="form-group">
                    <label>🖼️ Resim URL</label>
                    <input type="url" name="image_url" value="{{ content.image_url }}">
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label>⭐ Puan (0-10)</label>
                        <input type="number" name="rating" value="{{ content.rating }}" min="0" max="10" step="0.1">
                    </div>
                    
                    <div class="form-group">
                        <label>⏱️ Süre (dakika)</label>
                        <input type="number" name="duration" value="{{ content.duration }}" min="1">
                    </div>
                </div>
                
                <div class="btn-group">
                    <button type="submit" class="btn btn-primary">💾 Güncelle</button>
                    <a href="/" class="btn btn-secondary">❌ İptal</a>
                </div>
            </form>
        </div>
    </div>
</body>
</html>
'''

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register page"""
    error = None
    success = None
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        # Validation
        if not name or not email or not password or not confirm_password:
            error = 'Tüm alanları doldurun'
        elif password != confirm_password:
            error = 'Şifreler eşleşmiyor'
        elif len(password) < 6:
            error = 'Şifre en az 6 karakter olmalı'
        elif any(u['email'] == email for u in users_data):
            error = 'Bu e-posta zaten kayıtlı'
        else:
            # Create new user
            new_user = {
                'id': max([u['id'] for u in users_data]) + 1 if users_data else 1,
                'email': email,
                'password': password,
                'name': name,
                'type': 'user'
            }
            users_data.append(new_user)
            save_users()
            success = True
    
    if success:
        register_html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Kayıt Başarılı - Netflux</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: #0a0a0a;
                    color: white;
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                }
                .container { 
                    max-width: 480px;
                    width: 100%;
                    background: linear-gradient(145deg, rgba(30,30,30,0.95) 0%, rgba(42,42,42,0.9) 100%);
                    padding: 60px 50px;
                    border-radius: 25px;
                    box-shadow: 0 30px 90px rgba(0, 0, 0, 0.7);
                    text-align: center;
                }
                .logo { 
                    font-size: 56px;
                    font-weight: 900;
                    background: linear-gradient(135deg, #e50914 0%, #ff4444 50%, #e50914 100%);
                    background-size: 200% auto;
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    margin-bottom: 30px;
                    animation: shimmer 3s linear infinite;
                }
                @keyframes shimmer {
                    to { background-position: 200% center; }
                }
                .success-icon {
                    font-size: 80px;
                    margin: 20px 0;
                }
                h2 {
                    font-size: 28px;
                    margin-bottom: 15px;
                    color: #4CAF50;
                }
                p {
                    color: #b3b3b3;
                    margin-bottom: 30px;
                    font-size: 16px;
                }
                a {
                    display: inline-block;
                    padding: 18px 40px;
                    background: linear-gradient(135deg, #e50914 0%, #b0070f 100%);
                    color: white;
                    text-decoration: none;
                    border-radius: 15px;
                    font-weight: 700;
                    transition: all 0.3s ease;
                }
                a:hover {
                    transform: translateY(-3px);
                    box-shadow: 0 15px 40px rgba(229, 9, 20, 0.7);
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="logo">🎬 Netflux</div>
                <div class="success-icon">✅</div>
                <h2>Kayıt Başarılı!</h2>
                <p>Hesabınız oluşturuldu. Şimdi giriş yapabilirsiniz.</p>
                <a href="/">Giriş Yap</a>
            </div>
        </body>
        </html>
        '''
        return render_template_string(register_html)
    
    register_html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Kayıt Ol - Netflux</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #0a0a0a;
                color: white;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
                position: relative;
                overflow: hidden;
            }
            
            body::before {
                content: '';
                position: fixed;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: 
                    radial-gradient(circle at 30% 40%, rgba(229, 9, 20, 0.25) 0%, transparent 40%),
                    radial-gradient(circle at 70% 60%, rgba(139, 0, 0, 0.2) 0%, transparent 40%);
                animation: rotate 30s linear infinite;
                z-index: -2;
            }
            
            @keyframes rotate {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .container { 
                max-width: 480px;
                width: 100%;
                background: linear-gradient(145deg, rgba(30,30,30,0.95) 0%, rgba(42,42,42,0.9) 100%);
                padding: 60px 50px;
                border-radius: 25px;
                box-shadow: 0 30px 90px rgba(0, 0, 0, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(20px);
                position: relative;
                z-index: 1;
            }
            
            .logo { 
                text-align: center;
                font-size: 56px;
                font-weight: 900;
                background: linear-gradient(135deg, #e50914 0%, #ff4444 50%, #e50914 100%);
                background-size: 200% auto;
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 50px;
                animation: shimmer 3s linear infinite;
                letter-spacing: -3px;
            }
            
            @keyframes shimmer {
                to { background-position: 200% center; }
            }
            
            h2 {
                text-align: center;
                margin-bottom: 35px;
                font-size: 30px;
                font-weight: 800;
                color: #fff;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            .error {
                background: linear-gradient(135deg, rgba(229, 9, 20, 0.25) 0%, rgba(180, 7, 15, 0.25) 100%);
                color: #ff6b6b;
                padding: 18px;
                border-radius: 15px;
                margin-bottom: 25px;
                text-align: center;
                border: 1px solid rgba(229, 9, 20, 0.4);
                font-weight: 600;
            }
            
            input { 
                width: 100%;
                padding: 18px 24px;
                margin: 15px 0;
                background: rgba(255, 255, 255, 0.05);
                border: 2px solid rgba(255, 255, 255, 0.1);
                color: white;
                border-radius: 15px;
                font-size: 15px;
                transition: all 0.4s ease;
                font-weight: 500;
            }
            
            input:focus {
                outline: none;
                background: rgba(255, 255, 255, 0.08);
                border-color: #e50914;
                box-shadow: 0 0 30px rgba(229, 9, 20, 0.4);
                transform: translateY(-2px);
            }
            
            input::placeholder {
                color: rgba(255, 255, 255, 0.4);
            }
            
            button { 
                width: 100%;
                padding: 18px;
                background: linear-gradient(135deg, #e50914 0%, #b0070f 100%);
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 17px;
                font-weight: 800;
                cursor: pointer;
                margin-top: 25px;
                transition: all 0.4s ease;
                box-shadow: 0 10px 30px rgba(229, 9, 20, 0.5);
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            button:hover {
                background: linear-gradient(135deg, #ff1a1a 0%, #e50914 100%);
                transform: translateY(-3px);
                box-shadow: 0 15px 40px rgba(229, 9, 20, 0.7);
            }
            
            .back-link { 
                text-align: center;
                margin-top: 35px;
                color: #b3b3b3;
                font-size: 14px;
                font-weight: 500;
            }
            
            .back-link a { 
                color: #e50914;
                text-decoration: none;
                font-weight: 700;
                transition: all 0.3s ease;
            }
            
            .back-link a:hover {
                color: #ff1a1a;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">🎬 Netflux</div>
            <h2>Kayıt Ol</h2>
            
            {% if error %}
            <div class="error">{{ error }}</div>
            {% endif %}
            
            <form method="POST">
                <input type="text" name="name" placeholder="Adınız Soyadınız" required>
                <input type="email" name="email" placeholder="E-posta adresiniz" required>
                <input type="password" name="password" placeholder="Şifre (en az 6 karakter)" required minlength="6">
                <input type="password" name="confirm_password" placeholder="Şifre Tekrar" required>
                <button type="submit">Kayıt Ol</button>
            </form>
            
            <div class="back-link">
                <p>Zaten hesabınız var mı? <a href="/">Giriş yapın</a></p>
            </div>
        </div>
    </body>
    </html>
    '''
    return render_template_string(register_html, error=error)

# ============================================
# RUN APPLICATION
# ============================================

def get_local_ip():
    """Get local IP address for network access"""
    import socket
    try:
        # Create a socket to get the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "Unable to get IP"

if __name__ == '__main__':
    local_ip = get_local_ip()
    
    print("\n" + "="*70)
    print("🎬 SIMPLE NETFLUX - SERVER STARTED!")
    print("="*70)
    print(f"🖥️  Local Access (This Computer):")
    print(f"   👉 http://localhost:5000")
    print(f"\n📱 Network Access (Other Devices on Same WiFi):")
    print(f"   👉 http://{local_ip}:5000")
    print("\n" + "="*70)
    print("🔐 Admin Login:")
    print("   📧 Email: admin@netflux.com")
    print("   🔑 Password: admin123")
    print("="*70)
    print("\n💡 SHARE THIS LINK WITH OTHERS:")
    print(f"   ➡️  http://{local_ip}:5000")
    print("\n⚠️  Important:")
    print("   • Other devices must be on the same WiFi network")
    print("   • Windows Firewall must allow port 5000")
    print("="*70 + "\n")
    
    app.run(host='0.0.0.0', debug=True, port=5000)

