from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import google.generativeai as genai
import os

app = Flask(__name__)
# Enable CORS for all routes
CORS(app)

# Configure Gemini API
API_KEY = "GEMINI_API_KEY"  # Your API key
genai.configure(api_key=API_KEY)

@app.route('/api/summarize', methods=['POST'])
def summarize():
    print("Received request to /api/summarize")
    data = request.json
    youtube_link = data.get('videoUrl')
    
    print(f"Processing video URL: {youtube_link}")
    
    if not youtube_link:
        return jsonify({"error": "No video URL provided"}), 400
    
    try:
        transcript = transcribe_youtube_video(youtube_link)
        if not transcript:
            return jsonify({"error": "Could not transcribe video"}), 400
        
        print(f"Transcript length: {len(transcript)} characters")
        
        summary = summarize_text(transcript, youtube_link)
        return jsonify({"summary": summary})
    except Exception as e:
        print(f"Error in summarize route: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

def extract_video_id(youtube_link):
    # Handle both youtube.com/watch?v= and youtu.be/ formats
    if "youtube.com/watch?v=" in youtube_link:
        video_id = youtube_link.split("v=")[1].split("&")[0]
    elif "youtu.be/" in youtube_link:
        video_id = youtube_link.split("youtu.be/")[1].split("?")[0]
    else:
        raise ValueError("Invalid YouTube URL format")
    return video_id

def transcribe_youtube_video(youtube_link):
    video_id = extract_video_id(youtube_link)
    print(f"Extracting transcript for video ID: {video_id}")
    
    try:
        # Try to get transcript in the original language
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
    except NoTranscriptFound:
        try:
            # Try fetching auto-generated subtitles
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        except NoTranscriptFound:
            return None
    except TranscriptsDisabled:
        return None
    except Exception as e:
        print(f"Error extracting transcript: {e}")
        return None

    # Convert transcript to full text
    text = ' '.join([entry['text'] for entry in transcript])
    
    # If transcript is too long, truncate it
    if len(text) > 30000:
        text = text[:30000] + "..."
    
    return text

def summarize_text(text, youtube_link):
    try:
        # From your server output, use one of these available models:
        MODEL_NAME = "models/gemini-1.5-flash"  # Use this model from your available list
        
        print(f"Initializing Gemini model: {MODEL_NAME}")
        model = genai.GenerativeModel(MODEL_NAME)
        
        print("Generating content with Gemini")
        
        # Enhanced detailed prompt with specific formatting instructions
        prompt = f"""
Create a comprehensive, detailed summary of the following YouTube video transcript. 
The summary should be very thorough and presented in a well-structured format for easy human understanding.

YouTube Video: {youtube_link}

TRANSCRIPT:
{text}

Please structure your summary as follows:

1. OVERVIEW (2-3 sentences explaining what the video is about)

2. KEY POINTS:
   * List each major point with a bullet
   * Include specific details, facts, and examples
   * Organize related information together
   * Capture all important concepts chronologically
   
3. MAIN THEMES:
   * Identify and explain recurring themes or concepts
   * Explain how they connect to the overall topic

4. NOTABLE QUOTES OR EXAMPLES:
   * Include any memorable quotes, examples, or illustrations used
   
5. CONCLUSION:
   * Summarize the final message or takeaway
   * Explain any call to action or next steps suggested

Make sure the summary is comprehensive, capturing all essential information, and presented in a way that makes it easy for someone who hasn't watched the video to understand the complete content.
"""
        
        # Generate content
        response = model.generate_content(prompt)
        print("Successfully generated content")
        return response.text
    except Exception as e:
        print(f"Gemini API error: {str(e)}")
        # If all else fails, provide a basic summary method
        if "404" in str(e) or "not found" in str(e).lower():
            return f"Error accessing Gemini models. Please try another model. Available models in your system include {MODEL_NAME}."
        return f"Error generating summary: {str(e)}"

if __name__ == "__main__":
    # Make sure we're running on port 5000
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Flask server on port {port}")
    app.run(debug=True, host='0.0.0.0', port=port)