"""
Profiling question set for the Minimal Personalization Study.
80 items across 3 sections:
  Section 1: Dimension Vignettes (20 bipolar 7-point items)
  Section 2: Projective Proxies (12 forced-choice items)
  Section 3: Personality Instruments (18 PI-18 + 30 BFI-2-S = 48 items)
"""

PROFILING_QUESTIONS = [
    # ==============================================================
    # SECTION 1: DIMENSION VIGNETTES
    # All items use a 7-point bipolar scale.
    # ==============================================================

    # ── 1.1 Tone (T1–T5) ─────────────────────────────────────────
    {
        "id": "t1", "tier": "dimension_tone", "section": "vignettes", "dimension": "tone",
        "text": "You ask AI to review a cover letter or help you prepare for an interview for a job you really want.",
        "type": "bipolar7",
        "left_anchor": "Reassuring and supportive",
        "right_anchor": "Brutally honest about weaknesses",
    },
    {
        "id": "t2", "tier": "dimension_tone", "section": "vignettes", "dimension": "tone",
        "text": "You're feeling stressed and mention it to the AI while asking for help with a task.",
        "type": "bipolar7",
        "left_anchor": "Acknowledges how I'm feeling before diving into the task",
        "right_anchor": "Skips the emotional stuff and jumps straight into helping",
    },
    {
        "id": "t3", "tier": "dimension_tone", "section": "vignettes", "dimension": "tone",
        "text": "You're using AI for a work task you will share with colleagues at work.",
        "type": "bipolar7",
        "left_anchor": "Casual and conversational, like talking to a coworker",
        "right_anchor": "Polished and professional throughout",
    },
    {
        "id": "t4", "tier": "dimension_tone", "section": "vignettes", "dimension": "tone",
        "text": "You ask the AI to explain a technical topic that's completely outside your area of expertise.",
        "type": "bipolar7",
        "left_anchor": "Patient and encouraging, checking in along the way",
        "right_anchor": "Straightforward and efficient, no hand-holding",
    },
    {
        "id": "t5", "tier": "dimension_tone", "section": "vignettes", "dimension": "tone",
        "text": "You ask the AI to help you plan an event with many moving parts (venue, guest list, catering, timeline).",
        "type": "bipolar7",
        "left_anchor": "Collaborative and chatty, like brainstorming with a friend",
        "right_anchor": "Systematic and no-nonsense",
    },

    # ── 1.2 Verbosity (V1–V5) ────────────────────────────────────
    {
        "id": "v1", "tier": "dimension_verbosity", "section": "vignettes", "dimension": "verbosity",
        "text": "You ask the AI to explain the potential side effects of a medication your doctor prescribed.",
        "type": "bipolar7",
        "left_anchor": "Just the key points, what I most need to know",
        "right_anchor": "Comprehensive and thorough, cover everything including rare risks",
    },
    {
        "id": "v2", "tier": "dimension_verbosity", "section": "vignettes", "dimension": "verbosity",
        "text": "You ask the AI to explain a process that involves many interconnected steps.",
        "type": "bipolar7",
        "left_anchor": "High-level overview first, I'll ask for more if I need it",
        "right_anchor": "Detailed walkthrough of every step from the start",
    },
    {
        "id": "v3", "tier": "dimension_verbosity", "section": "vignettes", "dimension": "verbosity",
        "text": "You're using the AI to prepare talking points for a presentation to senior leadership.",
        "type": "bipolar7",
        "left_anchor": "Crisp and concise, just the key messages",
        "right_anchor": "Rich with supporting detail and context I can draw from",
    },
    {
        "id": "v4", "tier": "dimension_verbosity", "section": "vignettes", "dimension": "verbosity",
        "text": "You ask the AI about a legal situation you're personally dealing with.",
        "type": "bipolar7",
        "left_anchor": "Brief and focused, just the essentials",
        "right_anchor": "Thorough \u2014 covering nuances, exceptions, and implications",
    },
    {
        "id": "v5", "tier": "dimension_verbosity", "section": "vignettes", "dimension": "verbosity",
        "text": "You're learning to use a new software tool and ask the AI how a specific feature works.",
        "type": "bipolar7",
        "left_anchor": "Short, simple explanation to get me started",
        "right_anchor": "In-depth explanation with background context and examples",
    },

    # ── 1.3 Structure (S1–S5) ────────────────────────────────────
    {
        "id": "s1", "tier": "dimension_structure", "section": "vignettes", "dimension": "structure",
        "text": "You ask the AI to help you compare options for a major financial decision (e.g., mortgage, investment).",
        "type": "bipolar7",
        "left_anchor": "Organized comparison with clear categories and side-by-side layout",
        "right_anchor": "Conversational walkthrough of the pros and cons",
    },
    {
        "id": "s2", "tier": "dimension_structure", "section": "vignettes", "dimension": "structure",
        "text": "You ask the AI to summarize a complicated situation involving multiple people, events, and factors.",
        "type": "bipolar7",
        "left_anchor": "Organized with clear sections separating each element",
        "right_anchor": "Flowing narrative that tells the story in connected prose",
    },
    {
        "id": "s3", "tier": "dimension_structure", "section": "vignettes", "dimension": "structure",
        "text": "You're using the AI to create content that colleagues or clients will read.",
        "type": "bipolar7",
        "left_anchor": "Well-formatted with headers, sections, and visual organization",
        "right_anchor": "Natural, readable prose without heavy formatting",
    },
    {
        "id": "s4", "tier": "dimension_structure", "section": "vignettes", "dimension": "structure",
        "text": "You ask the AI for guidance on how to navigate a difficult conversation with a family member.",
        "type": "bipolar7",
        "left_anchor": "Organized as clear steps or options to consider",
        "right_anchor": "Flowing, conversational response in natural paragraphs",
    },
    {
        "id": "s5", "tier": "dimension_structure", "section": "vignettes", "dimension": "structure",
        "text": "You're researching an unfamiliar professional field and ask the AI to bring you up to speed.",
        "type": "bipolar7",
        "left_anchor": "Structured outline progressing from fundamentals to advanced topics",
        "right_anchor": "Conversational explanation that builds my understanding organically",
    },

    # ── 1.4 Initiative (I1–I5) ───────────────────────────────────
    {
        "id": "i1", "tier": "dimension_initiative", "section": "vignettes", "dimension": "initiative",
        "text": "You ask the AI to help you draft an important email to a client.",
        "type": "bipolar7",
        "left_anchor": "Suggests improvements and flags potential issues I didn't mention",
        "right_anchor": "Writes exactly what I asked for, nothing more",
    },
    {
        "id": "i2", "tier": "dimension_initiative", "section": "vignettes", "dimension": "initiative",
        "text": "You describe a problem to the AI that could be approached in several different ways.",
        "type": "bipolar7",
        "left_anchor": "Explores multiple approaches and recommends one",
        "right_anchor": "Addresses only the specific approach I described",
    },
    {
        "id": "i3", "tier": "dimension_initiative", "section": "vignettes", "dimension": "initiative",
        "text": "You're contributing to a group project and ask the AI for help with your section.",
        "type": "bipolar7",
        "left_anchor": "Points out how my section connects to the broader project and flags inconsistencies",
        "right_anchor": "Focuses only on the specific section I asked about",
    },
    {
        "id": "i4", "tier": "dimension_initiative", "section": "vignettes", "dimension": "initiative",
        "text": "You ask the AI for advice about your personal financial situation.",
        "type": "bipolar7",
        "left_anchor": "Flags related concerns or opportunities I might not have thought of",
        "right_anchor": "Only addresses what I specifically asked about",
    },
    {
        "id": "i5", "tier": "dimension_initiative", "section": "vignettes", "dimension": "initiative",
        "text": "You're new to a hobby and ask the AI a specific beginner question.",
        "type": "bipolar7",
        "left_anchor": "Answers my question and suggests what to explore or learn next",
        "right_anchor": "Just answers my question, clearly and simply",
    },

    # ==============================================================
    # SECTION 2: PROJECTIVE PROXIES (P1–P12)
    # Forced choice between two options.
    # ==============================================================
    {
        "id": "p1", "tier": "projective", "section": "projective",
        "text": "Who do you prefer?",
        "type": "forced_choice",
        "options": ["Someone who's kind but a bit incompetent", "Someone who's blunt but gets things done well"],
    },
    {
        "id": "p2", "tier": "projective", "section": "projective",
        "text": "Which are you more drawn to?",
        "type": "forced_choice",
        "options": ["Cooking \u2014 improvise, taste, adjust", "Baking \u2014 measure precisely, follow the recipe"],
    },
    {
        "id": "p3", "tier": "projective", "section": "projective",
        "text": "You're lost in an unfamiliar city. Which companion do you prefer?",
        "type": "forced_choice",
        "options": ["Someone who takes the lead and suggests detours to cool spots", "Someone who waits for you to decide, then helps you get there"],
    },
    {
        "id": "p4", "tier": "projective", "section": "projective",
        "text": "A friend recommends a movie to you. What do you prefer to hear?",
        "type": "forced_choice",
        "options": ["\"Trust me, just watch it\"", "A full explanation of why they think you'd like it"],
    },
    {
        "id": "p5", "tier": "projective", "section": "projective",
        "text": "When someone pitches you an idea, what do you want to hear first?",
        "type": "forced_choice",
        "options": ["The concrete details \u2014 how it works, what it costs, what the steps are", "The big vision \u2014 what it could become and why it matters"],
    },
    {
        "id": "p6", "tier": "projective", "section": "projective",
        "text": "When explaining your point of view on something, you tend to:",
        "type": "forced_choice",
        "options": ["Give the big picture and let them ask if they need details", "Walk through it step by step so nothing gets missed"],
    },
    {
        "id": "p7", "tier": "projective", "section": "projective",
        "text": "At a restaurant with a group that can't decide what to order, you tend to:",
        "type": "forced_choice",
        "options": ["Let the conversation play out naturally", "Suggest a plan \u2014 \"let's each pick two dishes and share\""],
    },
    {
        "id": "p8", "tier": "projective", "section": "projective",
        "text": "When you hear about a news event, you tend to:",
        "type": "forced_choice",
        "options": ["Accept the headline and move on", "Dig into multiple sources to understand the full picture"],
    },
    {
        "id": "p9", "tier": "projective", "section": "projective",
        "text": "Starting a new project, you prefer to:",
        "type": "forced_choice",
        "options": ["Figure it out as you go \u2014 the shape will emerge", "Define the scope and plan before doing anything"],
    },
    {
        "id": "p10", "tier": "projective", "section": "projective",
        "text": "A friend is upset about a bad day. Your instinct is:",
        "type": "forced_choice",
        "options": ["Listen and validate how they're feeling", "Help them figure out what to do about it"],
    },
    {
        "id": "p11", "tier": "projective", "section": "projective",
        "text": "What type of game appeals to you more?",
        "type": "forced_choice",
        "options": ["One with clear strategy where you can find optimal moves", "One with open-ended play where you create your own story"],
    },
    {
        "id": "p12", "tier": "projective", "section": "projective",
        "text": "If you could have someone around all day, you'd want someone who:",
        "type": "forced_choice",
        "options": ["Makes you better at what you do", "Makes what you do easier"],
    },

    # ==============================================================
    # SECTION 3: PERSONALITY INSTRUMENTS
    # ==============================================================

    # ── 3.1 Primal World Beliefs — PI-18 (Clifton et al. 2019) ───
    # 6-point scale: 1=Strongly Disagree → 6=Strongly Agree
    {"id": "pi_1",  "tier": "primals", "section": "primals", "instrument": "PI-18", "type": "likert6", "text": "In life, there's way more beauty than ugliness.", "anchors": ["Strongly Disagree", "Strongly Agree"]},
    {"id": "pi_2",  "tier": "primals", "section": "primals", "instrument": "PI-18", "type": "likert6", "text": "It often feels like events are happening in order to help me in some way.", "anchors": ["Strongly Disagree", "Strongly Agree"]},
    {"id": "pi_3",  "tier": "primals", "section": "primals", "instrument": "PI-18", "type": "likert6", "text": "I tend to see the world as pretty safe.", "anchors": ["Strongly Disagree", "Strongly Agree"]},
    {"id": "pi_4",  "tier": "primals", "section": "primals", "instrument": "PI-18", "type": "likert6", "text": "What happens in the world is meant to happen.", "anchors": ["Strongly Disagree", "Strongly Agree"]},
    {"id": "pi_5",  "tier": "primals", "section": "primals", "instrument": "PI-18", "type": "likert6", "text": "While some things are worth checking out or exploring further, most things probably aren't worth the effort.", "anchors": ["Strongly Disagree", "Strongly Agree"]},
    {"id": "pi_6",  "tier": "primals", "section": "primals", "instrument": "PI-18", "type": "likert6", "text": "Most things in life are kind of boring.", "anchors": ["Strongly Disagree", "Strongly Agree"]},
    {"id": "pi_7",  "tier": "primals", "section": "primals", "instrument": "PI-18", "type": "likert6", "text": "The world is an abundant place with tons and tons to offer.", "anchors": ["Strongly Disagree", "Strongly Agree"]},
    {"id": "pi_8",  "tier": "primals", "section": "primals", "instrument": "PI-18", "type": "likert6", "text": "No matter where we are or what the topic might be, the world is fascinating.", "anchors": ["Strongly Disagree", "Strongly Agree"]},
    {"id": "pi_9",  "tier": "primals", "section": "primals", "instrument": "PI-18", "type": "likert6", "text": "The world is a somewhat dull place where plenty of things are not that interesting.", "anchors": ["Strongly Disagree", "Strongly Agree"]},
    {"id": "pi_10", "tier": "primals", "section": "primals", "instrument": "PI-18", "type": "likert6", "text": "On the whole, the world is a dangerous place.", "anchors": ["Strongly Disagree", "Strongly Agree"]},
    {"id": "pi_11", "tier": "primals", "section": "primals", "instrument": "PI-18", "type": "likert6", "text": "Instead of being cooperative, the world is a cut-throat and competitive place.", "anchors": ["Strongly Disagree", "Strongly Agree"]},
    {"id": "pi_12", "tier": "primals", "section": "primals", "instrument": "PI-18", "type": "likert6", "text": "Events seem to lack any cosmic or bigger purpose.", "anchors": ["Strongly Disagree", "Strongly Agree"]},
    {"id": "pi_13", "tier": "primals", "section": "primals", "instrument": "PI-18", "type": "likert6", "text": "Most things have a habit of getting worse.", "anchors": ["Strongly Disagree", "Strongly Agree"]},
    {"id": "pi_14", "tier": "primals", "section": "primals", "instrument": "PI-18", "type": "likert6", "text": "The universe needs me for something important.", "anchors": ["Strongly Disagree", "Strongly Agree"]},
    {"id": "pi_15", "tier": "primals", "section": "primals", "instrument": "PI-18", "type": "likert6", "text": "Most things in the world are good.", "anchors": ["Strongly Disagree", "Strongly Agree"]},
    {"id": "pi_16", "tier": "primals", "section": "primals", "instrument": "PI-18", "type": "likert6", "text": "Everything happens for a reason and on purpose.", "anchors": ["Strongly Disagree", "Strongly Agree"]},
    {"id": "pi_17", "tier": "primals", "section": "primals", "instrument": "PI-18", "type": "likert6", "text": "Most things and situations are harmless and totally safe.", "anchors": ["Strongly Disagree", "Strongly Agree"]},
    {"id": "pi_18", "tier": "primals", "section": "primals", "instrument": "PI-18", "type": "likert6", "text": "No matter where we are, incredible beauty is always around us.", "anchors": ["Strongly Disagree", "Strongly Agree"]},

    # ── 3.2 Big Five — BFI-2-S (Soto & John 2017) ───────────────
    # 5-point scale: 1=Disagree Strongly → 5=Agree Strongly
    # Stem: "I am someone who..."
    {"id": "bfi_1",  "tier": "bigfive", "section": "bigfive", "instrument": "BFI-2-S", "type": "likert5", "stem": "I am someone who...", "text": "Tends to be quiet.", "anchors": ["Disagree Strongly", "Agree Strongly"]},
    {"id": "bfi_2",  "tier": "bigfive", "section": "bigfive", "instrument": "BFI-2-S", "type": "likert5", "stem": "I am someone who...", "text": "Is compassionate, has a soft heart.", "anchors": ["Disagree Strongly", "Agree Strongly"]},
    {"id": "bfi_3",  "tier": "bigfive", "section": "bigfive", "instrument": "BFI-2-S", "type": "likert5", "stem": "I am someone who...", "text": "Tends to be disorganized.", "anchors": ["Disagree Strongly", "Agree Strongly"]},
    {"id": "bfi_4",  "tier": "bigfive", "section": "bigfive", "instrument": "BFI-2-S", "type": "likert5", "stem": "I am someone who...", "text": "Worries a lot.", "anchors": ["Disagree Strongly", "Agree Strongly"]},
    {"id": "bfi_5",  "tier": "bigfive", "section": "bigfive", "instrument": "BFI-2-S", "type": "likert5", "stem": "I am someone who...", "text": "Is fascinated by art, music, or literature.", "anchors": ["Disagree Strongly", "Agree Strongly"]},
    {"id": "bfi_6",  "tier": "bigfive", "section": "bigfive", "instrument": "BFI-2-S", "type": "likert5", "stem": "I am someone who...", "text": "Is dominant, acts as a leader.", "anchors": ["Disagree Strongly", "Agree Strongly"]},
    {"id": "bfi_7",  "tier": "bigfive", "section": "bigfive", "instrument": "BFI-2-S", "type": "likert5", "stem": "I am someone who...", "text": "Is sometimes rude to others.", "anchors": ["Disagree Strongly", "Agree Strongly"]},
    {"id": "bfi_8",  "tier": "bigfive", "section": "bigfive", "instrument": "BFI-2-S", "type": "likert5", "stem": "I am someone who...", "text": "Has difficulty getting started on tasks.", "anchors": ["Disagree Strongly", "Agree Strongly"]},
    {"id": "bfi_9",  "tier": "bigfive", "section": "bigfive", "instrument": "BFI-2-S", "type": "likert5", "stem": "I am someone who...", "text": "Tends to feel depressed, blue.", "anchors": ["Disagree Strongly", "Agree Strongly"]},
    {"id": "bfi_10", "tier": "bigfive", "section": "bigfive", "instrument": "BFI-2-S", "type": "likert5", "stem": "I am someone who...", "text": "Has little interest in abstract ideas.", "anchors": ["Disagree Strongly", "Agree Strongly"]},
    {"id": "bfi_11", "tier": "bigfive", "section": "bigfive", "instrument": "BFI-2-S", "type": "likert5", "stem": "I am someone who...", "text": "Is full of energy.", "anchors": ["Disagree Strongly", "Agree Strongly"]},
    {"id": "bfi_12", "tier": "bigfive", "section": "bigfive", "instrument": "BFI-2-S", "type": "likert5", "stem": "I am someone who...", "text": "Assumes the best about people.", "anchors": ["Disagree Strongly", "Agree Strongly"]},
    {"id": "bfi_13", "tier": "bigfive", "section": "bigfive", "instrument": "BFI-2-S", "type": "likert5", "stem": "I am someone who...", "text": "Is reliable, can always be counted on.", "anchors": ["Disagree Strongly", "Agree Strongly"]},
    {"id": "bfi_14", "tier": "bigfive", "section": "bigfive", "instrument": "BFI-2-S", "type": "likert5", "stem": "I am someone who...", "text": "Is emotionally stable, not easily upset.", "anchors": ["Disagree Strongly", "Agree Strongly"]},
    {"id": "bfi_15", "tier": "bigfive", "section": "bigfive", "instrument": "BFI-2-S", "type": "likert5", "stem": "I am someone who...", "text": "Is original, comes up with new ideas.", "anchors": ["Disagree Strongly", "Agree Strongly"]},
    {"id": "bfi_16", "tier": "bigfive", "section": "bigfive", "instrument": "BFI-2-S", "type": "likert5", "stem": "I am someone who...", "text": "Is outgoing, sociable.", "anchors": ["Disagree Strongly", "Agree Strongly"]},
    {"id": "bfi_17", "tier": "bigfive", "section": "bigfive", "instrument": "BFI-2-S", "type": "likert5", "stem": "I am someone who...", "text": "Can be cold and uncaring.", "anchors": ["Disagree Strongly", "Agree Strongly"]},
    {"id": "bfi_18", "tier": "bigfive", "section": "bigfive", "instrument": "BFI-2-S", "type": "likert5", "stem": "I am someone who...", "text": "Keeps things neat and tidy.", "anchors": ["Disagree Strongly", "Agree Strongly"]},
    {"id": "bfi_19", "tier": "bigfive", "section": "bigfive", "instrument": "BFI-2-S", "type": "likert5", "stem": "I am someone who...", "text": "Is relaxed, handles stress well.", "anchors": ["Disagree Strongly", "Agree Strongly"]},
    {"id": "bfi_20", "tier": "bigfive", "section": "bigfive", "instrument": "BFI-2-S", "type": "likert5", "stem": "I am someone who...", "text": "Has few artistic interests.", "anchors": ["Disagree Strongly", "Agree Strongly"]},
    {"id": "bfi_21", "tier": "bigfive", "section": "bigfive", "instrument": "BFI-2-S", "type": "likert5", "stem": "I am someone who...", "text": "Prefers to have others take charge.", "anchors": ["Disagree Strongly", "Agree Strongly"]},
    {"id": "bfi_22", "tier": "bigfive", "section": "bigfive", "instrument": "BFI-2-S", "type": "likert5", "stem": "I am someone who...", "text": "Is respectful, treats others with respect.", "anchors": ["Disagree Strongly", "Agree Strongly"]},
    {"id": "bfi_23", "tier": "bigfive", "section": "bigfive", "instrument": "BFI-2-S", "type": "likert5", "stem": "I am someone who...", "text": "Is persistent, works until the task is finished.", "anchors": ["Disagree Strongly", "Agree Strongly"]},
    {"id": "bfi_24", "tier": "bigfive", "section": "bigfive", "instrument": "BFI-2-S", "type": "likert5", "stem": "I am someone who...", "text": "Feels secure, comfortable with self.", "anchors": ["Disagree Strongly", "Agree Strongly"]},
    {"id": "bfi_25", "tier": "bigfive", "section": "bigfive", "instrument": "BFI-2-S", "type": "likert5", "stem": "I am someone who...", "text": "Is complex, a deep thinker.", "anchors": ["Disagree Strongly", "Agree Strongly"]},
    {"id": "bfi_26", "tier": "bigfive", "section": "bigfive", "instrument": "BFI-2-S", "type": "likert5", "stem": "I am someone who...", "text": "Is less active than other people.", "anchors": ["Disagree Strongly", "Agree Strongly"]},
    {"id": "bfi_27", "tier": "bigfive", "section": "bigfive", "instrument": "BFI-2-S", "type": "likert5", "stem": "I am someone who...", "text": "Tends to find fault with others.", "anchors": ["Disagree Strongly", "Agree Strongly"]},
    {"id": "bfi_28", "tier": "bigfive", "section": "bigfive", "instrument": "BFI-2-S", "type": "likert5", "stem": "I am someone who...", "text": "Can be somewhat careless.", "anchors": ["Disagree Strongly", "Agree Strongly"]},
    {"id": "bfi_29", "tier": "bigfive", "section": "bigfive", "instrument": "BFI-2-S", "type": "likert5", "stem": "I am someone who...", "text": "Is temperamental, gets emotional easily.", "anchors": ["Disagree Strongly", "Agree Strongly"]},
    {"id": "bfi_30", "tier": "bigfive", "section": "bigfive", "instrument": "BFI-2-S", "type": "likert5", "stem": "I am someone who...", "text": "Has little creativity.", "anchors": ["Disagree Strongly", "Agree Strongly"]},
]

