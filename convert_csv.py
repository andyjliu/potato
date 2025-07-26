import pandas as pd
from argparse import ArgumentParser
from typing import Dict
import json

def add_attention_check_to_df(df: pd.DataFrame) -> pd.DataFrame:
    attention_row = {
        'id': '0_testing',
        'text': (
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
    }
    # Insert the attention check row at the top
    df_with_attention = pd.concat([pd.DataFrame([attention_row]), df], ignore_index=True)
    return df_with_attention
    

def convert_dataframe_to_html_format(df: pd.DataFrame, value_dict: Dict[str, str]) -> pd.DataFrame:
    """
    Convert the input dataframe to the desired HTML format with id,text columns
    
    Args:
        df: pandas DataFrame with columns: scenario_id, description, action1, action2, value1, value2
        value_dict: Dictionary mapping value names to their descriptions
    
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


def main():
    parser = ArgumentParser()
    parser.add_argument("--input_csv", '-i', type=str, required=True)
    parser.add_argument("--output_csv", '-o', type=str, required=True)
    parser.add_argument("--value_dict", '-v', type=str, required=True)
    parser.add_argument("--no_attention_check", '-n', action='store_true')
    args = parser.parse_args()
    
    df = pd.read_csv(args.input_csv)
    value_dict_path = f'value_sets/{args.value_dict}.json'
    with open(value_dict_path, 'r') as f:
        value_dict = json.load(f)
    converted_df = convert_dataframe_to_html_format(df, value_dict)
    if not args.no_attention_check:
        converted_df = add_attention_check_to_df(converted_df)
    converted_df.to_csv(args.output_csv, index=False)
    
if __name__ == "__main__":
    main()
    
    
# /Users/andyliu/develop/potato/data/claude-3-5-sonnet-latest.csv
# /Users/andyliu/develop/potato/project-hub/conflictbench_v1a-LOCAL/data_files/pilot_data