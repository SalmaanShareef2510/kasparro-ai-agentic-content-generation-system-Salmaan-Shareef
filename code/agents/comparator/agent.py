# agents/Comparator.py

from google.adk.agents import Agent
from pydantic import BaseModel, Field
from typing import List, Dict, Union

# --- Output Models for Comparator Agent ---

class ComparisonPoint(BaseModel):
    """
    A single point used for comparing this product against others.
    """
    category: str = Field(description="The category of comparison (e.g., 'Primary Active', 'Targeted Issue', 'Price Point').")
    value: Union[str, List[str]] = Field(description="The specific data point being compared (e.g., '2% Salicylic Acid', ['Oily', 'Acne-Prone']).")
    comparison_summary: str = Field(description="A concise sentence describing its competitive positioning (e.g., 'Highest BHA concentration in its class for maximum exfoliation.', 'Positions in the mid-range budget category.').")

class ComparisonOutput(BaseModel):
    """
    The final structured output used to feed comparison tables or features.
    """
    key_comparison_points: List[ComparisonPoint] = Field(
        description="A list of 5-7 structured points essential for comparing this product to rivals."
    )
    neutral_feature_summary: str = Field(
        description="A short summary of any neutral features (e.g., texture, color, packaging) that don't offer a strong competitive edge but are good to know."
    )
    potential_disadvantages: str = Field(
        description="A concise statement on the product's primary trade-offs or disadvantages, derived from 'potential_risks' and 'price_tag' for balanced comparison."
    )


# --- Agent Definition ---

root_agent = Agent(
    name="comparator",
    model="gemini-2.5-flash",
    description="Analyzes structured product data to generate key points for product comparison.",
    instruction="""
You are the **Product Comparator Agent**.
Your **single responsibility** is to analyze the input and extract or synthesize features that are critical for competitive analysis and comparison tables vs others.

**Steps:**
1.  **Identify 5-7 Key Comparison Points:** Focus on the 'concentration', 'primary_benefits', 'target_skin_types', and 'price_tag'.
2.  **Generate `ComparisonPoint` Objects:** For each point, provide a `comparison_summary` that frames the value as a competitive edge or a clear classification point.
3.  **Summarize Disadvantages:** Use the 'potential_risks' and 'price_tag' to synthesize a statement on its competitive disadvantages (e.g., high price, risk of irritation).
4.  **Do Not Add External Data:** All analysis must be based strictly on the provided input data.
""",
    output_schema=ComparisonOutput,
)