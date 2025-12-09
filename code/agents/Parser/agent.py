from google.adk.agents import Agent
from pydantic import Field, BaseModel
from typing import List

# --- Input Model (Matches Raw Data) ---
class InputModel(BaseModel):
    Product_Name : str = Field(
        description="Name of the Product"
    )
    Concentration : str = Field(
        description="The Chemical and Ingredient Concentration in the Product"
    )
    Skin_Type : str = Field(
        description="The Suitable SkinType the product can be used"
    ) 
    Key_Ingredients : str = Field(
        description="The Main Ingredients for this product"
    )
    Benefits : str = Field(
        description="The Benefits that a person gets by using this product"
    )
    How_to_Use : str = Field(
        description="The Procedure and Usage Description of this product"
    )
    Side_Effects : str = Field(
        description="The Side Effects thay may occur by Using this Product"
    )
    Price : str = Field( # Changed to str to match raw data format (e.g., '₹699')
        description="The Price of this Product"
    )


class IngredientDetail(BaseModel):
    ingredient: str = Field(description="The name of the ingredient.")
    role: str = Field(description="A brief description of its function and importance for content generation (e.g., Comparison, Benefits).")

class OutputModel(BaseModel):
    product_name: str = Field(description="Cleaned, standardized product name.")
    price_tag: str = Field(description="The product's price, including currency.")
    concentration: str = Field(description="The primary active concentration details.")
    target_skin_types: List[str] = Field(description="List of suitable skin types, parsed from the input string.")
    usage_instructions: str = Field(description="The procedure for using the product.")
    potential_risks: str = Field(description="Any stated side effects or warnings.")
    primary_benefits: List[str] = Field(description="List of key benefits, parsed from the input string.")
    ingredient_functionality: List[IngredientDetail] = Field(
        description="A list of key ingredients and an analytical description of their content generation role."
    )

# --- Agent Definition with Instructions ---
root_agent = Agent(
    name="Parser",
    model="gemini-2.5-flash",
    description="You are the Data Parsing and Internal Model Generator Agent. You transform raw product data into a structured JSON model for content generation.",
    instruction="""
You are the **Data Parser and Internal Model Generator Agent**.
Your **single responsibility** is to analyze the raw input product data and transform it into a clean, comprehensive, machine-readable JSON object that strictly adheres to the provided `OutputModel` schema.

**Steps:**
1.  **Parse and Clean:** Extract values from the `InputModel`.
2.  **Standardize Lists:** Convert comma-separated fields like 'Skin Type', 'Key Ingredients', and 'Benefits' into clean Python lists (e.g., `["Oily", "Combination"]`).
3.  **Analyze and Structure:** For the `ingredient_functionality` field, analyze each item in the `Key_Ingredients` list and provide an **in-depth description** of its role. This role should be written to be immediately useful for the downstream FAQ, Description, and Comparison Agents (e.g., 'Primary hydrating agent for comparison against other emollients.').
4.  **Do Not Add New Facts:** You must only use the information provided in the input data[cite: 23].

**Goal:** Produce a validated `OutputModel` object that serves as the single, reliable source of truth for the entire content generation pipeline.
""",
input_schema=InputModel,
output_schema=OutputModel,


)