from google import genai
from .settings import GEMINI_API_KEY


def extract_names_and_questions(email_content: str):
    # Initialize the Gemini client
    client = genai.Client(api_key=GEMINI_API_KEY)

    # Assignment 2
    # Define your prompt content (replace this with your actual prompt)
    # email_content = "Hello Yuan, how are you doing today? Best, Isa"

    # prompt = f"""
    #     Given the following email content, extract the only sender and receiver names,
    #     don't include any other messages or different format:
    #
    #     Email Content: "{email_content}"
    #
    #     The output should be as in the below format and if you don't find either Sender Name or Receiver Name in the
    #     email content, pass empty string to the respective field.
    #     Sender Name:
    #     Receiver Name:
    #
    #     """

    # Assignment 3
    prompt = f"""
               Given the following email content, extract the sender and receiver names and also all inquiry 
               questions. Do not include greetings, introductory phrases, or any context. Only include the exact 
               questions as they appear, with each question on a new line.

               Email Content: "{email_content}"

               The output should be in the following format, and if you don't find either Sender Name or Receiver Name in the 
               email content, pass an empty string to the respective field.
               Sender Name: 
               Receiver Name:
               Inquiry Questions:[
                   [First inquiry question],
                   [Second inquiry question],
                   ...
                   ..
               ]

               Strictly include only sentences that are actual questions (ending with a question mark) and 
               do not include any statements, greetings, or non-question sentences.
               If there are no questions, return an empty list: '"Inquiry Questions": []'.
               """

    try:
        # Sending the request to the Gemini model
        response = client.models.generate_content(
            model="gemini-2.0-flash",  # Specify the Gemini model
            contents=[
                "you are a helpful assistant.",  # Input as a string, not a dictionary
                prompt  # User prompt
            ]
        )

        # Print the response from Gemini model
        print(response.text)  # Assuming response.text contains the generated output

        # Check if the response has valid text
        response_text = response.text.strip() if response.text else ""
        if not response_text:
            raise ValueError("Empty response from Gemini model")

        # Initialize default values
        sender_name = ""
        receiver_name = ""
        inquiry_questions = []

        # Split the response into lines and process
        in_questions = False
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith("Sender Name:"):
                sender_name = line.split("Sender Name:")[-1].strip()
            elif line.startswith("Receiver Name:"):
                receiver_name = line.split("Receiver Name:")[-1].strip()
            elif line.startswith("Inquiry Questions:"):
                in_questions = True  # Start reading questions
                continue  # Skip the current line
            elif in_questions:
                if line == "]":  # End of the questions block
                    in_questions = False
                    continue
                # Extract the question from the line, removing commas and brackets
                question = line.strip(" [],")
                if question:
                    inquiry_questions.append(question)

        # Return the extracted names and questions list
        print(sender_name, "-->", receiver_name, "-->", inquiry_questions)
        return sender_name, receiver_name, inquiry_questions

    except Exception as e:
        print(f"Error occurred: {e}")
        return "", "", []


def generate_ai_reply(sender_name: str, receiver_name: str, inquiry_questions: list, original_email: str):
    """
    Generate an AI-powered reply based on the extracted questions and email content.
    """
    
    # Create a personalized greeting
    if sender_name:
        greeting = f"Hi {sender_name},"
    else:
        greeting = "Hi there,"
    
    # Create a personalized signature
    if receiver_name:
        signature = f"Best regards,\n{receiver_name}"
    else:
        signature = "Best regards,\nCustomer Support Team"
    
    # If no questions were found, return a basic acknowledgment
    if not inquiry_questions:
        ai_response = "Thank you for your email. I've received your message and appreciate you reaching out. I'll review your inquiry and get back to you with a detailed response soon."
    else:
        # Create intelligent responses for common questions (demo version)
        responses = []
        
        for question in inquiry_questions:
            question_lower = question.lower()
            
            if "password" in question_lower and "reset" in question_lower:
                responses.append("Regarding your password reset request: I can help you with that! Please check your email for password reset instructions, or visit our account recovery page. If you don't receive the email within 5 minutes, please check your spam folder.")
            
            elif "billing" in question_lower or "payment" in question_lower:
                responses.append("For billing and payment inquiries: You can update your billing information in your account settings under 'Payment Methods'. If you need assistance with charges or have billing questions, our billing support team is available 24/7.")
            
            elif "upgrade" in question_lower or "subscription" in question_lower or "plan" in question_lower:
                responses.append("About subscription upgrades: We offer several plans to meet your needs! You can view and upgrade your plan anytime in your account dashboard. Our premium plans include additional features and priority support.")
            
            elif "free" in question_lower and "today" in question_lower:
                responses.append("Thank you for asking! I'm doing well and I'm here to help you with any questions or concerns you may have.")
            
            elif "pricing" in question_lower or "cost" in question_lower or "price" in question_lower:
                responses.append("Regarding pricing: Our plans start from $9.99/month for basic features. We also offer annual discounts and enterprise solutions. I'd be happy to discuss which plan would work best for your needs.")
            
            elif "trial" in question_lower and "free" in question_lower:
                responses.append("About our free trial: Yes! We offer a 14-day free trial with full access to all features. No credit card required to start your trial. You can sign up directly on our website.")
            
            elif "feature" in question_lower:
                responses.append("About our key features: Our platform includes automated workflows, real-time analytics, team collaboration tools, and 24/7 customer support. I can provide a detailed feature breakdown if you'd like more specific information.")
            
            elif "discount" in question_lower or "bulk" in question_lower:
                responses.append("Regarding bulk discounts: Yes, we offer significant discounts for bulk purchases and enterprise clients. Discounts start at 15% for 10+ licenses and can go up to 30% for larger organizations. I'd be happy to create a custom quote for you.")
            
            else:
                # Generic helpful response for unrecognized questions
                responses.append(f"Thank you for your question: '{question}' - I've noted your inquiry and will make sure to provide you with comprehensive information. Our team will research this and get back to you with detailed answers.")
        
        ai_response = "\n\n".join(responses)
    
    # Combine greeting, AI response, and signature
    full_reply = f"{greeting}\n\n{ai_response}\n\n{signature}"
    
    return full_reply