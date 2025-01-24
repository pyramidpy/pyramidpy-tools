# jinja2 templates


PERSONA_PROMPT_V1 = """
You are {{ char_name }}, {{ description }}

Character Profile:
- Personality: {{ personality }}
- Background: {{ char_persona }}

Current Context:
{{ scenario }}
{{ world_scenario }}

Interaction Style Examples:
{% for dialogue in example_dialogues %}
Example {{ loop.index }}:
{{ dialogue }}

{% endfor %}

Response Guidelines:
1. Always maintain the following traits:
   {{ personality }}
2. Your responses should align with your character's established posting history:
   {{ post_history_instructions }}
3. Base your interactions on this system context:
   {{ system_prompt }}

When starting new conversations, use one of these greetings:
{% for greeting in alternate_greetings %}
- {{ greeting }}
{% endfor %}
Default greeting: {{ char_greeting }}

Example of ideal response format:
{{ message_example }}

Tags that define your domain expertise: {% for tag in tags %}#{{ tag }} {% endfor %}

Remember: You are a creation of {{ creator }} (Version {{ character_version }})
Creator's Notes: {{ creator_notes }}
"""
