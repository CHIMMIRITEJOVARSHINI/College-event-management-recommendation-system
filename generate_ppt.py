import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    # Set slide width and height to 16:9 widescreen format
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Color Palette
    COLOR_PRIMARY = RGBColor(30, 58, 138)      # Dark Navy Blue #1E3A8A
    COLOR_SECONDARY = RGBColor(59, 130, 246)   # Royal Blue #3B82F6
    COLOR_ACCENT = RGBColor(245, 158, 11)      # Amber / Gold #F59E0B
    COLOR_BG_CARD = RGBColor(241, 245, 249)    # Light Slate #F1F5F9
    COLOR_TEXT_DARK = RGBColor(30, 41, 59)     # Slate 800 #1E293B
    COLOR_TEXT_MUTED = RGBColor(100, 116, 139) # Slate 500 #64748B
    COLOR_WHITE = RGBColor(255, 255, 255)

    blank_slide_layout = prs.slide_layouts[6]

    def add_header(slide, title_text, category_text="COLLEGE EVENT MANAGEMENT & RECOMMENDATION SYSTEM"):
        # Header background banner
        shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.2))
        shape.fill.solid()
        shape.fill.fore_color.rgb = COLOR_PRIMARY
        shape.line.fill.background()

        # Category text
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.15), Inches(11.7), Inches(0.3))
        tf_cat = cat_box.text_frame
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = COLOR_ACCENT

        # Title text
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.6))
        tf_title = title_box.text_frame
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_WHITE

    def add_card(slide, left, top, width, height, title, content_bullets, bg_color=COLOR_BG_CARD, border_color=COLOR_SECONDARY):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1.5)

        # Title
        tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15), width - Inches(0.4), Inches(0.5))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = COLOR_PRIMARY

        # Content
        tb_body = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.65), width - Inches(0.4), height - Inches(0.8))
        tf_body = tb_body.text_frame
        tf_body.word_wrap = True

        for idx, bullet in enumerate(content_bullets):
            p_b = tf_body.add_paragraph() if idx > 0 else tf_body.paragraphs[0]
            p_b.text = f"• {bullet}"
            p_b.font.size = Pt(13)
            p_b.font.color.rgb = COLOR_TEXT_DARK
            p_b.space_after = Pt(6)

    # ----------------------------------------------------
    # SLIDE 1: Title Slide
    # ----------------------------------------------------
    slide1 = prs.slides.add_slide(blank_slide_layout)
    bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = COLOR_PRIMARY
    bg1.line.fill.background()

    # Title box
    tb1 = slide1.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.333), Inches(2.0))
    tf1 = tb1.text_frame
    p1 = tf1.paragraphs[0]
    p1.text = "College Event Management &\nRecommendation System"
    p1.font.size = Pt(40)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_WHITE
    p1.alignment = PP_ALIGN.LEFT

    # Subtitle
    p1_sub = tf1.add_paragraph()
    p1_sub.text = "A Smart Content-Based Recommendation & Registration Platform for Campus Events"
    p1_sub.font.size = Pt(20)
    p1_sub.font.color.rgb = COLOR_ACCENT
    p1_sub.space_before = Pt(15)

    # Footer details
    tb1_foot = slide1.shapes.add_textbox(Inches(1.0), Inches(5.5), Inches(11.333), Inches(1.0))
    tf1_foot = tb1_foot.text_frame
    p1_f = tf1_foot.paragraphs[0]
    p1_f.text = "Tech Stack: Python | Streamlit | FastAPI | SQLite | SQLAlchemy"
    p1_f.font.size = Pt(14)
    p1_f.font.color.rgb = RGBColor(203, 213, 225)

    # ----------------------------------------------------
    # SLIDE 2: Problem Statement & Motivation
    # ----------------------------------------------------
    slide2 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide2, "1. Problem Statement & Motivation")

    add_card(slide2, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2), 
             "⚠️ Current Challenges", [
                 "Information Fragmentation: Students miss events announced via paper posters, scattered WhatsApp groups, or emails.",
                 "Lack of Personalization: Students receive generic notices regardless of their actual technical or cultural interests.",
                 "Manual Registration Hurdles: Event organizers struggle with paper forms or spreadsheets, leading to duplicate registrations and poor tracking.",
                 "Low Participation Rates: Relevant hackathons and workshops fail to reach interested students."
             ])

    add_card(slide2, Inches(6.8), Inches(1.6), Inches(5.6), Inches(5.2), 
             "💡 Key Motivation", [
                 "Centralized Campus Hub: Single unified web application for all college events, technical workshops, and fests.",
                 "Intelligent Matching: Recommends events based on student profile interests (e.g. AI, Web Dev, Sports).",
                 "Streamlined Administration: Empower organizers to easily publish events, monitor seats, and audit registered students.",
                 "Data-Driven Decisions: Live analytics dashboard for campus event participation."
             ])

    # ----------------------------------------------------
    # SLIDE 3: Proposed Solution Overview
    # ----------------------------------------------------
    slide3 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide3, "2. Proposed Solution")

    add_card(slide3, Inches(0.8), Inches(1.6), Inches(3.6), Inches(5.2),
             "🎓 Student Portal", [
                 "Register & Login securely.",
                 "Custom Profile with interest selection (Coding, AI, Sports, Cultural, etc.).",
                 "Personalized 'Recommended for You' section with Match % badges.",
                 "One-click Event Registration & Cancellation."
             ])

    add_card(slide3, Inches(4.8), Inches(1.6), Inches(3.6), Inches(5.2),
             "🧠 Recommendation Engine", [
                 "Content-Based Filtering algorithm.",
                 "Compares Student Interests ↔ Event Category & Tags.",
                 "Calculates matching score percentage (e.g. 🔥 85% Match).",
                 "Sorts recommended events from highest score to lowest."
             ])

    add_card(slide3, Inches(8.8), Inches(1.6), Inches(3.6), Inches(5.2),
             "📊 Admin Dashboard", [
                 "Role-based secure admin login.",
                 "Full CRUD operations for managing events.",
                 "Live statistics (Total Events, Students, Registrations, Upcoming).",
                 "View and export student registration audit logs."
             ])

    # ----------------------------------------------------
    # SLIDE 4: System Architecture & Workflow
    # ----------------------------------------------------
    slide4 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide4, "3. System Architecture & Tech Stack")

    add_card(slide4, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2),
             "🏗️ System Layer Architecture", [
                 "Frontend UI: Streamlit (Python) with custom CSS styling for modern cards & badges.",
                 "REST API Backend: FastAPI (Python) for asynchronous endpoints and high performance.",
                 "Database Layer: SQLite with SQLAlchemy ORM for clean relational data modeling.",
                 "Auth Engine: SHA-256 password hashing with salt and OAuth2 / JWT access tokens.",
                 "Recommendation Module: Custom content-based NLP matching module."
             ])

    add_card(slide4, Inches(6.8), Inches(1.6), Inches(5.6), Inches(5.2),
             "🛠️ Technology Stack Breakdown", [
                 "Language: Python 3.14",
                 "Web Framework: Streamlit 1.65+",
                 "API Framework: FastAPI 0.142+",
                 "ORM & DB: SQLAlchemy 2.1+ / SQLite3",
                 "Data Processing: Pandas 3.0+",
                 "Security: Passlib, Python-Jose (JWT), Cryptography"
             ])

    # ----------------------------------------------------
    # SLIDE 5: Recommendation Algorithm Detail
    # ----------------------------------------------------
    slide5 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide5, "4. Recommendation Algorithm")

    add_card(slide5, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2),
             "🔍 Content-Based Filtering Approach", [
                 "1. Feature Extraction: Extracts interest tags from student profile (e.g., Coding, AI, Hackathons).",
                 "2. Event Vectorization: Extracts event category, tags, title, and description keywords.",
                 "3. Keyword Normalization: Converts interest mapping to normalized token sets.",
                 "4. Weight Calculation: Gives higher weights to direct Category & Tag matches over general description matches."
             ])

    add_card(slide5, Inches(6.8), Inches(1.6), Inches(5.6), Inches(5.2),
             "📐 Mathematical Matching Formula", [
                 "Match Ratio = (Matched Interests Count) / (Total Student Interests Count)",
                 "Weighted Score = min(1.0, (Match Ratio × 0.5) + (Match Weight Sum / Total Interests) × 0.5)",
                 "Match Percentage = min(100, max(25, round(Weighted Score × 100)))",
                 "Example Output: Student Interests (AI, Coding, Hackathon) + AI Hackathon Event = 🔥 85% Match Badge."
             ])

    # ----------------------------------------------------
    # SLIDE 6: Database Schema & Entity Design
    # ----------------------------------------------------
    slide6 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide6, "5. Database Design & Relational Model")

    add_card(slide6, Inches(0.8), Inches(1.6), Inches(3.6), Inches(5.2),
             "👤 Users Table", [
                 "id (Primary Key)",
                 "name (String)",
                 "email (String, Unique)",
                 "password (Hashed String)",
                 "college & department",
                 "year (String)",
                 "interests (Comma-separated Text)",
                 "role ('student' or 'admin')"
             ])

    add_card(slide6, Inches(4.8), Inches(1.6), Inches(3.6), Inches(5.2),
             "🎯 Events Table", [
                 "id (Primary Key)",
                 "name & description",
                 "category (String)",
                 "date & time",
                 "venue & organizer",
                 "max_participants (Integer)",
                 "registration_deadline",
                 "image (URL Text)",
                 "tags (Comma-separated Text)"
             ])

    add_card(slide6, Inches(8.8), Inches(1.6), Inches(3.6), Inches(5.2),
             "📝 Registrations Table", [
                 "id (Primary Key)",
                 "user_id (Foreign Key -> Users)",
                 "event_id (Foreign Key -> Events)",
                 "registration_date (Timestamp)",
                 "status ('Registered' / 'Cancelled')",
                 "Enforces unique active registration per student per event."
             ])

    # ----------------------------------------------------
    # SLIDE 7: Key Features Demonstration
    # ----------------------------------------------------
    slide7 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide7, "6. Key Application Features")

    add_card(slide7, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2),
             "📱 Student Features", [
                 "Home Dashboard: View Upcoming, Popular, and Recommended events at a glance.",
                 "Search & Filters: Search by keyword, filter by Category, Date, Department, and Venue.",
                 "One-Click Registration: Instantly register with live available seat counters.",
                 "My Registered Events: View active event passes and cancel registrations anytime.",
                 "Profile Management: Dynamically update profile interests to refresh recommendations."
             ])

    add_card(slide7, Inches(6.8), Inches(1.6), Inches(5.6), Inches(5.2),
             "⚙️ Admin / Organizer Features", [
                 "Admin Metrics: Live counts of Total Events, Students, Registrations, and Upcoming Events.",
                 "Event Creation: Publish events with images, capacity, deadlines, and recommendation tags.",
                 "Event Management: Edit event details or delete past events.",
                 "Registration Tracking: Access complete audit table of student registrations."
             ])

    # ----------------------------------------------------
    # SLIDE 8: API Endpoints & Security
    # ----------------------------------------------------
    slide8 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide8, "7. API Architecture & Security")

    add_card(slide8, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2),
             "🔌 Core REST API Endpoints", [
                 "POST /api/auth/register & /login - Authenticate users",
                 "GET /api/events - Search & filter events",
                 "GET /api/recommendations - Personalized ranked recommendations",
                 "POST /api/events/{id}/register - Register student for event",
                 "POST /api/events/{id}/cancel - Cancel event registration",
                 "GET /api/admin/stats - Admin dashboard overview metrics"
             ])

    add_card(slide8, Inches(6.8), Inches(1.6), Inches(5.6), Inches(5.2),
             "🔒 Security & Robustness", [
                 "SHA-256 Password Hashing: Ensures plain passwords are never stored in plaintext.",
                 "JWT Bearer Token Security: Protects student and admin routes.",
                 "Duplicate Registration Guard: Database-level and API-level check preventing double registration.",
                 "Capacity Limit Enforcement: Prevents registrations beyond maximum seat capacity."
             ])

    # ----------------------------------------------------
    # SLIDE 9: System Results & Screenshots Overview
    # ----------------------------------------------------
    slide9 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide9, "8. Results & System Performance")

    add_card(slide9, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2),
             "📈 System Performance Metrics", [
                 "Recommendation Speed: Sub-10ms match calculation for candidate events.",
                 "Database Efficiency: SQLite query execution in <5ms.",
                 "Responsive Web UI: Instant render with Streamlit component state.",
                 "Scalability: Decoupled REST API enables mobile or web client integration."
             ])

    add_card(slide9, Inches(6.8), Inches(1.6), Inches(5.6), Inches(5.2),
             "✨ User Experience Highlights", [
                 "Intuitive Dashboard: College-themed aesthetic with modern card layouts.",
                 "Clear Match Badges: Visual match percentages (e.g. 🔥 85% Match) boost student engagement.",
                 "Zero Training Required: Clean navigation tabs for students and organizers."
             ])

    # ----------------------------------------------------
    # SLIDE 10: Conclusion & Future Enhancements
    # ----------------------------------------------------
    slide10 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide10, "9. Conclusion & Future Enhancements")

    add_card(slide10, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2),
             "✅ Conclusion", [
                 "Successfully developed a full-stack College Event Management & Recommendation System.",
                 "Solved information gap by providing personalized content-based event discovery for students.",
                 "Empowered college admins with streamlined event creation, seat tracking, and registration management.",
                 "Demonstrates high practical value for campus mini-projects and real-world college deployment."
             ])

    add_card(slide10, Inches(6.8), Inches(1.6), Inches(5.6), Inches(5.2),
             "🔮 Future Enhancements", [
                 "Mobile App Integration: React Native / Flutter mobile client for push notifications.",
                 "Collaborative Filtering: Combine user interest matching with peer registration patterns.",
                 "QR Code Event Check-In: Generate QR tickets for instant venue attendance scanning.",
                 "Automated Certificate Generation: Issue digital participation certificates post-event."
             ])

    output_path = os.path.join(os.path.dirname(__file__), "College_Event_Management_System.pptx")
    prs.save(output_path)
    print(f"Presentation saved successfully to {output_path}")
    return output_path

if __name__ == "__main__":
    create_presentation()
