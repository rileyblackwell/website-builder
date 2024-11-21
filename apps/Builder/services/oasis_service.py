# builder/services/oasis_service.py

import os
import re
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
from ..models import Message, Conversation, Page
from .utils import (
    test_html, 
    test_css, 
    get_system_message, 
    get_file_context,
    ensure_website_directory
)

# Load environment variables from .env
load_dotenv()
openai_key = os.getenv('OPENAI_KEY')
anthropic_key = os.getenv('ANTHROPIC_KEY')

openai_client = OpenAI(api_key=openai_key)
anthropic_client = anthropic.Anthropic(api_key=anthropic_key)


def build_conversation_history(system_msg, page, output_dir):
    """Builds the conversation history in the exact format sent to AI models.
    
    Structure:
    1. System prompt (main Imagi Oasis instructions)
    2. Most recent version of all current HTML and CSS files
    3. All user and assistant messages for the current file
    4. File-specific system prompt
    """
    conversation_history = []
    
    # 1. Add current state of all files (most recent versions)
    if os.path.exists(output_dir):
        # First add all HTML files
        html_files = [f for f in os.listdir(output_dir) if f.endswith('.html')]
        html_files.sort()  # Ensure consistent order (index.html first)
        if 'index.html' in html_files:  # Move index.html to front if it exists
            html_files.remove('index.html')
            html_files.insert(0, 'index.html')
            
        for filename in html_files:
            file_path = os.path.join(output_dir, filename)
            try:
                with open(file_path, 'r') as f:
                    file_content = f.read()
                    conversation_history.append({
                        "role": "assistant",
                        "content": f"[File: {filename}]\nCurrent HTML content:\n{file_content}"
                    })
            except FileNotFoundError:
                continue
        
        # Then add CSS file if it exists
        css_path = os.path.join(output_dir, 'styles.css')
        if os.path.exists(css_path):
            try:
                with open(css_path, 'r') as f:
                    css_content = f.read()
                    conversation_history.append({
                        "role": "assistant",
                        "content": f"[File: styles.css]\nCurrent CSS content:\n{css_content}"
                    })
            except FileNotFoundError:
                pass
    
    # 2. Add conversation history for the current file being edited
    current_file_messages = page.messages.all().order_by('created_at')
    for msg in current_file_messages:
        if msg.role == 'user':
            conversation_history.append({
                "role": "user",
                "content": f"[File: {msg.page.filename}]\n{msg.content}"
            })
        elif msg.role == 'assistant':
            conversation_history.append({
                "role": "assistant",
                "content": msg.content
            })
    
    return conversation_history


def process_user_input(user_input, model, conversation, page):
    """Processes user input for a specific page."""
    try:
        # Get system message
        system_msg = get_system_message()
        
        # Set up output directory - ensure it exists
        base_dir = os.path.dirname(__file__)
        output_dir = ensure_website_directory(os.path.join(base_dir, '..'))
        
        # Build conversation history - this should only read files, never delete them
        conversation_history = build_conversation_history(system_msg, page, output_dir)
        
        # Add the current file context
        file_context = get_file_context(page.filename)
        
        # Add the current request
        current_request = f"[File: {page.filename}]\n{user_input}"
        
        # Create the messages array that will be used for both models
        ai_messages = [
            {"role": "system", "content": system_msg["content"]},  # Main system prompt
            *conversation_history,  # Current file state + conversation history
            {"role": "system", "content": file_context},  # File context
            {"role": "user", "content": current_request}  # Current request
        ]

        # Store the full conversation for logging (same format for both models)
        full_conversation = {
            "model": model,
            "messages": ai_messages,
            "system": system_msg["content"] + "\n\n" + file_context  # For reference
        }

        # Process based on model
        try:
            if model == 'claude-sonnet':
                # For Claude, combine system messages and pass as system parameter
                system_content = system_msg["content"] + "\n\n" + file_context
                
                # Filter out system messages from the conversation history
                claude_messages = [
                    msg for msg in ai_messages 
                    if msg["role"] != "system"
                ]
                
                completion = anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2048,
                    system=system_content,  # Combined system messages
                    messages=claude_messages  # Everything except system messages
                )
                assistant_response = completion.content[0].text
            else:
                # For OpenAI, use the messages array as is
                completion = openai_client.chat.completions.create(
                    model=model,
                    messages=ai_messages
                )
                assistant_response = completion.choices[0].message.content

        except Exception as e:
            raise ValueError(f"API error: {str(e)}")

        # Validate and clean the response based on file type
        if page.filename.endswith('.html'):
            # For HTML files, first try to extract HTML content if it's wrapped in other text
            html_match = re.search(r'(?s)<!DOCTYPE html>.*?</html>', assistant_response)
            if html_match:
                assistant_response = html_match.group(0)
            
            # Then validate the HTML content
            cleaned_response = test_html(assistant_response)
            if not cleaned_response:
                raise ValueError("Invalid HTML content received")
                
        elif page.filename == 'styles.css':
            # For CSS files, extract CSS content if needed
            css_match = re.search(r'(?s)/\*.*?\*/\s*(.*?)$', assistant_response)
            if css_match:
                assistant_response = css_match.group(1)
            
            # Validate and clean the CSS content
            cleaned_response = test_css(assistant_response)
            if not cleaned_response:
                raise ValueError("Invalid CSS content received")
            
            # Add a debug print to see the cleaned CSS
            print("Cleaned CSS content:", cleaned_response)
        else:
            cleaned_response = assistant_response

        # Save only the current file being edited
        output_path = os.path.join(output_dir, page.filename)
        with open(output_path, 'w') as f:
            f.write(cleaned_response)

        # Save the conversation
        Message.objects.create(
            conversation=conversation,
            page=page,
            role="user",
            content=user_input
        )

        Message.objects.create(
            conversation=conversation,
            page=page,
            role="assistant",
            content=cleaned_response
        )

        # For CSS updates, also return the current index.html content
        if page.filename == 'styles.css':
            index_path = os.path.join(output_dir, 'index.html')
            try:
                with open(index_path, 'r') as f:
                    index_content = f.read()
                return {
                    'html': index_content, 
                    'css': cleaned_response,
                    'conversation_history': full_conversation
                }
            except FileNotFoundError:
                return {
                    'html': '', 
                    'css': cleaned_response,
                    'conversation_history': full_conversation
                }

        return {
            'html': cleaned_response,
            'conversation_history': full_conversation
        }

    except Exception as e:
        print(f"Error in process_user_input: {str(e)}")
        raise ValueError(str(e))


def undo_last_action(conversation, page):
    """Removes the last user-assistant exchange from the specific page."""
    messages = page.messages.order_by('-created_at')
    total_messages = messages.count()

    if total_messages >= 2:
        # Get the previous content (before the last change)
        previous_content = messages[2].content if total_messages > 2 else ''
        
        # Delete only the last exchange (last two messages)
        latest_two = messages[:2]
        Message.objects.filter(id__in=[msg.id for msg in latest_two]).delete()

        # For styles.css, we need to ensure we return valid CSS
        if page.filename == 'styles.css':
            previous_content = test_css(previous_content)
            if not previous_content:
                # If no previous CSS exists, return empty string but don't delete file
                return '', 'No previous CSS version available.'
        else:
            previous_content = test_html(previous_content) if previous_content else ''

        return previous_content, 'Last action undone successfully.'
    else:
        # Don't delete all messages for styles.css when there's not enough history
        if page.filename == 'styles.css':
            return '', 'Not enough history to undo last action.'
        else:
            messages.all().delete()
            return '', 'Not enough history to undo last action; page history cleared.'
