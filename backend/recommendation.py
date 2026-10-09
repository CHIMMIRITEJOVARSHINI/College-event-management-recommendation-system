from typing import List, Dict, Any, Tuple
import re

def normalize_text(text: str) -> List[str]:
    """Extracts lowercase tokens from a text string."""
    if not text:
        return []
    # Replace symbols with spaces and split
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
    words = [w.strip() for w in cleaned.split() if len(w.strip()) > 1]
    return words

def get_interest_keywords(interest: str) -> List[str]:
    """Maps user interests to normalized keyword tokens."""
    interest_lower = interest.lower().strip()
    mapping = {
        "ai & machine learning": ["ai", "ml", "machine", "learning", "artificial", "intelligence", "python", "deep"],
        "coding": ["coding", "code", "programming", "developer", "software", "python", "java", "c++"],
        "web development": ["web", "frontend", "backend", "fullstack", "react", "html", "css", "javascript", "node"],
        "sports": ["sports", "football", "cricket", "basketball", "volleyball", "chess", "athletics", "tournament"],
        "cultural": ["cultural", "dance", "music", "drama", "art", "fest", "singing", "fashion", "talent"],
        "music": ["music", "singing", "band", "concert", "orchestra", "instrumental", "vocal"],
        "dance": ["dance", "choreography", "hiphop", "classical", "folk"],
        "technical": ["technical", "tech", "coding", "workshop", "hackathon", "robotics", "cybersecurity"],
        "workshops": ["workshop", "hands-on", "bootcamp", "training", "session"],
        "seminars": ["seminar", "talk", "webinar", "lecture", "keynote", "conference"],
        "hackathons": ["hackathon", "hack", "coding", "innovation", "buildathon"],
        "entrepreneurship": ["entrepreneurship", "startup", "pitch", "business", "incubation", "venture"]
    }
    
    if interest_lower in mapping:
        return mapping[interest_lower]
    
    # Fallback to normalized words of interest
    return normalize_text(interest)

def calculate_recommendation_score(student_interests: List[str], event: Any) -> Tuple[float, int, List[str]]:
    """
    Content-Based Recommendation Engine:
    Compares Student Interests ↔ Event Category, Tags, Title & Description.
    Returns (match_score: float, match_percentage: int, matching_interests: List[str]).
    """
    if not student_interests:
        return 0.0, 0, []

    event_category = getattr(event, 'category', '') or ''
    event_tags_raw = getattr(event, 'tags', '') or ''
    event_name = getattr(event, 'name', '') or ''
    event_desc = getattr(event, 'description', '') or ''

    # Process tags (comma-separated or list)
    if isinstance(event_tags_raw, str):
        event_tags = [t.strip().lower() for t in event_tags_raw.split(',') if t.strip()]
    else:
        event_tags = [str(t).strip().lower() for t in event_tags_raw if str(t).strip()]

    event_text_tokens = set(
        normalize_text(event_category) +
        event_tags +
        normalize_text(event_name) +
        normalize_text(event_desc)
    )

    matching_interests = []
    total_matched_weight = 0.0

    for interest in student_interests:
        interest_cleaned = interest.strip()
        keywords = get_interest_keywords(interest_cleaned)
        
        # Check direct category/tag match
        is_category_match = interest_cleaned.lower() in event_category.lower() or event_category.lower() in interest_cleaned.lower()
        is_tag_match = any(k in event_tags for k in keywords) or any(t in interest_cleaned.lower() for t in event_tags)
        is_keyword_match = any(k in event_text_tokens for k in keywords)

        if is_category_match or is_tag_match or is_keyword_match:
            matching_interests.append(interest_cleaned)
            if is_category_match:
                total_matched_weight += 1.0
            elif is_tag_match:
                total_matched_weight += 0.85
            else:
                total_matched_weight += 0.6

    if not matching_interests:
        return 0.0, 0, []

    # Score calculation relative to number of student interests
    raw_ratio = len(matching_interests) / len(student_interests)
    # Weighted score combining interest coverage and keyword alignment strength
    score = min(1.0, (raw_ratio * 0.5) + (total_matched_weight / max(len(student_interests), 1)) * 0.5)
    
    # Scale score so matched events get clear percentages (e.g. 50% - 100%)
    match_percentage = min(100, max(25, int(score * 100)))

    return score, match_percentage, matching_interests

def recommend_events(student_interests: List[str], events: List[Any]) -> List[Dict[str, Any]]:
    """
    Ranks events based on content similarity with student interests.
    Returns list of event items augmented with match scores.
    """
    scored_events = []
    
    for event in events:
        score, percentage, matches = calculate_recommendation_score(student_interests, event)
        scored_events.append({
            "event": event,
            "match_score": score,
            "match_percentage": percentage,
            "matching_interests": matches
        })

    # Sort descending by match score and then by match percentage
    scored_events.sort(key=lambda x: (x["match_score"], x["match_percentage"]), reverse=True)
    return scored_events
