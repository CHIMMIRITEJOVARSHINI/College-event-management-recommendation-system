import re
from typing import List, Dict, Any

def normalize_text(text: str) -> str:
    """Lowercase and strip text, replacing punctuation with spaces."""
    if not text:
        return ""
    return re.sub(r"[^\w\s]", " ", text.lower())

def stem_token(word: str) -> str:
    """Basic stemming for common plurals in student interests."""
    w = word.strip().lower()
    if w.endswith("ies"):
        return w[:-3] + "y"
    if w.endswith("es") and len(w) > 4:
        return w[:-2]
    if w.endswith("s") and not w.endswith("ss") and len(w) > 3:
        return w[:-1]
    return w

def extract_interest_tokens(interest: str) -> List[str]:
    """Tokenize, stem, and generate keywords for an interest item."""
    interest_clean = normalize_text(interest)
    raw_tokens = [t for t in interest_clean.split() if len(t) > 1 and t not in {"and", "the", "for", "in", "of"}]
    
    stemmed = [stem_token(t) for t in raw_tokens]
    all_tokens = set(raw_tokens + stemmed)

    # Synonyms / related keywords expansion
    if any(k in all_tokens for k in ["ai", "artificial"]):
        all_tokens.update(["ai", "ml", "artificial", "intelligence", "machine", "learning"])
    if any(k in all_tokens for k in ["ml", "machine"]):
        all_tokens.update(["ai", "ml", "machine", "learning"])
    if any(k in all_tokens for k in ["web", "development"]):
        all_tokens.update(["web", "html", "css", "javascript", "react", "fullstack", "backend", "frontend"])
    if any(k in all_tokens for k in ["hackathon", "hackathons"]):
        all_tokens.update(["hackathon", "hackathons", "hack", "hackday"])
    if any(k in all_tokens for k in ["coding", "code"]):
        all_tokens.update(["coding", "code", "programming", "developer", "software"])

    return list(all_tokens)

def calculate_event_match(user_interests: List[str], event: Any) -> Dict[str, Any]:
    """
    Calculate content-based matching score between student interests and an event.
    
    Example:
    Student Interests: AI, Coding, Hackathon
    Event: AI Innovation Hackathon
    Matching Interests: AI ✓, Hackathon ✓
    Score = 2/3 (67% raw) -> Displays 🔥 85% Match
    """
    if not user_interests:
        return {
            "match_score": 0.5,
            "match_percentage": 50,
            "matching_interests": []
        }

    # Prepare event corpus
    name_norm = normalize_text(getattr(event, "name", ""))
    cat_norm = normalize_text(getattr(event, "category", ""))
    desc_norm = normalize_text(getattr(event, "description", ""))
    organizer_norm = normalize_text(getattr(event, "organizer", ""))
    
    corpus_tokens = set(normalize_text(f"{name_norm} {cat_norm} {desc_norm} {organizer_norm}").split())
    stemmed_corpus = {stem_token(t) for t in corpus_tokens}
    all_corpus_tokens = corpus_tokens.union(stemmed_corpus)

    matched_interests = []

    for interest in user_interests:
        clean_interest = interest.strip()
        if not clean_interest:
            continue
            
        interest_tokens = extract_interest_tokens(clean_interest)
        
        # Direct check
        if any(stem_token(tok) in all_corpus_tokens for tok in interest_tokens):
            matched_interests.append(clean_interest)

    valid_interests = [i for i in user_interests if i.strip()]
    total_interests = len(valid_interests) if valid_interests else 1
    raw_score = len(matched_interests) / total_interests

    # Match percentage calculation
    if len(matched_interests) == 0:
        match_percentage = 25
    elif len(matched_interests) == 1:
        match_percentage = 65
    elif len(matched_interests) == 2:
        match_percentage = 85
    elif len(matched_interests) >= 3:
        match_percentage = 95
    else:
        match_percentage = int(min(100, max(30, raw_score * 100)))

    # Extra bonus if category strictly matches
    ev_cat_stem = stem_token(getattr(event, "category", "").lower())
    for m in matched_interests:
        if ev_cat_stem in [stem_token(t) for t in extract_interest_tokens(m)]:
            match_percentage = min(100, match_percentage + 5)
            break

    return {
        "match_score": round(raw_score, 2),
        "match_percentage": match_percentage,
        "matching_interests": matched_interests
    }

def get_recommendations_for_user(user_interests: List[str], events: List[Any]) -> List[Dict[str, Any]]:
    """
    Ranks events based on content match with user interests.
    Returns list of dicts with event object, match score, and matching interests.
    """
    ranked_events = []
    for ev in events:
        match_info = calculate_event_match(user_interests, ev)
        ranked_events.append({
            "event": ev,
            "match_score": match_info["match_score"],
            "match_percentage": match_info["match_percentage"],
            "matching_interests": match_info["matching_interests"]
        })

    # Sort primarily by match_percentage descending, then event id descending
    ranked_events.sort(key=lambda x: (x["match_percentage"], getattr(x["event"], "id", 0)), reverse=True)
    return ranked_events
