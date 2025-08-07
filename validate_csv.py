from ast import Continue
import pandas as pd
from argparse import ArgumentParser

def preprocess_annotation_tsv(df):
    """
    Preprocesses annotation TSV data by consolidating Likert-style ratings into single columns.
    
    For each attribute (columns ending with ':::'), finds all related columns and takes 
    the first non-NaN value to create a single '{attribute}_score' column.
    
    Args:
        df (pd.DataFrame): Raw TSV data
        
    Returns:
        pd.DataFrame: Processed dataframe with consolidated score columns
    """
    
    # Filter out HTML columns
    non_html_columns = [col for col in df.columns if not col.lower().endswith('.html')]
    non_html_columns = [col for col in non_html_columns if 'free' not in col]
    df_filtered = df[non_html_columns].copy()
    
    # Find all base attributes by extracting the prefix before ':::'
    base_attributes = set()
    for col in df_filtered.columns:
        if ':::' in col:
            # Extract the part before the first ':::'
            attribute_name = col.split(':::')[0]
            base_attributes.add(attribute_name)
    
    # Filter out obvious survey questions (keep common rating attributes)
    # You can customize this list based on your specific attributes
    survey_questions = {
        'Which of these AI chatbots have you interacted with recently?',
        'Which of the following is your primary spoken language?',
        'Based on the instructions you have just read, what makes a scenario high-quality?',
        'Based on the instructions you have just read, which of the following justifications should you NOT give for why you chose a certain rating?',
        'Based on the instructions you have just read, what should you do if the model response doesn\'t exactly resemble either of the two Candidate Actions?',
        'Based on the instructions you have just read, when should you mark 5 for a scenario\'s Value Alignment 1?',
        'Which of these actions would be considered feasible for an AI chatbot in above scenario?'
    }
    
    # Keep only attributes that aren't survey questions
    rating_attributes = [attr for attr in base_attributes if attr not in survey_questions]
    rating_attributes = sorted(rating_attributes)
    
    # Start with essential columns
    essential_cols = ['user', 'instance_id']
    result_df = df_filtered[essential_cols].copy()
    
    # For each rating attribute, consolidate related columns
    for attr in rating_attributes:
        # Find all columns related to this attribute
        related_cols = [col for col in df_filtered.columns if col.startswith(attr + ':::')]
        if len(related_cols) < 2:
            continue
        
        print(f"Processing {attr}: found {len(related_cols)} related columns")
        
        if related_cols:
            # For each row, get the first non-empty value among the columns for this attribute
            # Replace empty strings with NaN, then use bfill to forward-fill, then take first column
            attr_data = df_filtered[related_cols].replace('', pd.NA)
            consolidated_scores = attr_data.bfill(axis=1).iloc[:, 0]
            
            # Add to result dataframe
            result_df[f'{attr}_score'] = consolidated_scores
    
    return result_df


def validate_tsv_with_preprocessing(df, expected_attention_score=2):
    """
    Complete validation pipeline: preprocess TSV data then validate annotations and attention checks.
    
    Args:
        df (pd.DataFrame): Raw TSV data
        expected_attention_score (int): Expected score for attention checks (default: 2)
        
    Returns:
        tuple: (processed_df, insufficient_annotations, failed_attention_checks)
    """
    
    # Step 1: Preprocess the data
    processed_df = preprocess_annotation_tsv(df)
    
    # Step 2: Run validation on processed data
    # Find score columns (ending with '_score')
    score_columns = [col for col in processed_df.columns if col.endswith('_score')]
    
    # 1. Find instances with insufficient annotations
    # Filter out HTML and testing instances
    non_test_df = processed_df[~processed_df['instance_id'].str.contains('testing|\.html', case=False, na=False)]
    
    # Count annotations per instance
    annotation_counts = non_test_df.groupby('instance_id').size()
    
    # Find instances with != 3 annotations
    insufficient_annotations = annotation_counts[annotation_counts != 3].index.tolist()
    
    # 2. Find users who failed attention checks
    # Filter for testing instances only
    testing_df = processed_df[processed_df['instance_id'].str.contains('testing', case=False, na=False)]
    
    failed_attention_checks = []
    
    for _, row in testing_df.iterrows():
        user = row['user']
        instance_id = row['instance_id']
        
        failed = False
        actual_responses = {}
        expected_responses = {}
        
        # Check each score column
        for col in score_columns:
            attr_name = col.replace('_score', '')
            expected_responses[attr_name] = expected_attention_score
            
            # Handle NaN values and convert to string
            actual_value = str(row[col]).strip() if pd.notna(row[col]) else -1
            try:
                actual_value = int(float(actual_value))
            except ValueError:
                actual_value = -1
            actual_responses[attr_name] = actual_value
            
            # Fail if the response doesn't match expected score
            if actual_value != expected_attention_score:
                failed = True
        
        if failed:
            failed_attention_checks.append({
                'user': user,
                'instance_id': instance_id,
                'expected_responses': expected_responses,
                'actual_responses': actual_responses
            })
    
    return processed_df, insufficient_annotations, failed_attention_checks

def main():
    parser = ArgumentParser()
    parser.add_argument("--tsv_path", type=str, required=True)
    parser.add_argument("--expected_attention_score", type=int, default=2)
    args = parser.parse_args()
    
    # Read the TSV file
    print(f"Reading TSV file: {args.tsv_path}")
    df = pd.read_csv(args.tsv_path, sep="\t")
    print(f"Original data shape: {df.shape}")
    
    # Process and validate
    processed_df, insufficient, failed = validate_tsv_with_preprocessing(df, args.expected_attention_score)
    
    # Save the processed CSV
    processed_path = args.tsv_path.replace('.tsv', '_processed.tsv')
    processed_df.to_csv(processed_path, sep='\t', index=False)
    print(f"Processed data saved to: {processed_path}")
    print(f"Processed data shape: {processed_df.shape}")
    
    # Print validation results
    print(f"Instances with insufficient annotations ({len(insufficient)}): {insufficient}")
    print(f"Users who failed attention checks ({len(failed)}): {failed}")
    
    # --- New code: Check users who did not annotate 10 (non-html, non-testing) instances ---
    # Filter out HTML and testing instances
    non_test_df = processed_df[~processed_df['instance_id'].str.contains('testing|\.html', case=False, na=False)]
    user_instance_counts = non_test_df.groupby('user')['instance_id'].nunique()
    users_not_10 = user_instance_counts[user_instance_counts != 10]
    if not users_not_10.empty:
        print("\nUsers who did not annotate 10 (non-html, non-testing) instances:")
        for user, count in users_not_10.items():
            print(f"  User: {user} - Annotated {count} instances")
    # -------------------------------------------------------------------------
    
    if failed:
        print("\nDetailed attention check failures:")
        for failure in failed:
            print(f"  User: {failure['user']}")
            print(f"  Instance: {failure['instance_id']}")
            print(f"  Expected: {failure['expected_responses']}")
            print(f"  Actual: {failure['actual_responses']}")
            print()


if __name__ == "__main__":
    main()