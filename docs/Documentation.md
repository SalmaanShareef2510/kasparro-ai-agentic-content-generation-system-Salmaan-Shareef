

-----
## ADK Product Content Generation Pipeline Documentation

This document serves as the **complete guide** for setting up and executing your Google Agent Development Kit (ADK) pipeline, which is designed to transform raw product data into structured marketing content. The pipeline utilizes a unique, decoupled architecture where individual agent names are used for session registration and execution via the global `/run` endpoint.

## 1\. Project Structure

The project employs a modular structure where each agent is self-contained within its own directory, sharing a common execution script (`main.py`) and dependencies (`requirements.txt`).

```
kspar/
├── agents/                  # Directory containing all ADK Agent modules
│   ├── comparator/
│   │   ├── agent.py     # Core Comparator logic and Pydantic models
│   │   └── .env         # Environment variables (Google API Key)
│   ├── descript/
│   │   ├── agent.py     # Core Descriptor logic and Pydantic models
│   │   └── .env
│   ├── faqgen/
│   │   ├── agent.py     # Core FAQGenerator logic and Pydantic models
│   │   └── .env
│   ├── Parser/
│   │   ├── agent.py     # Core Parser logic/models (Handles Raw Input)
│   │   └── .env
│   └── __init__.py      # Makes 'agents' a Python package
├── main.py              # Python script for orchestration and HTTP calls (The client)
└── requirements.txt     # List of all required Python libraries
```

-----

## 2\. Setup and Installation

### Prerequisites

1.  **Python 3.8+**
2.  **Google ADK SDK:** Ensure the `adk` command-line tool is installed and accessible in your environment PATH.

### Step 1: Install Dependencies

Navigate to the **`kspar/`** root directory and use the `requirements.txt` file to install all necessary Python libraries:

```bash
pip install -r requirements.txt
```

**`requirements.txt` contents:**

```
requests
pydantic
google-adk
```

### Step 2: Configure API Key

Since each agent runs independently, the Google Gemini API Key must be placed in a `.env` file **inside every single agent directory** (`Parser/.env`, `descript/.env`, etc.).

**Example `agents/Parser/.env` contents:**

```
GOOGLE_API_KEY="YOUR_API_KEY_HERE"
```

-----

## 3\. Execution Guide

### Step 1: Start the Local ADK Server (Host Agents)

The ADK server must be running to handle the HTTP execution requests from `main.py`.

1.  Navigate to the **`agents/`** directory in your terminal:

    ```bash
    cd kspar/agents/
    ```

2.  Execute the ADK server command:

    ```bash
    adk api_server
    ```

    > **Note:** The server is assumed to be running on **`http://localhost:8000`**, as configured in `main.py`. Keep this terminal window open.

### Step 2: Run the Pipeline (Client Execution)

This single script manages session setup and drives the data through all four agents sequentially.

1.  Navigate back to the **`kspar/`** root directory:

    ```bash
    cd ..
    ```

2.  Execute the client script:

    ```bash
    python main.py
    ```

-----

## 4\.Execution Flow and Data Handling

The `main.py` script implements a **shared-context, sequential execution** pipeline.

### Session and Context Registration

The `main.py` script ensures a shared context exists by performing a key step upfront:

  * The `create_new_session` function iterates through all four agent names (`Parser`, `descript`, `faqgen`, `comparator`) and registers the single **`SESSION_ID`** (`s\_abc`) and **`USER_ID`** (`u\_123`) against **each agent name individually** (e.g., `POST /apps/Parser/users/u_123/sessions/s_abc`).

### Pipeline Data Flow

The pipeline uses four separate calls to the global **`/run`** endpoint, changing only the `"appName"` in the payload for each step:

| Step | Agent Name (`appName`) | Input Data | Output Data |
| :--- | :--- | :--- | :--- |
| **1 (Parser)** | `Parser` | **Raw Product Data** (`example_raw_data`) | **Structured Data** (JSON) |
| **2 (Descriptor)** | `descript` | **Structured Data** (from Step 1) | Marketing Copy (JSON) |
| **3 (FAQ Generator)** | `faqgen` | **Structured Data** (from Step 1) | FAQ List (JSON) |
| **4 (Comparator)** | `comparator` | **Structured Data** (from Step 1) | Comparison Points (JSON) |

### Key Logic in `main.py`:

  * **Input Embedding:** The entire input (raw data in Step 1, structured data in Steps 2-4) is converted to a JSON string and placed inside the `newMessage.parts[0].text` field of the `/run` payload.
  * **Output Extraction:** The `run_agent_with_payload` function includes robust logic to extract and decode the **nested JSON string** from the final event's content (`event['content']['parts'][0]['text']`) returned by the `/run` endpoint. This ensures the output of the Parser is a usable Python dictionary for the next agents.

-----

## 5\.Configuration Details

### ADK IDs

| Parameter | Value | Purpose |
| :--- | :--- | :--- |
| `BASE_URL` | `http://localhost:8000` | Local server endpoint. |
| `USER_ID` | `u_123` | Static user identifier. |
| `SESSION_ID` | `s_abc` | Shared session context ID used in all requests. |

### Altering Input Data

To modify the product input, simply update the `example_raw_data` dictionary located within the `if __name__ == "__main__":` block of **`main.py`**. You do not need to change any agent files for a new product run.