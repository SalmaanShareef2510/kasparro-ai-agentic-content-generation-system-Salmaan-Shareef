# agents/FAQGenerator.py

from google.adk.agents import Agent
from pydantic import BaseModel, Field
from typing import List 

# --- Output Model for FAQ Agent ---
class FAQItem(BaseModel):
    question: str = Field(description="A common question a user might have.")
    answer: str = Field(description="A concise answer based only on the provided data.")

class FAQOutput(BaseModel):
    faqs: List[FAQItem] = Field(description="A list of 5-7 frequently asked questions and answers.")

root_agent =Agent(
    name="faqgen",
    model="gemini-2.5-flash",
    description="Generates FAQs based on product usage, ingredients, and side effects.",
    instruction="""
You are the **FAQ Generation Agent**.
Analyze the structured product data, focusing on 'How_to_Use', 'Side_Effects','Advantages' and 'ingredient_functionality'.
Generate a list of 15 relevant questions and provide short, accurate answers using only the provided information formally.
""",
    output_schema=FAQOutput,
)