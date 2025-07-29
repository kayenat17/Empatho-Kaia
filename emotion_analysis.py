import re
from collections import Counter

def analyze_emotion(text):
    """
    Enhanced emotion analysis for VoiceLens
    Analyzes text for emotional content and returns detailed emotion analysis
    """
    text = text.lower()
    
    # Emotion keywords with weights
    emotion_keywords = {
        'joy': [
            'happy', 'joy', 'excited', 'thrilled', 'delighted', 'cheerful', 'elated', 'ecstatic',
            'jubilant', 'euphoric', 'blissful', 'content', 'pleased', 'satisfied', 'grateful',
            'blessed', 'fortunate', 'lucky', 'wonderful', 'amazing', 'fantastic', 'brilliant',
            'outstanding', 'excellent', 'superb', 'magnificent', 'splendid', 'glorious',
            'radiant', 'beaming', 'smiling', 'laughing', 'giggling', 'chuckling', 'grinning',
            'overjoyed', 'ecstatic', 'rapturous', 'exhilarated', 'energized', 'vibrant',
            'lively', 'spirited', 'enthusiastic', 'passionate', 'inspired', 'motivated',
            'fulfilled', 'accomplished', 'proud', 'confident', 'empowered', 'strong',
            'successful', 'victorious', 'triumphant', 'celebrating', 'rejoicing', 'blessed'
        ],
        'sadness': [
            'sad', 'depressed', 'melancholy', 'gloomy', 'heartbroken', 'disappointed', 'lonely',
            'miserable', 'unhappy', 'sorrowful', 'grief-stricken', 'mournful', 'tearful',
            'weeping', 'crying', 'sobbing', 'wailing', 'anguished', 'tormented', 'suffering',
            'pained', 'hurt', 'wounded', 'crushed', 'devastated', 'shattered', 'broken',
            'defeated', 'hopeless', 'despairing', 'despondent', 'dejected', 'downcast',
            'discouraged', 'disheartened', 'demoralized', 'defeated', 'overwhelmed',
            'exhausted', 'weary', 'tired', 'fatigued', 'drained', 'empty', 'hollow',
            'numb', 'cold', 'distant', 'withdrawn', 'isolated', 'abandoned', 'rejected',
            'unloved', 'unwanted', 'worthless', 'useless', 'helpless', 'powerless',
            'trapped', 'stuck', 'lost', 'confused', 'bewildered', 'perplexed', 'puzzled', 'down', 'low'
        ],
        'anger': [
            'angry', 'furious', 'irritated', 'annoyed', 'frustrated', 'mad', 'rage',
            'enraged', 'livid', 'fuming', 'seething', 'boiling', 'steaming', 'heated',
            'hot', 'burning', 'raging', 'outraged', 'incensed', 'infuriated', 'exasperated',
            'aggravated', 'bothered', 'disturbed', 'perturbed', 'displeased', 'dissatisfied',
            'disgusted', 'repulsed', 'revolted', 'sickened', 'nauseated', 'offended',
            'insulted', 'humiliated', 'embarrassed', 'ashamed', 'guilty', 'remorseful',
            'regretful', 'bitter', 'resentful', 'vengeful', 'hostile', 'aggressive',
            'violent', 'destructive', 'hateful', 'spiteful', 'malicious', 'cruel',
            'ruthless', 'merciless', 'heartless', 'cold-hearted', 'mean', 'nasty',
            'vicious', 'brutal', 'savage', 'wild', 'uncontrollable', 'unrestrained', 'shut up'
        ],
        'fear': [
            'afraid', 'scared', 'terrified', 'anxious', 'worried', 'nervous', 'panicked',
            'frightened', 'startled', 'shocked', 'alarmed', 'disturbed', 'troubled',
            'concerned', 'uneasy', 'uncomfortable', 'tense', 'stressed', 'strained',
            'overwhelmed', 'overloaded', 'burdened', 'pressured', 'strained', 'stretched',
            'exhausted', 'drained', 'fatigued', 'weary', 'tired', 'worn', 'beaten',
            'defeated', 'overcome', 'conquered', 'subdued', 'suppressed', 'repressed',
            'hidden', 'buried', 'concealed', 'masked', 'disguised', 'pretending',
            'faking', 'lying', 'deceiving', 'misleading', 'confusing', 'puzzling',
            'perplexing', 'bewildering', 'confounding', 'mystifying', 'enigmatic',
            'cryptic', 'obscure', 'unclear', 'vague', 'ambiguous', 'uncertain',
            'unsure', 'doubtful', 'skeptical', 'suspicious', 'distrustful', 'paranoid'
        ],
        'surprise': [
            'surprised', 'shocked', 'amazed', 'astonished', 'stunned', 'startled',
            'bewildered', 'confused', 'puzzled', 'perplexed', 'baffled', 'mystified',
            'confounded', 'flabbergasted', 'gobsmacked', 'dumbfounded', 'speechless',
            'wordless', 'silent', 'quiet', 'still', 'motionless', 'frozen', 'paralyzed',
            'immobilized', 'trapped', 'stuck', 'caught', 'snared', 'ensnared',
            'entangled', 'involved', 'complicated', 'complex', 'intricate', 'elaborate',
            'detailed', 'thorough', 'comprehensive', 'extensive', 'wide-ranging',
            'far-reaching', 'broad', 'wide', 'expansive', 'spacious', 'roomy',
            'generous', 'ample', 'plentiful', 'abundant', 'copious', 'profuse',
            'excessive', 'extreme', 'intense', 'severe', 'serious', 'critical',
            'crucial', 'vital', 'essential', 'important', 'significant', 'meaningful', 'my god'
        ],
        'disgust': [
            'disgusted', 'revolted', 'sickened', 'appalled', 'horrified', 'shocked',
            'dismayed', 'distressed', 'troubled', 'bothered', 'annoyed', 'irritated',
            'aggravated', 'exasperated', 'frustrated', 'angry', 'mad', 'furious',
            'enraged', 'livid', 'fuming', 'seething', 'boiling', 'steaming', 'heated',
            'hot', 'burning', 'raging', 'outraged', 'incensed', 'infuriated',
            'offended', 'insulted', 'humiliated', 'embarrassed', 'ashamed', 'guilty',
            'remorseful', 'regretful', 'bitter', 'resentful', 'vengeful', 'hostile',
            'aggressive', 'violent', 'destructive', 'hateful', 'spiteful', 'malicious',
            'cruel', 'ruthless', 'merciless', 'heartless', 'cold-hearted', 'mean',
            'nasty', 'vicious', 'brutal', 'savage', 'wild', 'uncontrollable', 'get lost'
        ],
        'trust': [
            'trust', 'confident', 'secure', 'safe', 'reliable', 'dependable', 'trustworthy',
            'faithful', 'loyal', 'devoted', 'committed', 'dedicated', 'steadfast',
            'unwavering', 'unshakeable', 'firm', 'solid', 'stable', 'steady', 'strong',
            'powerful', 'mighty', 'forceful', 'influential', 'authoritative', 'commanding',
            'respected', 'admired', 'esteemed', 'honored', 'valued', 'appreciated',
            'cherished', 'treasured', 'beloved', 'dear', 'precious', 'special',
            'unique', 'extraordinary', 'exceptional', 'outstanding', 'remarkable',
            'notable', 'distinguished', 'prominent', 'eminent', 'famous', 'renowned',
            'celebrated', 'acclaimed', 'praised', 'commended', 'lauded', 'applauded',
            'cheered', 'encouraged', 'supported', 'backed', 'endorsed', 'approved',
            'accepted', 'welcomed', 'embraced', 'adopted', 'chosen', 'selected'
        ],
        'anticipation': [
            'excited', 'eager', 'hopeful', 'optimistic', 'looking forward', 'anticipating',
            'expecting', 'waiting', 'preparing', 'planning', 'organizing', 'arranging',
            'scheduling', 'timing', 'coordinating', 'orchestrating', 'managing',
            'directing', 'guiding', 'leading', 'inspiring', 'motivating', 'encouraging',
            'supporting', 'helping', 'assisting', 'aiding', 'facilitating', 'enabling',
            'empowering', 'strengthening', 'building', 'developing', 'growing',
            'expanding', 'extending', 'broadening', 'widening', 'deepening', 'enriching',
            'enhancing', 'improving', 'upgrading', 'advancing', 'progressing',
            'evolving', 'transforming', 'changing', 'adapting', 'adjusting', 'modifying',
            'refining', 'polishing', 'perfecting', 'mastering', 'achieving', 'accomplishing',
            'succeeding', 'winning', 'triumphing', 'prevailing', 'overcoming', 'conquering'
        ]
    }
    
    # Calculate emotion scores
    emotion_scores = {}
    total_words = len(text.split())
    
    for emotion, keywords in emotion_keywords.items():
        score = sum(text.count(keyword) for keyword in keywords)
        if total_words > 0:
            emotion_scores[emotion] = score / total_words
        else:
            emotion_scores[emotion] = 0
    
    # Find dominant emotion
    if max(emotion_scores.values()) == 0:
        dominant_emotion = 'neutral'
        confidence = 0.5
    else:
        dominant_emotion = max(emotion_scores, key=emotion_scores.get)
        confidence = min(emotion_scores[dominant_emotion] * 10, 1.0)  # Scale confidence
    
    # Sentiment analysis
    positive_words = ['good', 'great', 'excellent', 'wonderful', 'amazing', 'beautiful', 'love', 'like']
    negative_words = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'horrible', 'worst', 'sad', 'unhappy', 'depressed', 'hopeless', 'heartbroken', 'miserable', 'lonely', 'rejected', 'abandoned', 'broken', 'empty', 'sorrowful', 'gloomy', 'tearful', 'despondent', 'melancholic', 'downcast', 'discouraged', 'disheartened', 'distraught', 'devastated', 'grief-stricken', 'pitiful', 'mournful', 'anguished', 'anxious', 'ashamed', 'regretful', 'disappointed', 'helpless', 'worthless', 'unloved', 'despairing', 'pained', 'suffering', 'weeping', 'aching', 'tormented', 'misunderstood', 'betrayed', 'isolated', 'overwhelmed', 'fearful', 'insecure', 'tense', 'weary', 'fragile', 'ruined', 'shattered', 'crushed', 'panicked', 'nervous', 'lost', 'numb', 'cold', 'withdrawn', 'defeated', 'downhearted', 'moody', 'grieving', 'distressed', 'upset', 'frustrated', 'angry', 'irritable', 'sulky', 'tragic', 'offended', 'tortured', 'agonized', 'pessimistic', 'remorseful', 'bitter', 'uneasy', 'loathed', 'hated', 'detested', 'suffocated', 'fatigued', 'low', 'sorrowing', 'hurt', 'distrusting', 'alienated', 'dejected', 'downtrodden']

    
    positive_count = sum(text.count(word) for word in positive_words)
    negative_count = sum(text.count(word) for word in negative_words)
    
    if positive_count > negative_count:
        sentiment = 'positive'
    elif negative_count > positive_count:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'
    
    return {
        'dominant_emotion': dominant_emotion,
        'confidence': round(confidence, 2),
        'sentiment': sentiment,
        'emotion_scores': {k: round(v, 3) for k, v in emotion_scores.items()},
        'intensity': 'high' if confidence > 0.7 else 'medium' if confidence > 0.4 else 'low'
    }

