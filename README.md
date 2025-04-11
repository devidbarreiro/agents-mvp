# Multiagent Assignment Evaluation System - Setup Guide

## Overview

This application is a multiagent system for educational assessment that enables:

* **Teachers** to create assignments with custom learning objectives
* **Students** to submit assignments and engage in AI-driven evaluation conversations
* **AI Agents** to ask relevant questions, evaluate submissions, and generate comprehensive reports

## System Requirements

* Python 3.8+
* OpenAI API key (for powering the AI agents)

## Installation

1. Clone the repository or download the code files
2. Create a virtual environment:
   ```bash
   python -m venv venvsource venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

Launch the Streamlit application with:

```bash
streamlit run app.py
```

This will start the application on your local machine, typically at http://localhost:8501

## Usage Guide

### For Teachers

1. Select the "Teacher" role in the sidebar
2. Enter your OpenAI API key
3. Navigate to the "Create Assignment" tab
4. Fill in:
   * Assignment name
   * Instructions
   * Learning objectives (add as many as needed)
   * Optional: Upload a reference document
5. Click "Create Assignment"
6. View created assignments in the "View Assignments" tab
7. Check student evaluations in the "View Reports" tab

### For Students

1. Select the "Student" role in the sidebar
2. Enter your OpenAI API key
3. Navigate to the "Submit Assignment" tab
4. Select an assignment from the dropdown
5. Submit your work by:
   * Writing your response in the text area
   * Optionally uploading a file
6. Click "Submit Assignment"
7. Engage in the follow-up conversation with the AI agent
8. View your evaluation report after completing the conversation
9. Access past evaluations in the "View Evaluations" tab

## System Architecture

The application uses several AI agents, each with specialized roles:

1. **Question Generator Agent**: Creates relevant questions based on learning objectives
2. **Conversation Agent**: Manages the student conversation to gather insights
3. **Evaluation Agent**: Assesses submissions against learning objectives
4. **Report Generator**: Creates comprehensive evaluation reports

All agents are powered by LangChain and OpenAI's GPT models.

## Data Storage

The application stores data locally in JSON files:

* `data/assignments.json`: Assignment details and learning objectives
* `data/submissions.json`: Student submissions
* `data/evaluations.json`: Evaluation reports and results

Uploaded files are stored in the appropriate subdirectories.

## Customization

To modify the evaluation criteria or agent behavior, edit the system prompts within each agent class in the code.
