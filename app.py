from flask import Flask, render_template, request, jsonify
import re
import requests
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

class YouTubeNoCookieViewer:
    def __init__(self):
        self.allowed_domains = [
            'youtube.com',
            'www.youtube.com', 
            'youtu.be',
            'm.youtube.com'
        ]
    
    def extract_video_id(self, url):
        """Extract YouTube video ID from various URL formats"""
        try:
            # Parse the URL
            parsed = urlparse(url)
            
            # Check if domain is allowed
            if parsed.netloc not in self.allowed_domains:
                return None
            
            # Different patterns for YouTube URLs
            patterns = [
                r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',  # youtube.com/watch?v=XXX
                r'(?:embed\/)([0-9A-Za-z_-]{11})',  # youtube.com/embed/XXX
                r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'  # youtu.be/XXX
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            
            return None
            
        except Exception as e:
            print(f"Error extracting video ID: {e}")
            return None
    
    def get_video_info(self, video_id):
        """Get basic video information using oEmbed"""
        try:
            oembed_url = f"https://www.youtube.com/oembed"
            params = {
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'format': 'json'
            }
            
            response = requests.get(oembed_url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'title': 'Video Not Available',
                    'thumbnail_url': None
                }
                
        except Exception as e:
            print(f"Error getting video info: {e}")
            return {
                'title': 'Video Information Unavailable',
                'thumbnail_url': None
            }
    
    def generate_no_cookie_url(self, video_id):
        """Generate YouTube no-cookie embed URL"""
        return f"https://www.youtube-nocookie.com/embed/{video_id}"
    
    def process_url(self, url):
        """Main method to process YouTube URL"""
        video_id = self.extract_video_id(url)
        
        if not video_id:
            return {
                'error': 'Invalid YouTube URL or video ID not found',
                'valid': False
            }
        
        # Get video information
        video_info = self.get_video_info(video_id)
        
        # Generate no-cookie URL
        embed_url = self.generate_no_cookie_url(video_id)
        
        return {
            'valid': True,
            'video_id': video_id,
            'embed_url': embed_url,
            'original_url': url,
            'title': video_info.get('title', 'Unknown Title'),
            'thumbnail_url': video_info.get('thumbnail_url'),
            'author_name': video_info.get('author_name', 'Unknown Author')
        }

viewer = YouTubeNoCookieViewer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/embed', methods=['POST'])
def get_embed_info():
    """API endpoint to get no-cookie embed information"""
    url = request.json.get('url', '').strip()
    
    if not url:
        return jsonify({'error': 'No URL provided', 'valid': False})
    
    result = viewer.process_url(url)
    return jsonify(result)

@app.route('/privacy')
def privacy():
    return """
    <h1>Privacy Information</h1>
    <p>This site uses YouTube's no-cookie domain (youtube-nocookie.com) which:</p>
    <ul>
        <li>Does not store visitor data unless they play the video</li>
        <li>Respects user privacy</li>
        <li>Is GDPR compliant for embedded content</li>
    </ul>
    <a href="/">Return to viewer</a>
    """

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
