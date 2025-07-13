

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
    placeholders = re.findall(r'{{(.*?)}}', template_content)
    values = {}

    # --- Context-Specific Questions for Stock Analysis ---
    if template_name == "stock_market_analysis_report.txt":
        print("\nTo generate a detailed stock analysis, please provide the following details:")
        for placeholder in placeholders:
            if placeholder == 'company_name':
                value = input("Enter the full company name: ")
            elif placeholder == 'stock_symbol':
                value = input("Enter the company's stock symbol (e.g., AAPL, GOOG): ")
            elif placeholder == 'time_horizon':
                value = input("What is the investment time horizon? (e.g., short-term, long-term, 5-year): ")
            elif placeholder == 'key_metrics':
                value = input("List the key financial metrics you want to focus on (e.g., P/E ratio, revenue growth, debt-to-equity): ")
            elif placeholder == 'competitors':
                value = input("Who are the main competitors to analyze? (comma-separated): ")
            elif placeholder == 'tone':
                value = input("What tone should the report have? (e.g., formal, objective, cautious): ")
            elif placeholder == 'audience':
                value = input("Who is the intended audience? (e.g., retail investors, institutional analysts): ")
            else:
                value = input(f"Enter a value for '{placeholder}': ")
            
            values[placeholder] = value
        return values

    # --- Generic Questions for All Other Templates ---
    print("\nPlease provide the following details to complete the prompt:")
    for placeholder in placeholders:
        if placeholder == 'tone':
            value = input(f"What is the desired tone for the content? (e.g., formal, casual, witty): ")
        elif placeholder == 'audience':
            value = input(f"Who is the target audience? (e.g., beginners, experts): ")
        else:
            value = input(f"Enter a value for '{placeholder}': ")
        
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
