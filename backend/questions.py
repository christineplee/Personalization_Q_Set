"""
Contains the 48 profiling questions, the 8 tasks, and the 5 evaluation items
Profiling question set for the Minimal Personalization Study.
~50 items spanning 6 tiers of user information.
"""

PROFILING_QUESTIONS = [
    # ======================================================
    # TIER 1: Validated Psychological Instruments
    # ======================================================

    # Big Five - TIPI (Ten Item Personality Inventory, Gosling et al. 2003)
    {
        "id": "tipi_1",
        "tier": "psychological",
        "instrument": "TIPI",
        "text": "I see myself as extraverted, enthusiastic.",
        "type": "likert7",
        "anchors": ["Disagree strongly", "Agree strongly"],
    },
    {
        "id": "tipi_2",
        "tier": "psychological",
        "instrument": "TIPI",
        "text": "I see myself as critical, quarrelsome.",
        "type": "likert7",
        "anchors": ["Disagree strongly", "Agree strongly"],
    },
    {
        "id": "tipi_3",
        "tier": "psychological",
        "instrument": "TIPI",
        "text": "I see myself as dependable, self-disciplined.",
        "type": "likert7",
        "anchors": ["Disagree strongly", "Agree strongly"],
    },
    {
        "id": "tipi_4",
        "tier": "psychological",
        "instrument": "TIPI",
        "text": "I see myself as anxious, easily upset.",
        "type": "likert7",
        "anchors": ["Disagree strongly", "Agree strongly"],
    },
    {
        "id": "tipi_5",
        "tier": "psychological",
        "instrument": "TIPI",
        "text": "I see myself as open to new experiences, complex.",
        "type": "likert7",
        "anchors": ["Disagree strongly", "Agree strongly"],
    },
    {
        "id": "tipi_6",
        "tier": "psychological",
        "instrument": "TIPI",
        "text": "I see myself as reserved, quiet.",
        "type": "likert7",
        "anchors": ["Disagree strongly", "Agree strongly"],
    },
    {
        "id": "tipi_7",
        "tier": "psychological",
        "instrument": "TIPI",
        "text": "I see myself as sympathetic, warm.",
        "type": "likert7",
        "anchors": ["Disagree strongly", "Agree strongly"],
    },
    {
        "id": "tipi_8",
        "tier": "psychological",
        "instrument": "TIPI",
        "text": "I see myself as disorganized, careless.",
        "type": "likert7",
        "anchors": ["Disagree strongly", "Agree strongly"],
    },
    {
        "id": "tipi_9",
        "tier": "psychological",
        "instrument": "TIPI",
        "text": "I see myself as calm, emotionally stable.",
        "type": "likert7",
        "anchors": ["Disagree strongly", "Agree strongly"],
    },
    {
        "id": "tipi_10",
        "tier": "psychological",
        "instrument": "TIPI",
        "text": "I see myself as conventional, uncreative.",
        "type": "likert7",
        "anchors": ["Disagree strongly", "Agree strongly"],
    },

    # Primals (PI-18 short form, Clifton et al. 2019)
    {
        "id": "primal_good",
        "tier": "psychological",
        "instrument": "Primals",
        "text": "In general, the world is a good place.",
        "type": "likert6",
        "anchors": ["Strongly disagree", "Strongly agree"],
    },
    {
        "id": "primal_safe",
        "tier": "psychological",
        "instrument": "Primals",
        "text": "The world is a safe place.",
        "type": "likert6",
        "anchors": ["Strongly disagree", "Strongly agree"],
    },
    {
        "id": "primal_interesting",
        "tier": "psychological",
        "instrument": "Primals",
        "text": "The world is an interesting place.",
        "type": "likert6",
        "anchors": ["Strongly disagree", "Strongly agree"],
    },
    {
        "id": "primal_alive",
        "tier": "psychological",
        "instrument": "Primals",
        "text": "The world is full of things that are alive and conscious.",
        "type": "likert6",
        "anchors": ["Strongly disagree", "Strongly agree"],
    },

    # Need for Cognition (short, 3 items from Cacioppo & Petty 1982)
    {
        "id": "nfc_1",
        "tier": "psychological",
        "instrument": "NFC",
        "text": "I prefer complex to simple problems.",
        "type": "likert7",
        "anchors": ["Very strongly disagree", "Very strongly agree"],
    },
    {
        "id": "nfc_2",
        "tier": "psychological",
        "instrument": "NFC",
        "text": "I like to have the responsibility of handling a situation that requires a lot of thinking.",
        "type": "likert7",
        "anchors": ["Very strongly disagree", "Very strongly agree"],
    },
    {
        "id": "nfc_3",
        "tier": "psychological",
        "instrument": "NFC",
        "text": "Thinking is not my idea of fun.",
        "type": "likert7",
        "anchors": ["Very strongly disagree", "Very strongly agree"],
    },

    # Regulatory Focus (2 items)
    {
        "id": "regfocus_promo",
        "tier": "psychological",
        "instrument": "RegFocus",
        "text": "I frequently imagine how I will achieve my hopes and aspirations.",
        "type": "likert7",
        "anchors": ["Never or seldom", "Very often"],
    },
    {
        "id": "regfocus_prevent",
        "tier": "psychological",
        "instrument": "RegFocus",
        "text": "I am anxious that I will fall short of my responsibilities and obligations.",
        "type": "likert7",
        "anchors": ["Never or seldom", "Very often"],
    },

    # MBTI-style preference (4 forced choice items)
    {
        "id": "mbti_ei",
        "tier": "psychological",
        "instrument": "MBTI",
        "text": "When you need to recharge, do you prefer:",
        "type": "forced_choice",
        "options": ["Spending time with others", "Spending time alone"],
    },
    {
        "id": "mbti_sn",
        "tier": "psychological",
        "instrument": "MBTI",
        "text": "When learning something new, do you focus more on:",
        "type": "forced_choice",
        "options": ["The specific facts and details", "The big picture and possibilities"],
    },
    {
        "id": "mbti_tf",
        "tier": "psychological",
        "instrument": "MBTI",
        "text": "When making decisions, do you tend to rely more on:",
        "type": "forced_choice",
        "options": ["Logic and objective analysis", "Personal values and how others feel"],
    },
    {
        "id": "mbti_jp",
        "tier": "psychological",
        "instrument": "MBTI",
        "text": "In your daily life, do you prefer:",
        "type": "forced_choice",
        "options": ["Having things planned and settled", "Keeping things open and flexible"],
    },

    # ======================================================
    # TIER 2: Lifestyle & Identity Proxy Questions
    # ======================================================
    {
        "id": "life_morning",
        "tier": "lifestyle",
        "text": "What best describes your morning routine?",
        "type": "forced_choice",
        "options": [
            "Structured — same routine every day",
            "Loose — general pattern but flexible",
            "Improvised — different every day",
        ],
    },
    {
        "id": "life_manual",
        "tier": "lifestyle",
        "text": "When you buy something that requires assembly, do you:",
        "type": "forced_choice",
        "options": [
            "Read the manual first, then assemble",
            "Glance at the manual, mostly figure it out",
            "Dive right in, consult the manual only if stuck",
        ],
    },
    {
        "id": "life_phone",
        "tier": "lifestyle",
        "text": "How would you describe your phone's home screen?",
        "type": "forced_choice",
        "options": [
            "Carefully organized into folders and groups",
            "Somewhat organized, a few apps on the main screen",
            "A bit chaotic — apps wherever they land",
        ],
    },
    {
        "id": "life_restaurant",
        "tier": "lifestyle",
        "text": "At a new restaurant, how do you typically order?",
        "type": "forced_choice",
        "options": [
            "I already know what I want before I sit down",
            "I ask the server what they recommend",
            "I study the full menu carefully before deciding",
        ],
    },
    {
        "id": "life_desk",
        "tier": "lifestyle",
        "text": "How would you describe your desk or workspace right now?",
        "type": "forced_choice",
        "options": [
            "Clean and minimal",
            "Organized but full — everything has a place",
            "Cluttered but I know where things are",
            "Honestly, a mess",
        ],
    },
    {
        "id": "life_seat",
        "tier": "lifestyle",
        "text": "On a flight, do you prefer:",
        "type": "forced_choice",
        "options": ["Window seat", "Aisle seat", "No preference"],
    },
    {
        "id": "life_pet",
        "tier": "lifestyle",
        "text": "Are you more of a:",
        "type": "forced_choice",
        "options": ["Dog person", "Cat person", "Both equally", "Neither"],
    },
    {
        "id": "life_media",
        "tier": "lifestyle",
        "text": "What genre do you gravitate toward in books, podcasts, or shows?",
        "type": "forced_choice",
        "options": [
            "Nonfiction / educational",
            "Mystery / thriller",
            "Comedy / humor",
            "Drama / character-driven stories",
            "Science fiction / fantasy",
        ],
    },

    # ======================================================
    # TIER 3: Perceptual & Projective Tasks
    # ======================================================
    {
        "id": "percept_email",
        "tier": "perceptual",
        "text": "You need to email a colleague about rescheduling a meeting. Which version would you send?",
        "type": "forced_choice",
        "options": [
            "Hi! Hope you're having a great week. I was wondering if we could possibly move our meeting to Thursday? Totally understand if that doesn't work — just let me know what's best for you!",
            "Hi — can we move our meeting to Thursday? Let me know.",
        ],
    },
    {
        "id": "percept_scenario",
        "tier": "perceptual",
        "text": "Your friend asks you to plan a group weekend trip. What do you do?",
        "type": "forced_choice",
        "options": [
            "Propose a full itinerary with options",
            "Suggest a few ideas and let the group decide",
            "Say 'I'm happy with anything — you pick!'",
        ],
    },
    {
        "id": "percept_llm_pref",
        "tier": "perceptual",
        "text": "You ask an AI: 'Should I learn Python or JavaScript first?' Which response do you prefer?",
        "type": "forced_choice",
        "options": [
            "Learn Python first. It's more versatile for beginners, has cleaner syntax, and opens doors to data science, automation, and AI. Start with an online tutorial and build a small project within your first week.",
            "It depends on your goals. Python is great for data science, automation, and general-purpose programming. JavaScript is essential if you're interested in web development. Could you tell me more about what you'd like to build?",
        ],
    },
    {
        "id": "percept_ambiguity",
        "tier": "perceptual",
        "text": "When someone gives you advice that could be interpreted multiple ways, do you usually:",
        "type": "forced_choice",
        "options": [
            "Pick the most likely interpretation and go with it",
            "Ask for clarification before proceeding",
            "Consider multiple interpretations and act on the safest one",
        ],
    },

    # ======================================================
    # TIER 4: Behavioral Micro-Tasks
    # ======================================================
    {
        "id": "behav_describe_day",
        "tier": "behavioral",
        "text": "In 2-3 sentences, describe what you did yesterday.",
        "type": "free_text",
    },
    {
        "id": "behav_topic_rank",
        "tier": "behavioral",
        "text": "Rank these topics by how interesting they are to you (most to least):",
        "type": "ranking",
        "options": [
            "Technology & Innovation",
            "Health & Wellness",
            "History & Culture",
            "Money & Finance",
            "Relationships & Social Life",
            "Nature & Environment",
            "Art & Creativity",
            "Science & Discovery",
        ],
    },

    # ======================================================
    # TIER 5: Values & Trade-Off Questions
    # ======================================================
    {
        "id": "value_advice_style",
        "tier": "values",
        "text": "When getting advice, would you rather:",
        "type": "forced_choice",
        "options": [
            "Hear all the options with pros and cons",
            "Just get the best recommendation",
        ],
    },
    {
        "id": "value_ai_mistake",
        "tier": "values",
        "text": "If an AI assistant made a mistake, would you rather it:",
        "type": "forced_choice",
        "options": [
            "Explain what went wrong and why",
            "Just fix it and move on",
        ],
    },
    {
        "id": "value_speed_accuracy",
        "tier": "values",
        "text": "Would you rather receive:",
        "type": "forced_choice",
        "options": [
            "A good-enough answer right now",
            "A more precise answer that takes longer to think through",
        ],
    },
    {
        "id": "value_learn_format",
        "tier": "values",
        "text": "You have 5 minutes to learn about a topic you know nothing about. You'd prefer:",
        "type": "forced_choice",
        "options": [
            "A concise summary",
            "A story or real-world example",
            "A diagram or visual",
            "A back-and-forth conversation",
        ],
    },
    {
        "id": "value_honest_kind",
        "tier": "values",
        "text": "If you had to choose, is it more important to be:",
        "type": "forced_choice",
        "options": ["Honest", "Kind"],
    },
    {
        "id": "value_certainty",
        "tier": "values",
        "text": "When someone is helping you make a decision, you prefer them to:",
        "type": "forced_choice",
        "options": [
            "Give a confident recommendation even if they're not 100% sure",
            "Share their uncertainty and let you weigh the options",
        ],
    },

    # ======================================================
    # TIER 6: Controversial / Identity Signal Questions
    # ======================================================
    {
        "id": "identity_political",
        "tier": "identity",
        "text": "Where would you place yourself on the political spectrum?",
        "type": "likert7",
        "anchors": ["Very liberal/progressive", "Very conservative"],
    },
    {
        "id": "identity_spiritual",
        "tier": "identity",
        "text": "Which best describes your relationship to religion or spirituality?",
        "type": "forced_choice",
        "options": [
            "Actively religious/practicing",
            "Spiritual but not religious",
            "Not particularly spiritual or religious",
            "Atheist or agnostic",
        ],
    },
    {
        "id": "identity_trust",
        "tier": "identity",
        "text": "Generally speaking, do you think most people can be trusted?",
        "type": "forced_choice",
        "options": [
            "Most people can be trusted",
            "You need to be careful with people",
        ],
    },
    {
        "id": "identity_change",
        "tier": "identity",
        "text": "Which statement resonates more with you?",
        "type": "forced_choice",
        "options": [
            "The world is generally getting better over time",
            "The world is generally getting worse over time",
        ],
    },
    {
        "id": "identity_vehicle",
        "tier": "identity",
        "text": "If you had to choose one vehicle regardless of cost, which would you pick?",
        "type": "forced_choice",
        "options": [
            "Electric sedan (e.g., Tesla)",
            "Pickup truck (e.g., F-150)",
            "SUV (e.g., RAV4)",
            "Compact/hybrid (e.g., Prius)",
            "Luxury car (e.g., BMW)",
        ],
    },
]

