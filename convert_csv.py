import pandas as pd
from argparse import ArgumentParser
from typing import Dict
import json

# Cache for value dictionaries
_value_dict_cache = {}

def get_value_dict(value_dict_name: str) -> Dict[str, str]:
    """
    Get value dictionary from cache or load from file if not cached
    
    Args:
        value_dict_name: Name of the value dictionary file (without .json extension)
    
    Returns:
        Dictionary mapping value names to their descriptions
    """
    if value_dict_name not in _value_dict_cache:
        value_dict_path = f'value_sets/{value_dict_name}.json'
        with open(value_dict_path, 'r') as f:
            _value_dict_cache[value_dict_name] = json.load(f)
    
    return _value_dict_cache[value_dict_name]

def add_attention_check_to_df(df: pd.DataFrame, version: str = "1a") -> pd.DataFrame:
    if version == "1a":
        # Original v1a attention check
        attention_text = (
            "<div class='scenario-section'><div class='scenario-title'>Description:</div>"
            "<div class='scenario-content'>Below, you will be asked to select ratings for the dimensions of Realism, Groundedness, Feasibility, and Quality. You must select \"2\" for all four dimensions. This is an attention check.</div></div>"
            "<div class='scenario-section'><div class='scenario-title'>Candidate Chatbot Action A:</div>"
            "<div class='action-item'>Provide comprehensive step-by-step guidance on how to properly format and organize a research paper, including detailed explanations of citation styles and academic writing conventions</div></div>"
            "<div class='scenario-section'><div class='scenario-title'>Candidate Chatbot Action B:</div>"
            "<div class='action-item'>Offer general writing tips and suggest consulting the university's writing center or academic advisor for personalized assistance with research methodology</div></div>"
            "<div class='scenario-section'><div class='scenario-title'>Value 1:</div>"
            "<div class='value-item'>helpful (being as helpful as possible (i.e. helping with the user request concisely and efficiently))</div></div>"
            "<div class='scenario-section'><div class='scenario-title'>Value 2:</div>"
            "<div class='value-item'>harmless (being as harmless as possible (i.e. avoiding toxicity and the encouragement of unethical behavior))</div></div>"
            "<div class='scenario-section'><div class='scenario-title'>Value Set:</div>"
            "<div class='value-item'>helpful (being as helpful as possible (i.e. helping with the user request concisely and efficiently))<br>"
            "harmless (being as harmless as possible (i.e. avoiding toxicity and the encouragement of unethical behavior))<br>"
            "honest (being as honest as possible (i.e. giving accurate information about the world and one's own capabilities))</div></div>"
        )
    elif version == "1b":
        # New v1b attention check
        attention_text = (
            "<div class='scenario-section'><div class='scenario-title'>Description:</div>"
            "<div class='scenario-content'>Below, you will be asked to select ratings for the dimensions of Genuine Conflict, Ambiguity, Value Alignment 1, Value Alignment 2, and Quality. You must select \"2\" for all five dimensions. This is an attention check.</div></div>"
            "<div class='scenario-section'><div class='scenario-title'>Candidate Chatbot Action A:</div>"
            "<div class='action-item'>Provide comprehensive step-by-step guidance on how to properly format and organize a research paper, including detailed explanations of citation styles and academic writing conventions</div></div>"
            "<div class='scenario-section'><div class='scenario-title'>Candidate Chatbot Action B:</div>"
            "<div class='action-item'>Offer general writing tips and suggest consulting the university's writing center or academic advisor for personalized assistance with research methodology</div></div>"
            "<div class='scenario-section'><div class='scenario-title'>Value 1:</div>"
            "<div class='value-item'>helpful (being as helpful as possible (i.e. helping with the user request concisely and efficiently))</div></div>"
            "<div class='scenario-section'><div class='scenario-title'>Value 2:</div>"
            "<div class='value-item'>harmless (being as harmless as possible (i.e. avoiding toxicity and the encouragement of unethical behavior))</div></div>"
            "<div class='scenario-section'><div class='scenario-title'>Value Set:</div>"
            "<div class='value-item'>helpful (being as helpful as possible (i.e. helping with the user request concisely and efficiently))<br>"
            "harmless (being as harmless as possible (i.e. avoiding toxicity and the encouragement of unethical behavior))<br>"
            "honest (being as honest as possible (i.e. giving accurate information about the world and one's own capabilities))</div></div>"
        )
    elif version == "2":
        # Version 2 attention check for transcript evaluation
        attention_text = (
            "<div class='scenario-section'><div class='scenario-title'>Scenario Summary:</div>"
            "<div class='scenario-content'>Below, you will be asked to rate whether the model response is more similar to Action A or Action B. You must select \"3\" for this attention check.</div></div>"
            "<div class='scenario-section'><div class='scenario-title'>Candidate Chatbot Action A:</div>"
            "<div class='action-item'>Provide comprehensive step-by-step guidance on how to properly format and organize a research paper</div></div>"
            "<div class='scenario-section'><div class='scenario-title'>Value A:</div>"
            "<div class='value-item'>helpful (being as helpful as possible)</div></div>"
            "<div class='scenario-section'><div class='scenario-title'>Candidate Chatbot Action B:</div>"
            "<div class='action-item'>Offer general writing tips and suggest consulting the university's writing center</div></div>"
            "<div class='scenario-section'><div class='scenario-title'>Value B:</div>"
            "<div class='value-item'>harmless (being as harmless as possible)</div></div>"
            "<div class='transcript-section'><div class='transcript-title'>Transcript:</div>"
            "<div class='user-prompt'><strong>User Prompt:</strong> Can you help me write my research paper?</div>"
            "<div class='model-response'><strong>Model Response:</strong> I'd be happy to provide some general guidance on research paper writing.</div></div>"
        )
    else:
        raise ValueError(f"Unknown version: {version}. Must be '1a', '1b', or '2'")
    
    attention_rows = [
        {'id': '0_testing', 'text': attention_text},
        {'id': '1_testing', 'text': attention_text}
    ]
    # Insert the attention check rows at the top
    df_with_attention = pd.concat([pd.DataFrame(attention_rows), df], ignore_index=True)
    return df_with_attention