def analyze_voice_tone(audio_features=None):
    """
    Placeholder for voice tone analysis
    In a real implementation, this would analyze pitch, tempo, volume, etc.
    """
    # Mock voice tone analysis
    return {
        'pitch': 'medium',
        'tempo': 'normal',
        'volume': 'moderate',
        'tone_confidence': 0.6
    }

def get_combined_analysis(text, voice_tone=None):
    """
    Combines text and voice analysis for comprehensive emotion detection
    """
    text_analysis = analyze_emotion(text)
    voice_analysis = analyze_voice_tone(voice_tone)
    
    # Combine analyses (in real implementation, this would be more sophisticated)
    combined_confidence = (text_analysis['confidence'] + voice_analysis['tone_confidence']) / 2
    
    return {
        'text_analysis': text_analysis,
        'voice_analysis': voice_analysis,
        'combined_confidence': round(combined_confidence, 2),
        'recommendation': get_wellness_recommendation(text_analysis, voice_analysis)
    }

def get_wellness_recommendation(text_analysis, voice_analysis):
    """
    Provides wellness recommendations based on emotion analysis
    """
    emotion = text_analysis['dominant_emotion']
    sentiment = text_analysis['sentiment']
    
    recommendations = {
        'joy': "Great mood! Consider sharing your positive energy with others.",
        'sadness': "It's okay to feel sad. Try talking to a friend or doing something you enjoy.",
        'anger': "Take deep breaths. Consider writing down what's bothering you.",
        'fear': "Remember that feelings of anxiety are temporary. Focus on what you can control.",
        'surprise': "New experiences can be overwhelming. Take time to process your feelings.",
        'disgust': "Acknowledge your feelings without judgment. What triggered this response?",
        'trust': "You're in a good place emotionally. Trust your instincts.",
        'anticipation': "Looking forward to things is healthy! Keep that positive outlook.",
        'neutral': "A calm state of mind. Consider what would bring you joy today."
    }
    
    return recommendations.get(emotion, "Take a moment to reflect on your feelings.")
 