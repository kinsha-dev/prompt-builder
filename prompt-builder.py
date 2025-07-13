

import os
import re

def get_categories(template_dir):
    """Gets a list of available categories."""
    return [d for d in os.listdir(template_dir) if os.path.isdir(os.path.join(template_dir, d))]

def choose_category(categories):
    """Asks the user to choose a category."""
    print("Available categories:")
    for i, category in enumerate(categories):
        print(f"{i + 1}. {category}")
    
    while True:
        try:
            choice = int(input("Choose a category (by number): "))
            if 1 <= choice <= len(categories):
                return categories[choice - 1]
            else:
                print("Invalid choice. Please enter a number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def get_templates(template_dir, category):
    """Gets a list of available prompt templates in a given category."""
    category_dir = os.path.join(template_dir, category)
    return [f for f in os.listdir(category_dir) if f.endswith('.txt')]

def choose_template(templates):
    """Asks the user to choose a template."""
    print("Available prompt templates:")
    for i, template in enumerate(templates):
        print(f"{i + 1}. {template}")
    
    while True:
        try:
            choice = int(input("Choose a template (by number): "))
            if 1 <= choice <= len(templates):
                return templates[choice - 1]
            else:
                print("Invalid choice. Please enter a number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def get_placeholder_values(template_content, template_name):
    """Gets values for placeholders from the user, with context-specific questions."""
    placeholders = re.findall(r'{{(.*?)\}', template_content)
    values = {}
    print("\nTo generate the best prompt, please answer the following questions:")

    # --- Custom Questions Dictionary ---
    custom_questions = {
        # Content Creation
        "blog_post.txt": {
            "topic": "What is the main topic of the blog post? ",
            "tone": "What tone should the blog post have? (e.g., informative, conversational, humorous): ",
            "audience": "Who is the target audience for this post? (e.g., beginners, industry experts): ",
            "length": "What is the approximate desired word count? "
        },
        "blog_post_titles.txt": {"topic": "What is the topic of the blog post you need titles for? "},
        "youtube_script.txt": {
            "topic": "What is the subject of the YouTube video? ",
            "duration": "What is the target video length (in minutes)? ",
            "style": "What style should the video be? (e.g., documentary, tutorial, comedic): "
        },
        "social_media_post.txt": {
            "product_or_service": "What product or service are you promoting? ",
            "platform": "Which social media platform is this for? (e.g., Twitter, Instagram, Facebook): "
        },
        "short_story.txt": {
            "genre": "What genre should the story be? (e.g., sci-fi, fantasy, mystery): ",
            "character_description": "Describe the main character: ",
            "challenge": "What challenge must the character overcome? "
        },
        "poem.txt": {
            "subject": "What is the subject of the poem? ",
            "poet": "Which poet's style should it emulate? (e.g., Edgar Allan Poe, Maya Angelou): "
        },
        "song_lyrics.txt": {
            "theme": "What is the central theme of the song? ",
            "mood": "What mood should the song have? (e.g., upbeat, melancholic, reflective): ",
            "genre": "What genre of music is this for? (e.g., pop, rock, country): "
        },
        "marketing_email.txt": {
            "event_or_product": "What event or product are you announcing? ",
            "audience": "Who is the target audience for this email? "
        },
        "press_release.txt": {
            "company": "What is the name of the company issuing the press release? ",
            "announcement": "What is the announcement about? "
        },
        "interview_questions.txt": {"role": "What job role are these interview questions for? "},
        "product_description.txt": {"product_name": "What is the name of the product? "},
        "tweet_series.txt": {"topic": "What topic do you want to tweet about? "},
        "newsletter_article.txt": {"industry": "Which industry are the trends about? "},
        "creative_brief.txt": {"product_or_brand": "What product or brand is this creative brief for? "},
        "case_study.txt": {
            "company": "What is the name of the company in the case study? ",
            "product_or_service": "What product or service did they use? ",
            "result": "What was the successful outcome? "
        },
        "faq_list.txt": {"product_or_service": "What product or service are the FAQs for? "},
        "podcast_script.txt": {
            "topic": "What is the topic of the podcast episode? ",
            "duration": "What is the target duration of the episode (in minutes)? ",
            "guest_or_expert": "Will there be a guest or expert? If so, who? "
        },
        "content_calendar.txt": {
            "month": "Which month is this content calendar for? ",
            "niche": "What is the niche of the blog? "
        },
        "white_paper.txt": {
            "topic": "What is the topic of the white paper? ",
            "audience": "Who is the target audience? "
        },
        "character_profile.txt": {"name": "What is the character's name? "},

        # Technical
        "technical_explanation.txt": {
            "concept": "What technical concept do you want to explain? ",
            "level": "Who is the target audience? (e.g., beginner, intermediate, expert): "
        },
        "code_snippet.txt": {
            "language": "Which programming language do you want the code in? ",
            "task_description": "What should the code accomplish? "
        },
        "debug_code.txt": {
            "language": "What language is the code in? ",
            "code_block": "Paste the code you want to debug: "
        },
        "tutorial.txt": {
            "technology_or_tool": "What technology or tool is the tutorial for? ",
            "audience": "Who is the target audience for this tutorial? "
        },
        "use_cases.txt": {"technology": "What technology do you want to find use cases for? "},
        "compare_technologies.txt": {
            "technology_1": "What is the first technology to compare? ",
            "technology_2": "What is the second technology to compare? "
        },
        "technical_specification.txt": {"feature_description": "What does the new feature do? "},
        "api_documentation.txt": {"api_endpoints": "What are the API endpoints to document? "},
        "unit_test.txt": {
            "testing_framework": "What testing framework are you using? ",
            "code_to_test": "Paste the code you want to write a unit test for: "
        },
        "refactor_code.txt": {"code_to_refactor": "Paste the code you want to refactor: "},
        "explain_error.txt": {"error_message": "Paste the error message you want explained: "},
        "regex_generator.txt": {"pattern_description": "Describe the pattern you want to match with a regular expression: "},
        "sql_query.txt": {
            "data_description": "What data do you want to retrieve? ",
            "database_schema": "Provide the database schema: "
        },
        "system_design.txt": {"system_description": "What system do you want to design? (e.g., a social media feed, a ride-sharing service): "},
        "security_vulnerabilities.txt": {"system_or_application": "What system or application do you want to check for vulnerabilities? "},
        "cli_script.txt": {"task_to_automate": "What task do you want to automate with a command-line script? "},
        "explain_difference.txt": {
            "term_1": "What is the first term? ",
            "term_2": "What is the second term? ",
            "domain": "What is the context or domain of these terms? "
        },
        "data_model.txt": {"application_description": "What application is the data model for? "},
        "pseudocode.txt": {"problem_description": "What problem do you want to solve with pseudocode? "},
        "test_cases.txt": {"function_to_test": "Paste the function you want to generate test cases for: "},

        # Business and Productivity
        "professional_email.txt": {
            "recipient": "Who is the recipient of the email? ",
            "subject": "What is the subject of the email? "
        },
        "meeting_agenda.txt": {
            "topic": "What is the topic of the meeting? ",
            "duration": "How long will the meeting be (in minutes)? ",
            "attendees": "Who will be attending the meeting? "
        },
        "project_plan.txt": {
            "project_goal": "What is the goal of the project? ",
            "deadline": "What is the project deadline? ",
            "budget": "What is the project budget? "
        },
        "job_description.txt": {"role": "What is the job role? "},
        "swot_analysis.txt": {"company_or_product": "What company or product is this SWOT analysis for? "},
        "business_plan.txt": {"company_description": "Describe the new company: "},
        "cover_letter.txt": {
            "role": "What role are you applying for? ",
            "company": "What company are you applying to? "
        },
        "business_ideas.txt": {"industry": "What industry are you interested in? "},
        "presentation.txt": {
            "topic": "What is the topic of the presentation? ",
            "duration": "How long is the presentation (in minutes)? ",
            "audience": "Who is the target audience? "
        },
        "performance_review.txt": {
            "employee_name": "What is the employee's name? ",
            "role": "What is the employee's role? "
        },
        "negotiation_strategies.txt": {"negotiation_goal": "What is your negotiation goal? "},
        "financial_projection.txt": {"number_of_years": "For how many years do you want to project the financials? "},
        "thank_you_note.txt": {
            "recipient": "Who are you thanking? ",
            "reason": "What are you thanking them for? "
        },
        "time_management_tips.txt": {"time_management_challenge": "What time management challenge are you facing? "},
        "customer_survey.txt": {"product_or_service": "What product or service is the survey about? "},
        "sales_pitch.txt": {
            "product_or_service": "What product or service are you selling? ",
            "customer_description": "Describe the potential customer: "
        },
        "marketing_slogans.txt": {"product_or_brand": "What product or brand are the slogans for? "},
        "competitive_analysis.txt": {
            "competitor_1": "Who is the first competitor? ",
            "competitor_2": "Who is the second competitor? "
        },
        "business_proposal.txt": {
            "recipient": "Who is the recipient of the proposal? ",
            "project_description": "What does the project entail? "
        },
        "kpi_list.txt": {"department_or_project": "What department or project are the KPIs for? "},
        "stock_market_analysis_report.txt": {
            "company_name": "Enter the full company name: ",
            "stock_symbol": "Enter the company's stock symbol (e.g., AAPL, GOOG): ",
            "time_horizon": "What is the investment time horizon? (e.g., short-term, long-term, 5-year): ",
            "key_metrics": "List the key financial metrics to focus on (e.g., P/E ratio, revenue growth): ",
            "competitors": "Who are the main competitors to analyze? (comma-separated): ",
            "tone": "What tone should the report have? (e.g., formal, objective, cautious): ",
            "audience": "Who is the intended audience? (e.g., retail investors, institutional analysts): "
        },

        # Learning and Education
        "simple_explanation.txt": {"concept": "What concept do you want explained in simple terms? "},
        "summarize_text.txt": {"text_to_summarize": "Paste the text you want to summarize: "},
        "lesson_plan.txt": {
            "subject": "What subject is the lesson plan for? ",
            "grade_level": "What grade level is this for? ",
            "duration": "How long should the lesson be (in minutes)? "
        },
        "flashcards.txt": {
            "subject": "What subject are the flashcards for? ",
            "topics": "What topics should the flashcards cover? "
        },
        "translate_phrase.txt": {
            "source_language": "What is the source language? ",
            "target_language": "What is the target language? ",
            "phrase_to_translate": "What phrase do you want to translate? "
        },
        "study_guide.txt": {"subject": "What subject is the study guide for? "},
        "research_paper_topics.txt": {"subject": "What subject do you need research paper topics for? "},
        "biography.txt": {"historical_figure": "Which historical figure do you want a biography of? "},
        "historical_event_significance.txt": {"historical_event": "What historical event do you want to know the significance of? "},
        "book_recommendations.txt": {"topic": "What topic are you interested in for book recommendations? "},
        "timeline.txt": {"person": "Who do you want a timeline of? "},
        "multiple_choice_questions.txt": {"subject": "What subject are the questions for? "},
        "essay.txt": {
            "essay_topic": "What is the topic of the essay? ",
            "length": "What is the desired word count? "
        },
        "vocabulary_list.txt": {"subject": "What subject is the vocabulary list for? "},
        "debate_prompt.txt": {"debate_topic": "What is the topic of the debate? "},
        "fun_facts.txt": {"topic": "What topic do you want fun facts about? "},
        "crossword_puzzle.txt": {"subject": "What is the subject of the crossword puzzle? "},
        "word_search.txt": {"subject": "What is the subject of the word search? "},
        "historical_dialogue.txt": {
            "figure_1": "Who is the first historical figure? ",
            "figure_2": "Who is the second historical figure? ",
            "topic": "What are they discussing? "
        },
        "online_resources.txt": {"topic": "What topic do you want online resources for? "},

        # Personal and Lifestyle
        "workout_plan.txt": {
            "fitness_goal": "What is your fitness goal? ",
            "duration": "For how many weeks do you want the plan to be? ",
            "days_per_week": "How many days per week do you want to work out? "
        },
        "meal_plan.txt": {
            "diet_type": "What type of diet is this for? (e.g., vegan, keto, low-carb): ",
            "number_of_days": "For how many days do you want the meal plan? "
        },
        "travel_recommendations.txt": {
            "destination": "Where are you traveling to? ",
            "duration": "How many days will your trip be? ",
            "interests": "What are your interests? (e.g., hiking, museums, food): "
        },
        "birthday_message.txt": {"person_name": "What is the person's name? "},
        "gift_ideas.txt": {
            "recipient": "Who is the gift for? ",
            "interests": "What are their interests? "
        },
        "budget_plan.txt": {
            "amount": "How much do you want to save per month? ",
            "income": "What is your monthly income? ",
            "expenses": "What are your fixed monthly expenses? "
        },
        "conversation_starters.txt": {},
        "letter_to_future_self.txt": {"number_of_years": "In how many years will you open this letter? "},
        "date_night_ideas.txt": {"interests": "What are your shared interests as a couple? "},
        "playlist.txt": {"mood": "What mood is the playlist for? "},
        "affirmations.txt": {"self_improvement_goal": "What self-improvement goal are you working on? "},
        "speech.txt": {"event": "What event is the speech for? (e.g., wedding, graduation): "},
        "hobby_ideas.txt": {},
        "cleaning_schedule.txt": {"number_of_bedrooms": "How many bedrooms are in the house? "},
        "random_acts_of_kindness.txt": {},
        "journal_prompt.txt": {},
        "yearly_goals.txt": {},
        "morning_routine.txt": {"feeling": "How do you want to feel in the morning? "},
        "icebreaker_questions.txt": {},
        "personal_story.txt": {}
    }

    template_specific_questions = custom_questions.get(template_name, {})

    for placeholder in placeholders:
        # Use the custom question if available, otherwise create a generic one.
        question = template_specific_questions.get(placeholder, f"Enter a value for '{placeholder}': ")
        value = input(question)
        values[placeholder] = value

    return values

def initial_user_prompt():
    """Asks the user what they want to do."""
    return input("What would you like to do today? ")

def suggest_category(user_input, categories):
    """Suggests a category based on user input."""
    user_input = user_input.lower()
    if any(keyword in user_input for keyword in ['blog', 'write', 'social media', 'content']):
        return "content_creation"
    elif any(keyword in user_input for keyword in ['code', 'technical', 'debug', 'explain']):
        return "technical"
    elif any(keyword in user_input for keyword in ['business', 'email', 'meeting', 'project', 'stock']):
        return "business_and_productivity"
    elif any(keyword in user_input for keyword in ['learn', 'study', 'explain', 'education']):
        return "learning_and_education"
    elif any(keyword in user_input for keyword in ['personal', 'lifestyle', 'workout', 'meal']):
        return "personal_and_lifestyle"
    else:
        return None

def refine_template_choice(templates, category):
    """Asks follow-up questions to refine the template choice."""
    # This function can be expanded with more refined logic for other categories
    return choose_template(templates)

def main():
    """Main function to run the CLI tool."""
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    categories = get_categories(template_dir)
    
    if not categories:
        print("No categories found in the 'templates' directory.")
        return

    user_input = initial_user_prompt()
    suggested_category = suggest_category(user_input, categories)

    if suggested_category and suggested_category in categories:
        print(f"\nBased on your input, I suggest the '{suggested_category}' category.")
        use_suggestion = input("Would you like to use this category? (y/n): ").lower()
        if use_suggestion == 'y':
            chosen_category = suggested_category
        else:
            chosen_category = choose_category(categories)
    else:
        chosen_category = choose_category(categories)
        
    templates = get_templates(template_dir, chosen_category)
    
    if not templates:
        print(f"No prompt templates found in the '{chosen_category}' category.")
        return
        
    chosen_template_file = refine_template_choice(templates, chosen_category)
    
    with open(os.path.join(template_dir, chosen_category, chosen_template_file), 'r') as f:
        template_content = f.read()
        
    values = get_placeholder_values(template_content, chosen_template_file)
    
    final_prompt = template_content
    for placeholder, value in values.items():
        final_prompt = final_prompt.replace(f'{{{{{placeholder}}}}}', value)
        
    print("\n--- Your final prompt ---")
    print(final_prompt)

if __name__ == "__main__":
    main()
