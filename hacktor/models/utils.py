import re

def escape_special_characters(text: str) -> str:
    """
    Escapes special characters in a string for use in Langchain ChatPromptTemplate.
    
    Args:
        text (str): The input string that needs escaping.
    
    Returns:
        str: The escaped string.
    """
    # Define a dictionary of special characters and their escaped equivalents
    special_chars = {
        '{': '{{',
        '}': '}}',
        '[': '\\[',
        ']': '\\]',
        '(': '\\(',
        ')': '\\)',
        '*': '\\*',
        '+': '\\+',
        '?': '\\?',
        '\\': '\\\\',
        '^': '\\^',
        '$': '\\$',
        '.': '\\.',
        '|': '\\|'
    }
    
    # Use regular expression to replace each special character with its escaped equivalent
    escaped_text = re.sub(r'([{}[\]()*+?\\^$.|])', lambda match: special_chars[match.group()], text)
    
    return escaped_text