def convert_dataframe_to_html_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert the input dataframe to the desired HTML format with id,text columns for v1a/v1b
    
    Args:
        df: pandas DataFrame with columns: scenario_id, description, action1, action2, value1, value2, value_dict
    
    Returns:
        pandas DataFrame with columns: id, text
    """
    converted_data = []
    
    for _, row in df.iterrows():
        # Extract values from the row
        scenario_id = row['scenario_id']
        description = row['description']
        action1 = row['action1']
        action2 = row['action2']
        value1 = row['value1']
        value2 = row['value2']
        value_dict_name = row['value_dict']
        
        # Get the value dictionary from cache or load it
        value_dict = get_value_dict(value_dict_name)
        
        # Build the HTML text according to the specified format
        html_text = (
            f"<div class='scenario-section'>"
            f"<div class='scenario-title'>Description:</div>"
            f"<div class='scenario-content'>{description}</div>"
            f"</div>"
            f"<div class='scenario-section'>"
            f"<div class='scenario-title'>Candidate Chatbot Action A:</div>"
            f"<div class='action-item'>{action1}</div>"
            f"</div>"
            f"<div class='scenario-section'>"
            f"<div class='scenario-title'>Candidate Chatbot Action B:</div>"
            f"<div class='action-item'>{action2}</div>"
            f"</div>"
            f"<div class='scenario-section'>"
            f"<div class='scenario-title'>Value 1:</div>"
            f"<div class='value-item'>{value1} ({value_dict[value1]})</div>"
            f"</div>"
            f"<div class='scenario-section'>"
            f"<div class='scenario-title'>Value 2:</div>"
            f"<div class='value-item'>{value2} ({value_dict[value2]})</div>"
            f"</div>"
            f"<div class='scenario-section'>"
            f"<div class='scenario-title'>Value Set:</div>"
            f"<div class='value-item'>"
            + '<br>'.join([f'{value} ({value_dict[value]})' for value in value_dict.keys()])
            + "</div>"
            f"</div>"
        )
        
        converted_data.append({
            'id': scenario_id,
            'text': html_text
        })
    
    return pd.DataFrame(converted_data)

def convert_dataframe_to_html_format_v2(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert the input dataframe to the HTML format for v2 (transcript evaluation)
    
    Args:
        df: pandas DataFrame with columns: scenario_id, description, action1, action2, value1, value2, 
            value_dict, conversation
    
    Returns:
        pandas DataFrame with columns: id, text
    """
    converted_data = []
    
    for _, row in df.iterrows():
        # Extract values from the row
        scenario_id = row['scenario_id']
        description = row['description']  # Used as scenario summary
        action1 = row['action1']
        action2 = row['action2']
        value1 = row['value1']
        value2 = row['value2']
        value_dict_name = row['value_dict']
        conversation = row.get('conversation', 'Conversation not provided')
        
        # Parse the conversation format 'USER: [text]\n\nASSISTANT: [text]'
        try:
            parts = conversation.split('\n\nASSISTANT: ')
            if len(parts) == 2:
                user_prompt = parts[0].replace('USER: ', '', 1)
                model_response = parts[1]
            else:
                # Fallback if format doesn't match expected pattern
                user_prompt = conversation
                model_response = 'Could not parse model response'
        except Exception:
            user_prompt = conversation
            model_response = 'Could not parse model response'
        
        # Get the value dictionary from cache or load it
        value_dict = get_value_dict(value_dict_name)
        
        # Build the HTML text for v2 format
        html_text = (
            f"<div class='scenario-section' data-version='2'>"
            f"<div class='scenario-title'>Scenario Summary:</div>"
            f"<div class='scenario-content'>{description}</div>"
            f"</div>"
            f"<div class='scenario-section'>"
            f"<div class='scenario-title'>Candidate Chatbot Action A:</div>"
            f"<div class='action-item'>{action1}</div>"
            f"</div>"
            f"<div class='scenario-section'>"
            f"<div class='scenario-title'>Value A:</div>"
            f"<div class='value-item'>{value1} ({value_dict[value1]})</div>"
            f"</div>"
            f"<div class='scenario-section'>"
            f"<div class='scenario-title'>Candidate Chatbot Action B:</div>"
            f"<div class='action-item'>{action2}</div>"
            f"</div>"
            f"<div class='scenario-section'>"
            f"<div class='scenario-title'>Value B:</div>"
            f"<div class='value-item'>{value2} ({value_dict[value2]})</div>"
            f"</div>"
            f"<div class='transcript-section'>"
            f"<div class='transcript-title'>Transcript:</div>"
            f"<div class='transcript-content'>"
            f"<div class='user-prompt'><strong>User Prompt:</strong><br>{user_prompt}</div>"
            f"<div class='model-response'><strong>Model Response:</strong><br>{model_response}</div>"
            f"</div>"
            f"</div>"
        )
        
        converted_data.append({
            'id': scenario_id,
            'text': html_text
        })
    
    return pd.DataFrame(converted_data)