# Total: 50 items

TASKS = [
    {
        "id": "task_advice",
        "category": "advice_seeking",
        "prompt": "I've been thinking about switching careers to something more creative, but I'm worried about financial stability. What should I consider?",
    },
    {
        "id": "task_explain",
        "category": "explanation",
        "prompt": "Can you explain how compound interest works and why people say it's so powerful?",
    },
    {
        "id": "task_emotional",
        "category": "emotional",
        "prompt": "I had a really frustrating day at work — I kept sharing ideas in a meeting and they were either ignored or someone else got credit for them. What do you think I should do?",
    },
    {
        "id": "task_planning",
        "category": "planning",
        "prompt": "I want to start eating healthier but I'm busy and not a great cook. Can you help me plan meals for the week?",
    },
    {
        "id": "task_creative",
        "category": "creative",
        "prompt": "I need to write a thank-you note to a mentor who really shaped my career trajectory. Can you help me draft something?",
    },
    {
        "id": "task_recommendation",
        "category": "recommendation",
        "prompt": "I want to understand economics better but I find most textbooks dry. What would you recommend?",
    },
    {
        "id": "task_howto",
        "category": "technical",
        "prompt": "My kitchen faucet has been dripping and it's driving me crazy. How do I fix a leaky faucet?",
    },
    {
        "id": "task_ambiguous",
        "category": "value_laden",
        "prompt": "I'm trying to decide whether to rent or buy a home. What are your thoughts?",
    },
]

EVALUATION_ITEMS = [
    {
        "id": "eval_content",
        "text": "This response focused on what mattered to me.",
        "dimension": "content",
    },
    {
        "id": "eval_tone",
        "text": "The way this was communicated felt right for me.",
        "dimension": "tone",
    },
    {
        "id": "eval_amount",
        "text": "The level of detail was right for me.",
        "dimension": "amount",
    },
    {
        "id": "eval_agency",
        "text": "The level of initiative the assistant took felt right for me.",
        "dimension": "agency",
    },
    {
        "id": "eval_overall",
        "text": "This response felt like it was written for me.",
        "dimension": "overall",
    },
]
