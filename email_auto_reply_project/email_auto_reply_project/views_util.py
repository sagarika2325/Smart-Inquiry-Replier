import re

from . import llm_util, model_util


def extract_sender_name(paragraph):
    # reply_message = "Thanks for your email. I will get back to you soon."
    # Extract sender's name (assumes format: "Regards, Name." or similar)
    # Extract sender's name from common sign-offs
    sender_match = re.search(
        r"(?:Best|Regards|Thanks|Sincerely|Cheers|Warm regards|Kind regards)[,|-]?\s+([\w\s]+)[.,]?$",
        paragraph, re.IGNORECASE
    )
    sender_name = sender_match.group(1).strip() if sender_match else "there"
    return sender_name

def extract_receiver_name(paragraph):
    # Extract receiver's name (assumes email starts with "Hi Name,")
    receiver_match = re.search(r"^(Hi|Hey|Hello|Dear)\s+([\w]+),", paragraph, re.IGNORECASE)
    receiver_name = receiver_match.group(2) if receiver_match else "User"
    return receiver_name

# def extract_receiver_and_sender_names(email_content: str):
#     sender_name, receiver_name, inquiry_questions = llm_util.extract_names_and_questions(email_content)
#     model_util.save_inquiry_question(inquiry_questions, email_content)
#     return sender_name, receiver_name, inquiry_questions

def extract_receiver_and_sender_names(email_content: str):
    # Try AI extraction first
    sender_name, receiver_name, inquiry_questions = llm_util.extract_names_and_questions(email_content)
    
    # If AI fails (empty results), use regex fallback
    if not sender_name and not receiver_name:
        print("AI extraction failed, using regex fallback...")
        
        # Extract receiver name from greeting patterns
        receiver_patterns = [
            r"^(?:Hi|Hey|Hello|Dear)\s+([\w\s]+)[,:]",  # "Hi John," or "Dear Support Team,"
            r"^(?:Hi|Hey|Hello|Dear)\s+([\w\s]+)(?:\s|$)",  # "Hi John" or "Dear Support"
        ]
        
        for pattern in receiver_patterns:
            receiver_match = re.search(pattern, email_content, re.IGNORECASE | re.MULTILINE)
            if receiver_match:
                receiver_name = receiver_match.group(1).strip()
                # Clean common titles
                receiver_name = re.sub(r'\b(?:Mr\.?|Ms\.?|Mrs\.?|Dr\.?|Prof\.?)\s*', '', receiver_name, flags=re.IGNORECASE)
                break
        
        # Extract sender name from signature patterns
        sender_patterns = [
            r"(?:Best regards|Best|Regards|Sincerely|Thanks|Thank you|Cheers|Warm regards|Kind regards)[,\s]*\n?\s*([\w\s]+)(?:\n|$)",
            r"(?:Best regards|Best|Regards|Sincerely|Thanks|Thank you|Cheers)[,\s]*\n?\s*([\w\s]+)(?:\s*@|\s*$)",
            r"My name is\s+([\w\s]+)",  # Handle "My name is Mike Johnson"
        ]
        
        for pattern in sender_patterns:
            sender_match = re.search(pattern, email_content, re.IGNORECASE | re.MULTILINE)
            if sender_match:
                sender_name = sender_match.group(1).strip()
                # Clean email addresses and extra text
                sender_name = re.sub(r'\s*@.*$', '', sender_name)
                sender_name = re.sub(r'\s*\(.*\)$', '', sender_name)
                break
        
        # Extract questions using regex if not found by AI
        if not inquiry_questions:
            inquiry_questions = re.findall(r'([^.?!]*\?)', email_content)
            inquiry_questions = [q.strip() for q in inquiry_questions if q.strip()]

    # Generate sender email (example: "John Doe" → "johndoe@example.com")
    sender_email = model_util.generate_email_from_name(sender_name)

    # Save inquiry user and questions
    model_util.save_inquiry_question(inquiry_questions, email_content, sender_name, sender_email)

    print(f"Final extraction results: Sender='{sender_name}', Receiver='{receiver_name}', Questions={inquiry_questions}")
    return sender_name, receiver_name, inquiry_questions