# Total: 80 items (20 vignettes + 12 projective + 18 primals + 30 BFI)

TASKS = [
    {"id": "task_advice", "category": "advice_seeking", "prompt": "I have a friend who I feel like has been pulling away lately. I don't know if I did something wrong or if they're just going through their own stuff. How should I handle this?"},
    {"id": "task_explain", "category": "explanation", "prompt": "I always feel tired even when I get a full night's sleep. Why does that happen, and what can I actually do about it?"},
    {"id": "task_emotional", "category": "emotional", "prompt": "I had a really frustrating day at work \u2014 I kept sharing ideas in a meeting and they were either ignored or someone else got credit for them. What do you think I should do?"},
    {"id": "task_planning", "category": "planning", "prompt": "I want to start eating healthier but I'm busy and not a great cook. Can you help me plan meals for the week?"},
    {"id": "task_creative", "category": "creative", "prompt": "I need to write a thank-you message to someone who really helped me through a tough time. Can you help me figure out what to say?"},
    {"id": "task_recommendation", "category": "recommendation", "prompt": "I want to pick up a new hobby but I have no idea where to start. I've got a few hours a week and a modest budget. Any suggestions?"},
    {"id": "task_howto", "category": "technical", "prompt": "I have to give a short presentation at work next week and I'm nervous about public speaking. How should I prepare?"},
    {"id": "task_ambiguous", "category": "value_laden", "prompt": "I've been feeling like I have no work-life balance lately. Everything blurs together and I'm always either working or thinking about work. How do people actually deal with this?"},
]

