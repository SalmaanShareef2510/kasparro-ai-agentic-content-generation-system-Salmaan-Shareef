import requests
import json
from typing import Dict, Any, Optional, List


BASE_URL = "http://localhost:8000"
USER_ID = "u_123"
SESSION_ID = "s_abc" 

 ###
AGENT_NAMES = {
    "Parser": "Parser", 
    "Descriptor": "descript", 
    "FAQGenerator": "faqgen", 
    "Comparator": "comparator"
}


def get_session_creation_url(agent_name: str, session_id: str):

    return f"{BASE_URL}/apps/{agent_name}/users/{USER_ID}/sessions/{session_id}"


def get_run_agent_url():
  
    return f"{BASE_URL}/run"


def create_new_session(session_id: str, context_data: Dict[str, Any]) -> bool:
    """
    Registers the session context for ALL required agents.
    """
    print(f"\n🚀 Registering session '{session_id}' across all agents...")
    
    all_successful = True
    
    # Iterate through all agent names to register the session context for each one
    for name, app_id in AGENT_NAMES.items():
        session_url = get_session_creation_url(app_id, session_id)
        headers = {"Content-Type": "application/json"}
        
        print(f"   -> Registering for {name} ({app_id}) at {session_url}...")
        
        try:
            # POST request to create/update the session context
            response = requests.post(session_url, headers=headers, data=json.dumps(context_data))
            response.raise_for_status()
            print(f"   ✅ Registered successfully.")
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Failed registration for {name}. Error: {e}")
            all_successful = False

    return all_successful


def run_agent_with_payload(agent_name: str, input_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:

    payload = {
        "appName": agent_name, # The specific agent name
        "userId": USER_ID,
        "sessionId": SESSION_ID, # The registered session ID
        "newMessage": {
            "role": "user",
            # Input payload is sent as a JSON string
            "parts": [
                {"text": json.dumps(input_payload)}
            ]
        }
    }
    
    headers = {"Content-Type": "application/json"}
    run_url = get_run_agent_url()
    
    print(f"\n--- Calling {agent_name} Agent via /run ---")
    
    try:
        response = requests.post(run_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        
        result_events: List[Dict[str, Any]] = response.json()
        print(f"✅ {agent_name} Agent responded with {len(result_events)} events.")
        
        # --- Locate and extract the final structured output ---
        final_content_event = next(
            (event for event in reversed(result_events) 
             if event.get('content') and event['content'].get('role') == 'model'),
            None
        )

        if not final_content_event:
            # Fallback for older ADK versions if 'content' isn't used
            final_response = next(
                (event.get('output') for event in reversed(result_events) if event.get('output') is not None),
                None
            )
            if final_response:
                return final_response
            
            print(f"⚠️ Could not find the final structured output event for {agent_name}.")
            return None
            
        # Extract the nested JSON string and deserialize it
        nested_json_string = final_content_event['content']['parts'][0]['text']
        final_structured_data = json.loads(nested_json_string)

        return final_structured_data
    
    except json.JSONDecodeError as e:
        print(f"❌ JSON Parsing Error for {agent_name}. Could not convert the nested string to a dictionary. Error: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error calling {agent_name} via /run: {e}")
        return None



def run_pipeline(raw_product_data: Dict[str, str]):
    """
    Executes the full pipeline: Parser (Raw Data) -> Others (Structured Data).
    """
    print(f"\n--- STARTING PIPELINE for Session ID: {SESSION_ID} ---")
    
    try:
        # 1. Parse Data (Input: Raw Data -> Output: Structured Data)
        print("\n[STEP 1/4: PARSING RAW DATA]")
        structured_data = run_agent_with_payload(AGENT_NAMES["Parser"], raw_product_data)
        
        if structured_data is None:
            print("\n!!! Pipeline failed at the Parser step. Execution halted. !!!")
            return

        # 2. Use Structured Data for subsequent agents
        
        print("\n[STEP 2/4: GENERATING DESCRIPTION]")
        description_output = run_agent_with_payload(AGENT_NAMES["Descriptor"], structured_data)
        
        print("\n[STEP 3/4: GENERATING FAQs]")
        faq_output = run_agent_with_payload(AGENT_NAMES["FAQGenerator"], structured_data)
        
        print("\n[STEP 4/4: GENERATING COMPARISON POINTS]")
        comparison_output = run_agent_with_payload(AGENT_NAMES["Comparator"], structured_data)
        
        
        print("\n=======================================================")
        print("           PIPELINE EXECUTION COMPLETE")
        print("=======================================================")
        
        # Aggregate and print the final output
        final_output = {
            "StructuredData": structured_data,
            "DescriptionOutput": description_output,
            "FAQOutput": faq_output,
            "ComparisonOutput": comparison_output,
        }
        
        print("\n--- FINAL AGGREGATED OUTPUT ---")
        print(json.dumps(final_output, indent=2))
        
    except Exception as e:
        print(f"\n!!! An unexpected error occurred during pipeline execution: {e} !!!")


# Example Usage


if __name__ == "__main__":
    # Example Raw Data (Input to the Parser Agent)
    example_raw_data = {
        "Product_Name": "Minimalist 2% Salicylic Acid Face Serum",
        "Concentration": "2% Salicylic Acid, 1% Zinc PCA",
        "Skin_Type": "Oily, Acne-Prone, Combination Skin",
        "Key_Ingredients": "Salicylic Acid, Zinc PCA, Aloe Vera Extract",
        "Benefits": "Exfoliates pores, reduces blackheads & whiteheads, controls oil, reduces redness.",
        "How_to_Use": "Apply 2-3 drops after cleansing and before moisturizing. Use 3-4 times a week.",
        "Side_Effects": "Mild tingling possible initially. Avoid use with other strong acids.",
        "Price": "₹699"
    }

    session_context = {"project_name": "KSPAR", "stage": "data_pipeline"}
    
    # 1. Create the session by registering the context for ALL agents
    if create_new_session(SESSION_ID, session_context):
        # 2. Run the pipeline using the shared SESSION_ID
        run_pipeline(example_raw_data)