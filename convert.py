
import json
import csv
import re

# Mapping for model IDs to match the desired output format
model_id_map = {
    "gemini-flash-latest": "Gemini-flash-latest",
    "gemini-flash-lite-latest": "Gemini-flash-latest",
    "gemini-3.1-pro-preview": "gemini-3.1-pro-preview" # Keep lowercase as specified
}

# Regex to strip trailing punctuation from the end of a word
trailing_punct_regex = re.compile(r'[.,!?;:]+$')

def get_first_n_words(text, n=50):
    """Extracts the first n words from a given text, preserving original spacing between words,
    and stripping trailing punctuation from the Nth word.
    
    Handles cases where the Nth word might be followed by spaces, ensuring those spaces
    are included if they are part of the segmentation up to the Nth word.
    Finally, trims trailing whitespace from the entire resulting string.
    """
    # Split the text into tokens: either a sequence of non-whitespace characters (\S+)
    # or a sequence of whitespace characters (\s+). This preserves original spacing.
    tokens = re.findall(r'(\S+|\s+)', text)
    
    output_parts = []
    word_count = 0
    
    for i, token in enumerate(tokens):
        if word_count >= n:
            break
        
        if not token.isspace(): # It's a word token
            word_count += 1
            
            if word_count < n:
                # If it's not the Nth word, add it directly.
                output_parts.append(token)
            else: # This is the Nth word
                # Strip trailing punctuation from the Nth word.
                cleaned_token = trailing_punct_regex.sub('', token)
                output_parts.append(cleaned_token)
        else: # It's a space token
            # Add space tokens as they appear, preserving original spacing.
            output_parts.append(token)

    # Join all the selected tokens. This reconstructs the string with preserved spacing.
    result = "".join(output_parts)
    
    # Trim any trailing whitespace from the final result to ensure consistency.
    return result.rstrip()

def extract_response_text(content_list):
    """Extracts text from content, ignoring 'thinking' blocks."""
    response_parts = []
    for item in content_list:
        if item.get('type') == 'text':
            response_parts.append(item.get('text', ''))
        # Ignore 'thinking' blocks as per objective
    return "".join(response_parts)

# The header for the output CSV, as determined from src/example-output.csv
header = ["modelId", "Prompt50", "Response50", "totalTokens", "totalCost"]

output_rows = []
current_user_message_content = None

# Process the input JSONL file
input_jsonl_path = "combined.jsonl"
output_csv_path = "combined_output.csv"

try:
    with open(input_jsonl_path, 'r') as infile:
        for line in infile:
            try:
                event = json.loads(line)

                if event.get("type") == "message":
                    message_data = event.get("message", {})
                    role = message_data.get("role")
                    content = message_data.get("content", [])
                    usage = message_data.get("usage", {})
                    # The model used for the assistant's response is in message.model
                    model = message_data.get("model") 

                    if role == "user":
                        # Store the user's text content to be paired with the next assistant message
                        user_text_parts = []
                        for item in content:
                            if item.get('type') == 'text':
                                user_text_parts.append(item.get('text', ''))
                        current_user_message_content = "".join(user_text_parts)

                    elif role == "assistant" and current_user_message_content is not None and model is not None:
                        # We have a user message and an assistant message pair
                        
                        # Extracting Response50: filter thinking blocks and get first 50 words
                        assistant_response_text = extract_response_text(content)
                        response50 = get_first_n_words(assistant_response_text, 50)

                        # Extracting Prompt50: get first 50 words of the user message
                        prompt50 = get_first_n_words(current_user_message_content, 50)

                        # Extracting usage details
                        total_tokens = usage.get("totalTokens", 0)
                        # Get raw total cost and round it to 7 decimal places
                        total_cost_raw = float(usage.get("cost", {}).get("total", 0.0))
                        total_cost = round(total_cost_raw, 7)

                        # Map the model ID using the defined map
                        mapped_model_id = model_id_map.get(model, model) # Default to original if not in map

                        # Create the row dictionary
                        output_rows.append({
                            "modelId": mapped_model_id,
                            "Prompt50": prompt50,
                            "Response50": response50,
                            "totalTokens": total_tokens,
                            "totalCost": total_cost
                        })

                        # Reset for the next pair
                        current_user_message_content = None

            except json.JSONDecodeError:
                print(f"Skipping invalid JSON line: {line.strip()}")
            except Exception as e:
                print(f"Error processing line: {line.strip()} - {e}")

    # Write the extracted data to test-output.csv
    with open(output_csv_path, 'w', newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=header, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Successfully processed {input_jsonl_path} and wrote to {output_csv_path}")

except FileNotFoundError:
    print(f"Error: Input file not found at {input_jsonl_path}")
except Exception as e:
    print(f"An unexpected error occurred during file processing: {e}")