# ── Attention Checks ──────────────────────────────────────────────
# These are inserted into the profiling flow but NEVER included in
# schedule subsets or LLM prompts. They are used to flag inattentive
# participants for potential exclusion.

ATTENTION_CHECKS = [
    {
        "id": "attn_vignette",
        "tier": "dimension_verbosity",
        "section": "vignettes",
        "type": "bipolar7",
        "text": "This is an attention check. Please select 2 on the scale below.",
        "left_anchor": "Left option",
        "right_anchor": "Right option",
        "is_attention_check": True,
        "expected_answer": 2,
        "insert_after": "v3",
    },
    {
        "id": "attn_projective",
        "tier": "projective",
        "section": "projective",
        "type": "forced_choice",
        "text": "This is an attention check. Please select the second option.",
        "options": ["Do not select this option", "Select this option"],
        "is_attention_check": True,
        "expected_answer": 1,
        "insert_after": "p6",
    },
    {
        "id": "attn_primals",
        "tier": "primals",
        "section": "primals",
        "type": "likert6",
        "text": "To make sure you are reading carefully, please select Strongly Disagree (1) for this item.",
        "anchors": ["Strongly Disagree", "Strongly Agree"],
        "is_attention_check": True,
        "expected_answer": 1,
        "insert_after": "pi_9",
    },
    {
        "id": "attn_eval_1",
        "type": "eval_attention",
        "text": "This is an attention check. Please select 2 on the scale below.",
        "is_attention_check": True,
        "expected_answer": 2,
        "in_task": 1,
    },
    {
        "id": "attn_eval_2",
        "type": "eval_attention",
        "text": "Please read carefully and select 6 for this item.",
        "is_attention_check": True,
        "expected_answer": 6,
        "in_task": 4,
    },
    {
        "id": "attn_eval_3",
        "type": "eval_attention",
        "text": "To confirm you are paying attention, please select 1 below.",
        "is_attention_check": True,
        "expected_answer": 1,
        "in_task": 6,
    },
]

def get_profiling_questions_with_attention_checks():
    """Return profiling questions with attention checks inserted at specified positions."""
    questions = list(PROFILING_QUESTIONS)
    profiling_checks = [ac for ac in ATTENTION_CHECKS if ac.get("insert_after")]
    for check in reversed(profiling_checks):
        anchor = check["insert_after"]
        for i, q in enumerate(questions):
            if q["id"] == anchor:
                questions.insert(i + 1, check)
                break
    return questions

EVALUATION_ITEMS = [
    {"id": "eval_tone", "text": "The tone of this response felt right for me \u2014 not too casual, not too formal, not too warm or too cold.", "dimension": "tone"},
    {"id": "eval_verbosity", "text": "The amount of detail was right for me \u2014 not too brief, not too lengthy.", "dimension": "verbosity"},
    {"id": "eval_structure", "text": "The way the response was organized worked for me \u2014 whether it used lists, paragraphs, sections, or flowing prose.", "dimension": "structure"},
    {"id": "eval_initiative", "text": "The assistant took the right level of initiative \u2014 it didn't overreach, but it also didn't hold back when I would have wanted more.", "dimension": "initiative"},
    {"id": "eval_overall", "text": "Overall, this response felt like it was written for someone like me.", "dimension": "overall"},
]
