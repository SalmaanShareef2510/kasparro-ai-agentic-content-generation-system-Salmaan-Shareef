# agents/Descriptor.py
from google.adk.agents import Agent
from pydantic import BaseModel, Field
 # Input from Parser

# --- Output Model for Descriptor Agent ---
class DescriptorOutput(BaseModel):
    product_description: str = Field(description="A compelling, SEO-friendly 200-word product description.")
    marketing_slogan: str = Field(description="A short, catchy tagline for the product.")

root_agent = Agent(
    name="descript",
    model="gemini-2.5-flash",
    description="Generates product descriptions and marketing copy from structured data.",
    instruction="""
You are the **Product Description Agent**.
Your input is the fully structured data about a cosmetic product.
Generate a compelling, detailed product description (approx. 200 words) and a catchy marketing slogan.
Focus on the key ingredients, primary benefits, and suitable skin types.
""",
    output_schema=DescriptorOutput,
)