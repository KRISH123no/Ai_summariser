from flask import Flask, render_template, request, jsonify
import requests
import PyPDF2
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptList

app = Flask(__name__)
app.secret_key = 'studyai_secret_key'

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral"

def extract_pdf_text(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text[:2000]
    except Exception as e:
        print(f"PDF error: {e}")
        return None

def get_youtube_transcript(url):
    try:
        video_id = url.split("v=")[1].split("&")[0]
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = None
        try:
            transcript = transcript_list.find_manually_created_transcript(['en'])
        except:
            pass
        if not transcript:
            try:
                transcript = transcript_list.find_generated_transcript(['en'])
            except:
                pass
        if not transcript:
            try:
                for t in transcript_list:
                    transcript = t.translate('en')
                    break
            except:
                pass
        if transcript:
            data = transcript.fetch()
            return " ".join([t['text'] for t in data])[:10000]
        return None
    except Exception as e:
        print(f"YouTube error: {e}")
        return None

def ai_generate(prompt):
    try:
        if len(prompt) > 3000:
            prompt = prompt[:3000]
        
        print(f"Calling Ollama with prompt length: {len(prompt)}")
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_ctx": 4096,
                "temperature": 0.7
            }
        }, timeout=300)
        
        print(f"Ollama status: {response.status_code}")
        if response.status_code == 200:
            return response.json()['response']
        else:
            print(f"Ollama error: {response.text}")
            return "Generation failed"
    except Exception as e:
        print(f"Error: {e}")
        return "Generation failed"

def generate_content(content, features):
    results = {}
    prompt_base = f"Based on the following content:\n\n{content}\n\n"
    
    print(f"=== START generate_content for: {features} ===")
    
    if 'summary' in features:
        print(">>> Generating SUMMARY...")
        results['summary'] = ai_generate(prompt_base + "Provide a clean 200-300 word summary. Just give me the summary, nothing else.")
        print(f"<<< SUMMARY done, length: {len(results.get('summary', ''))}")
    
    if 'notes' in features:
        print(">>> Generating NOTES...")
        results['notes'] = ai_generate(prompt_base + "Create structured notes with headings and bullet points. Make it comprehensive but organized.")
        print(f"<<< NOTES done, length: {len(results.get('notes', ''))}")
    
    if 'quiz' in features:
        print(">>> Generating QUIZ...")
        quiz_text = ai_generate(prompt_base + "Generate 10 multiple choice questions with 4 options each. Format as:\nQ1: question\nA) option1\nB) option2\nC) option3\nD) option4\nCorrect: X\nRepeat for all 10 questions.")
        print(f"<<< QUIZ raw length: {len(quiz_text)}")
        results['quiz'] = parse_quiz(quiz_text)
    
    if 'flashcards' in features:
        print(">>> Generating FLASHCARDS...")
        flashcards_text = ai_generate(prompt_base + "Generate 15 flashcards in question/answer format. Format as:\nQ1: question\nA1: answer\nQ2: question\nA2: answer\netc.")
        print(f"<<< FLASHCARDS raw length: {len(flashcards_text)}")
        results['flashcards'] = parse_flashcards(flashcards_text)
    
    if 'ppt' in features:
        print(">>> Generating PPT...")
        results['ppt'] = ai_generate(prompt_base + "Create a PPT outline with 8-10 slides. Format as:\nSlide 1: Title\n- bullet1\n- bullet2\n- bullet3\netc.")
        print(f"<<< PPT done, length: {len(results.get('ppt', ''))}")
    
    if 'concepts' in features:
        print(">>> Generating CONCEPTS...")
        results['concepts'] = ai_generate(prompt_base + "Extract 10-15 key terms with short definitions. Format as:\nTerm: definition\nTerm: definition\netc.")
        print(f"<<< CONCEPTS done, length: {len(results.get('concepts', ''))}")
    
    print(f"=== END generate_content, results keys: {list(results.keys())} ===")
    return results

def parse_quiz(text):
    questions = []
    blocks = text.split('Q')
    for block in blocks[1:]:
        lines = block.strip().split('\n')
        if len(lines) >= 5:
            q = {'question': lines[0].strip(': '), 'options': [], 'correct': ''}
            for line in lines[1:]:
                if line.strip().startswith('A)') or line.strip().startswith('A:'):
                    q['options'].append(('A', line.strip()[2:].strip()))
                elif line.strip().startswith('B)') or line.strip().startswith('B:'):
                    q['options'].append(('B', line.strip()[2:].strip()))
                elif line.strip().startswith('C)') or line.strip().startswith('C:'):
                    q['options'].append(('C', line.strip()[2:].strip()))
                elif line.strip().startswith('D)') or line.strip().startswith('D:'):
                    q['options'].append(('D', line.strip()[2:].strip()))
                elif 'Correct' in line or 'correct' in line:
                    q['correct'] = line.split(':')[-1].strip().upper()
            if len(q['options']) == 4:
                questions.append(q)
    return questions[:10]

def parse_flashcards(text):
    flashcards = []
    lines = text.split('\n')
    current_q = None
    current_a = None
    for line in lines:
        if line.strip().startswith('Q') and ':' in line:
            if current_q and current_a:
                flashcards.append({'question': current_q, 'answer': current_a})
            current_q = line.split(':', 1)[1].strip()
            current_a = None
        elif line.strip().startswith('A') and ':' in line:
            current_a = line.split(':', 1)[1].strip()
    if current_q and current_a:
        flashcards.append({'question': current_q, 'answer': current_a})
    return flashcards[:15]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result')
def result():
    data = request.args.get('data', '{}')
    import json
    try:
        results = json.loads(data)
    except:
        results = {}
    return render_template('result.html', results=results)

@app.route('/generate', methods=['POST'])
def generate():
    try:
        pdf_file = request.files.get('pdf')
        youtube_url = request.form.get('youtube_url', '').strip()
        features = request.form.getlist('features')

        if not pdf_file and not youtube_url:
            return jsonify({'error': 'Please upload a PDF or enter a YouTube URL'}), 400

        if not features:
            return jsonify({'error': 'Please select at least one feature'}), 400

        content = ""

        if pdf_file and pdf_file.filename:
            content = extract_pdf_text(pdf_file)
            if content is None:
                return jsonify({'error': 'Could not read this PDF. Please try another file'}), 400
        elif youtube_url:
            content = get_youtube_transcript(youtube_url)
            if content is None:
                return jsonify({'error': 'This video has no captions available'}), 400

        if not content.strip():
            return jsonify({'error': 'Could not extract content from the provided source'}), 400

        results = generate_content(content, features)
        print("RESULTS:", results)
        print("FEATURES:", features)
        return render_template('result.html', results=results, features=features)

    except Exception as e:
        print(f"Generation error: {e}")
        return jsonify({'error': f'AI generation failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)