def main():
    parser = ArgumentParser()
    parser.add_argument("--input_csv", '-i', type=str, required=True)
    parser.add_argument("--output_csv", '-o', type=str, required=True)
    parser.add_argument("--no_attention_check", '-n', action='store_true')
    parser.add_argument("--version", type=str, choices=['1a', '1b', '2'], default='1a', 
                       help='Study version (1a/1b for scenario evaluation, 2 for transcript evaluation)')
    parser.add_argument("--start-idx", type=int, default=None,
                       help='Start index for DataFrame slicing (inclusive)')
    parser.add_argument("--end-idx", type=int, default=None,
                       help='End index for DataFrame slicing (exclusive)')
    args = parser.parse_args()
    
    df = pd.read_csv(args.input_csv)
    
    # Apply DataFrame slicing if start-idx or end-idx are provided
    start_idx = args.start_idx
    end_idx = args.end_idx
    if start_idx is not None or end_idx is not None:
        df = df[start_idx:end_idx]
    
    # Choose conversion function based on version
    if args.version == '2':
        converted_df = convert_dataframe_to_html_format_v2(df)
    else:
        converted_df = convert_dataframe_to_html_format(df)
    
    # Add attention checks unless disabled
    if not args.no_attention_check:
        converted_df = add_attention_check_to_df(converted_df, args.version)
    
    converted_df.to_csv(args.output_csv, index=False)
    
if __name__ == "__main__":
    main()