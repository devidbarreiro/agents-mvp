import streamlit as st
import os
import json
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain.agents import Tool, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain, ConversationChain
from langchain_community.callbacks import StreamlitCallbackHandler

# UI text translations
ui_text = {
    "English": {
        "app_title": "Educational Assignment Evaluation System",
        "api_key_label": "OpenAI API Key",
        "api_key_warning": "Please enter your OpenAI API key to proceed.",
        "user_role_label": "Select your role:",
        "teacher_role": "Teacher",
        "student_role": "Student",
        "api_key_info": "Enter your OpenAI API key in the sidebar to get started.",
        "teacher_dashboard": "Teacher Dashboard",
        "create_tab": "Create Assignment",
        "view_tab": "View Assignments",
        "reports_tab": "View Reports",
        "create_new": "Create New Assignment",
        "assignment_name": "Assignment Name",
        "assignment_instructions": "Assignment Instructions",
        "questions_slider": "Number of Questions to Ask Students",
        "questions_help": "Select how many questions will be asked to evaluate the student's work",
        "learning_obj_title": "Learning Objectives",
        "learning_obj_desc": "Define the learning objectives for this assignment.",
        "objective_label": "Objective",
        "remove_btn": "Remove",
        "add_obj_btn": "Add Objective",
        "upload_label": "Upload Assignment Document (Optional)",
        "create_btn": "Create Assignment",
        "fields_error": "Please fill in all required fields (name, instructions, at least one learning objective).",
        "created_success": "Assignment '{name}' created successfully!",
        "no_assignments": "No assignments created yet.",
        "select_assignment": "Select Assignment",
        "instructions_label": "Instructions",
        "obj_label": "Learning Objectives",
        "file_label": "Attached File",
        "file_prefix": "File: ",
        "id_label": "Assignment ID",
        "created_label": "Created",
        "delete_btn": "Delete Assignment",
        "deleted_success": "Assignment deleted successfully!",
        "view_evals_title": "View Evaluation Reports",
        "no_evals": "No evaluations available yet.",
        "reports_for": "Reports for: ",
        "select_eval": "Select Evaluation Report",
        "report_from": "Report from ",
        "eval_report_label": "Evaluation Report",
        "detailed_eval_label": "Detailed Evaluation Data",
        "student_dashboard": "Student Dashboard",
        "submit_tab": "Submit Assignment",
        "evals_tab": "View Evaluations",
        "eval_conversation": "Evaluation Conversation",
        "eval_complete": "Evaluation complete! Here's your assessment report:",
        "new_submission_btn": "Start a New Submission",
        "submit_assignment": "Submit Assignment",
        "no_assignments_submit": "No assignments available for submission.",
        "assignment_details": "Assignment Details",
        "your_submission": "Your Submission",
        "response_placeholder": "Enter your assignment response here",
        "response_help": "Write your response to the assignment here.",
        "upload_submission": "Upload Your Assignment (Optional)",
        "upload_help": "You can optionally upload a file with your assignment submission.",
        "submit_btn": "Submit Assignment",
        "submission_error": "Please either write your submission or upload a file.",
        "submitted_success": "Assignment submitted successfully! Let's begin the evaluation conversation.",
        "view_your_evals": "View Your Evaluations",
        "no_evals_yet": "No evaluations available yet. Submit an assignment to get evaluated.",
        "report_for": "Evaluation Report for ",
        "report_label": "Report"
    },
    "Español": {
        "app_title": "Sistema de Evaluación de Tareas Educativas",
        "api_key_label": "Clave API de OpenAI",
        "api_key_warning": "Por favor ingresa tu clave API de OpenAI para continuar.",
        "user_role_label": "Selecciona tu rol:",
        "teacher_role": "Profesor",
        "student_role": "Estudiante",
        "api_key_info": "Ingresa tu clave API de OpenAI en la barra lateral para comenzar.",
        "teacher_dashboard": "Panel del Profesor",
        "create_tab": "Crear Tarea",
        "view_tab": "Ver Tareas",
        "reports_tab": "Ver Informes",
        "create_new": "Crear Nueva Tarea",
        "assignment_name": "Nombre de la Tarea",
        "assignment_instructions": "Instrucciones de la Tarea",
        "questions_slider": "Número de Preguntas para Estudiantes",
        "questions_help": "Selecciona cuántas preguntas se harán para evaluar el trabajo del estudiante",
        "learning_obj_title": "Objetivos de Aprendizaje",
        "learning_obj_desc": "Define los objetivos de aprendizaje para esta tarea.",
        "objective_label": "Objetivo",
        "remove_btn": "Eliminar",
        "add_obj_btn": "Añadir Objetivo",
        "upload_label": "Subir Documento de Tarea (Opcional)",
        "create_btn": "Crear Tarea",
        "fields_error": "Por favor completa todos los campos obligatorios (nombre, instrucciones, al menos un objetivo de aprendizaje).",
        "created_success": "Tarea '{name}' creada exitosamente!",
        "no_assignments": "Aún no hay tareas creadas.",
        "select_assignment": "Seleccionar Tarea",
        "instructions_label": "Instrucciones",
        "obj_label": "Objetivos de Aprendizaje",
        "file_label": "Archivo Adjunto",
        "file_prefix": "Archivo: ",
        "id_label": "ID de Tarea",
        "created_label": "Creado",
        "delete_btn": "Eliminar Tarea",
        "deleted_success": "Tarea eliminada exitosamente!",
        "view_evals_title": "Ver Informes de Evaluación",
        "no_evals": "Aún no hay evaluaciones disponibles.",
        "reports_for": "Informes para: ",
        "select_eval": "Seleccionar Informe de Evaluación",
        "report_from": "Informe del ",
        "eval_report_label": "Informe de Evaluación",
        "detailed_eval_label": "Datos Detallados de Evaluación",
        "student_dashboard": "Panel del Estudiante",
        "submit_tab": "Entregar Tarea",
        "evals_tab": "Ver Evaluaciones",
        "eval_conversation": "Conversación de Evaluación",
        "eval_complete": "¡Evaluación completa! Aquí está tu informe de evaluación:",
        "new_submission_btn": "Iniciar una Nueva Entrega",
        "submit_assignment": "Entregar Tarea",
        "no_assignments_submit": "No hay tareas disponibles para entregar.",
        "assignment_details": "Detalles de la Tarea",
        "your_submission": "Tu Entrega",
        "response_placeholder": "Ingresa tu respuesta a la tarea aquí",
        "response_help": "Escribe tu respuesta a la tarea aquí.",
        "upload_submission": "Subir Tu Tarea (Opcional)",
        "upload_help": "Puedes subir opcionalmente un archivo con tu entrega de tarea.",
        "submit_btn": "Entregar Tarea",
        "submission_error": "Por favor escribe tu entrega o sube un archivo.",
        "submitted_success": "¡Tarea entregada con éxito! Comencemos la conversación de evaluación.",
        "view_your_evals": "Ver Tus Evaluaciones",
        "no_evals_yet": "Aún no hay evaluaciones disponibles. Entrega una tarea para ser evaluado.",
        "report_for": "Informe de Evaluación para ",
        "report_label": "Informe"
    }
}

# Function to get UI text based on language
def get_text(key, language="English"):
    """Get UI text in the specified language"""
    if language in ui_text and key in ui_text[language]:
        return ui_text[language][key]
    # Fallback to English
    return ui_text["English"].get(key, key)

# Setup directory structure
def setup_directories():
    """Create necessary directories for storing files and data"""
    dirs = ["data", "data/assignments", "data/submissions", "data/evaluations"]
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)

# File handling functions
def save_uploaded_file(uploaded_file, directory):
    """Save an uploaded file to the specified directory"""
    file_path = os.path.join(directory, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def read_file(file_path):
    """Read file contents with error handling and UTF-8 encoding"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def save_json(data, file_path):
    """Save data as JSON"""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        logging.info(f"Datos guardados en {file_path}")
    except Exception as e:
        logging.error(f"Error al guardar JSON en {file_path}: {e}")

@st.cache_data(show_spinner=False)
def load_json(file_path):
    """Load data from JSON with caching"""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


# Agent definitions
class QuestionGeneratorAgent:
    """Agent responsible for generating questions based on the assignment and learning objectives"""
    
    def __init__(self, llm):
        self.llm = llm
        self.system_prompts = {
            "English": """You are an expert educational assessment agent. 
            Your task is to generate thoughtful questions based on assignment instructions and learning objectives.
            The questions should help evaluate the student's understanding and achievement of learning objectives.
            Generate questions that are clear, specific, and directly related to the learning objectives.""",
            
            "Español": """Eres un agente experto en evaluación educativa.
            Tu tarea es generar preguntas reflexivas basadas en las instrucciones de la tarea y los objetivos de aprendizaje.
            Las preguntas deben ayudar a evaluar la comprensión del estudiante y el logro de los objetivos de aprendizaje.
            Genera preguntas claras, específicas y directamente relacionadas con los objetivos de aprendizaje."""
        }
        
    def generate_questions(self, assignment_text, learning_objectives, num_questions=5, language="English"):
        """Generate questions based on assignment and learning objectives"""
        
        system_prompt = self.system_prompts.get(language, self.system_prompts["English"])
        
        prompt_templates = {
            "English": "Assignment Instructions:\n{assignment_text}\n\n"
                      "Learning Objectives:\n{learning_objectives}\n\n"
                      "Generate {num_questions} questions that will help assess if a student has met these learning objectives.",
                      
            "Español": "Instrucciones de la tarea:\n{assignment_text}\n\n"
                      "Objetivos de aprendizaje:\n{learning_objectives}\n\n"
                      "Genera {num_questions} preguntas que ayuden a evaluar si un estudiante ha alcanzado estos objetivos de aprendizaje."
        }
        
        prompt_template = prompt_templates.get(language, prompt_templates["English"])
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template(prompt_template)
        ])
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        try:
            response = chain.run(
                assignment_text=assignment_text,
                learning_objectives="\n".join([f"- {obj}" for obj in learning_objectives]),
                num_questions=num_questions
            )
        except Exception as e:
            # Loggear el error y devolver una lista vacía
            logging.error(f"Error generando preguntas: {e}")
            response = ""
        
        # Parse the questions from the response
        questions = []
        for line in response.split("\n"):
            line = line.strip()
            if line and (line.startswith("- ") or line.startswith("Q") or line[0].isdigit() and line[1] in [".", ")"]):
                # Clean up the question format
                question = line
                if line.startswith("- "):
                    question = line[2:]
                elif line[0].isdigit() and line[1] in [".", ")"]:
                    question = line[2:].strip()
                elif line.startswith("Q") and ":" in line:
                    question = line.split(":", 1)[1].strip()
                
                questions.append(question)
        
        return questions[:num_questions]  # Ensure we only return the requested number

class ConversationAgent:
    """Agent that converses with the student, asking questions and recording responses"""
    
    def __init__(self, llm):
        self.llm = llm
        self.memory = ConversationBufferMemory(return_messages=True)
        self.system_prompts = {
            "English": """You are a friendly educational assistant conducting an assessment conversation.
            Ask questions in a supportive and encouraging manner. Listen carefully to student responses.
            Your goal is to understand the student's comprehension and thought process, not to judge or evaluate at this stage.""",
            
            "Español": """Eres un asistente educativo amigable que realiza una conversación de evaluación.
            Haz preguntas de manera solidaria y alentadora. Escucha atentamente las respuestas de los estudiantes.
            Tu objetivo es comprender la comprensión y el proceso de pensamiento del estudiante, no juzgar o evaluar en esta etapa."""
        }
        
        self.intro_messages = {
            "English": "I'd like to ask you a few questions about your assignment to understand your thought process better.",
            "Español": "Me gustaría hacerte algunas preguntas sobre tu tarea para entender mejor tu proceso de pensamiento."
        }
        
        self.response_acknowledgments = {
            "English": "Thank you for your response.",
            "Español": "Gracias por tu respuesta."
        }
        
        self.completion_messages = {
            "English": "Thank you for answering all the questions. I'll now analyze your responses.",
            "Español": "Gracias por responder todas las preguntas. Ahora analizaré tus respuestas."
        }
        
    def start_conversation(self, questions, language="English"):
        """Initialize the conversation with the student"""
        self.questions = questions
        self.current_question_idx = 0
        self.conversation_history = []
        self.student_responses = {}
        self.language = language
        self.timestamps = []  # Add timestamps to track response times
        self.timestamps.append(datetime.now().isoformat())  # Initial timestamp
        
        return {
            "message": self.intro_messages.get(language, self.intro_messages["English"]),
            "question": questions[0],
            "done": False
        }
    
    def continue_conversation(self, student_response):
        """Process student response and continue conversation"""
        # Record timestamp for this response
        self.timestamps.append(datetime.now().isoformat())
        
        # Record response
        current_question = self.questions[self.current_question_idx]
        self.student_responses[current_question] = student_response
        
        # Update conversation history
        self.conversation_history.append({"question": current_question, "response": student_response})
        
        # Move to next question or finish
        self.current_question_idx += 1
        if self.current_question_idx < len(self.questions):
            next_question = self.questions[self.current_question_idx]
            return {
                "message": self.response_acknowledgments.get(self.language, self.response_acknowledgments["English"]),
                "question": next_question,
                "done": False
            }
        else:
            return {
                "message": self.completion_messages.get(self.language, self.completion_messages["English"]),
                "question": None,
                "done": True
            }
    
    def get_conversation_summary(self, language="English"):
        """Generate a summary of the conversation"""
        system_prompt_templates = {
            "English": "You are an educational assessment expert. Summarize the following student responses to questions.",
            "Español": "Eres un experto en evaluación educativa. Resume las siguientes respuestas del estudiante a las preguntas."
        }
        
        human_prompt_templates = {
            "English": "Here are the questions and student responses:\n{conversation}\n\n"
                    "Provide a concise summary of the conversation highlighting key points from the student's responses.",
            "Español": "Aquí están las preguntas y las respuestas del estudiante:\n{conversation}\n\n"
                     "Proporciona un resumen conciso de la conversación destacando los puntos clave de las respuestas del estudiante."
        }
        
        system_prompt = system_prompt_templates.get(language, system_prompt_templates["English"])
        human_prompt = human_prompt_templates.get(language, human_prompt_templates["English"])
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template(human_prompt)
        ])
        
        conversation_text = "\n\n".join([
            f"Question: {item['question']}\nResponse: {item['response']}" 
            for item in self.conversation_history
        ])
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        try:
            summary = chain.run(conversation=conversation_text)
        except Exception as e:
            logging.error(f"Error generando resumen de conversación: {e}")
            summary = "No se pudo generar el resumen de la conversación."
        
        return {
            "conversation_history": self.conversation_history,
            "summary": summary,
            "responses": self.student_responses,
            "language": language,
            "timestamps": self.timestamps  # Include timestamps for response time analysis
        }

class EvaluationAgent:
    """Agent that evaluates the student's work and conversation responses"""
    
    def __init__(self, llm):
        self.llm = llm
        self.system_prompts = {
            "English": """You are an expert educational evaluator.
            Your task is to assess student work and conversation responses against specific learning objectives.
            Provide a fair, balanced, and constructive evaluation. Back up your assessments with specific evidence from the student's work and responses.""",
            
            "Español": """Eres un evaluador educativo experto.
            Tu tarea es evaluar el trabajo del estudiante y las respuestas de la conversación en relación con objetivos de aprendizaje específicos.
            Proporciona una evaluación justa, equilibrada y constructiva. Respalda tus evaluaciones con ejemplos específicos del trabajo y las respuestas del estudiante.
            Debes analizar cuidadosamente la autenticidad del trabajo, detectando posible plagio o contenido copiado."""
        }
        
        self.prompt_part1_templates = {
            "English": "Assignment Instructions:\n{assignment_text}\n\n"
                     "Student Submission:\n{submission_text}\n\n"
                     "Conversation Summary:\n{conversation_summary}\n\n"
                     "Evaluate the student's work on the following criteria:\n"
                     "1. Comprehension - How well does the student understand the core concepts?\n"
                     "2. Authenticity - Is the work original and does it show the student's own thinking?\n\n"
                     "For each criterion, provide:\n"
                     "- A score (0-100, where 100 is excellent)\n"
                     "- Specific examples from the work or conversation\n"
                     "- Constructive feedback",
                     
            "Español": "Instrucciones de la tarea:\n{assignment_text}\n\n"
                      "Entrega del estudiante:\n{submission_text}\n\n"
                      "Resumen de la conversación:\n{conversation_summary}\n\n"
                      "Tiempos de respuesta: {response_times}\n\n"
                      "Evalúa el trabajo del estudiante según los siguientes criterios:\n"
                      "1. Comprensión (0-100) - ¿Qué tan bien comprende el estudiante los conceptos centrales?\n"
                      "2. Autenticidad (0-100) - ¿Es el trabajo original y muestra el propio pensamiento del estudiante? Detecta si hay contenido copiado o plagiado.\n"
                      "3. Habilidades relacionales (0-100) - ¿Cómo conecta el estudiante diferentes conceptos e ideas?\n"
                      "4. Argumentación (0-100) - ¿Qué tan bien estructurados y fundamentados están sus argumentos?\n"
                      "5. Uso de bibliografía (0-100) - ¿Cita o hace referencia a bibliografía adecuada?\n\n"
                      "Para cada criterio, proporciona:\n"
                      "- Una puntuación (0-100, donde 100 es excelente)\n"
                      "- Ejemplos específicos del trabajo o la conversación\n"
                      "- Retroalimentación constructiva\n\n"
                      "Analiza también:\n"
                      "- Consistencia entre el trabajo escrito y las respuestas en la conversación\n"
                      "- Si los tiempos de respuesta son coherentes con la cantidad de contenido (respuestas muy elaboradas en tiempos muy cortos podrían indicar uso de contenido pregenerado)\n"
                      "- Indica claramente si detectas copypaste o plagio, proporcionando evidencia"
        }
        
        self.prompt_part2_templates = {
            "English": "Assignment Instructions:\n{assignment_text}\n\n"
                     "Learning Objectives:\n{learning_objectives}\n\n"
                     "Student Submission:\n{submission_text}\n\n"
                     "Conversation Summary:\n{conversation_summary}\n\n"
                     "Evaluate how well the student's work achieves each of the following learning objectives. "
                     "For each objective, provide:\n"
                     "- A score (0-100, where 100 is excellent)\n" 
                     "- Specific examples from the work or conversation\n"
                     "- Constructive feedback",
                     
            "Español": "Instrucciones de la tarea:\n{assignment_text}\n\n"
                      "Objetivos de aprendizaje:\n{learning_objectives}\n\n"
                      "Entrega del estudiante:\n{submission_text}\n\n"
                      "Resumen de la conversación:\n{conversation_summary}\n\n"
                      "Conversación completa:\n{conversation_details}\n\n"
                      "Evalúa qué tan bien el trabajo del estudiante logra cada uno de los siguientes objetivos de aprendizaje. "
                      "Para cada objetivo, proporciona:\n"
                      "- Una puntuación (0-100, donde 100 es excelente)\n"
                      "- Ejemplos específicos del trabajo o la conversación\n"
                      "- Retroalimentación constructiva"
        }
        
        self.prompt_part3_templates = {
            "English": "Assignment Instructions:\n{assignment_text}\n\n"
                     "Student Submission:\n{submission_text}\n\n"
                     "Evaluate the overall quality of the student's work, considering clarity, organization, and depth of thought.\n"
                     "Provide:\n"
                     "- A score (0-100, where 100 is excellent)\n"
                     "- Specific examples from the work\n"
                     "- Constructive feedback",
                     
            "Español": "Instrucciones de la tarea:\n{assignment_text}\n\n"
                      "Entrega del estudiante:\n{submission_text}\n\n"
                      "Conversación completa:\n{conversation_details}\n\n"
                      "Evalúa la calidad general del trabajo del estudiante, considerando claridad, organización y profundidad de pensamiento.\n"
                      "Proporciona:\n"
                      "- Una puntuación global (0-100, donde 100 es excelente)\n"
                      "- Ejemplos específicos del trabajo\n"
                      "- Retroalimentación constructiva\n\n"
                      "Realiza también un análisis final sobre la originalidad del trabajo y la coherencia entre la entrega escrita y las respuestas durante la conversación."
        }
        
        self.section_headers = {
            "English": {
                "comprehension": "# Comprehension and Authenticity Evaluation",
                "objectives": "# Learning Objectives Evaluation",
                "overall": "# Overall Quality Evaluation"
            },
            "Español": {
                "comprehension": "# Evaluación de comprensión, autenticidad y habilidades",
                "objectives": "# Evaluación de objetivos de aprendizaje",
                "overall": "# Evaluación de calidad general y análisis de originalidad"
            }
        }
        
    def evaluate_submission(self, assignment_text, assignment_file_path, submission_text, 
                          learning_objectives, conversation_data):
        """Evaluate the student's submission against learning objectives"""
        # Get the language from conversation data
        language = conversation_data.get("language", "Español")
        
        # Truncate long inputs to avoid context length issues
        max_chars = 3000  # Approximate limit to avoid exceeding token limits
        
        if len(assignment_text) > max_chars:
            assignment_text = assignment_text[:max_chars] + "... [truncated]"
            
        if len(submission_text) > max_chars:
            submission_text = submission_text[:max_chars] + "... [truncated]"
        
        # Calculate response times if available in conversation_data
        response_times_text = "No disponible"
        if "timestamps" in conversation_data:
            response_times = []
            for i, timestamp in enumerate(conversation_data["timestamps"]):
                if i > 0:
                    prev_time = datetime.fromisoformat(conversation_data["timestamps"][i-1])
                    curr_time = datetime.fromisoformat(timestamp)
                    response_time = (curr_time - prev_time).total_seconds()
                    question = conversation_data["conversation_history"][i-1]["question"]
                    response = conversation_data["conversation_history"][i-1]["response"]
                    response_times.append({
                        "question": question[:50] + "..." if len(question) > 50 else question,
                        "response_length": len(response),
                        "time_seconds": response_time
                    })
            
            if response_times:
                response_times_text = "\n".join([
                    f"Pregunta {i+1}: {rt['time_seconds']:.1f} segundos para {rt['response_length']} caracteres" 
                    for i, rt in enumerate(response_times)
                ])
        
        # We'll do the evaluation in steps to avoid context length issues
        system_prompt = self.system_prompts.get(language, self.system_prompts["Español"])
        
        # Extract conversation details
        conversation_details = "\n\n".join([
            f"Pregunta: {item['question']}\nRespuesta: {item['response']}" 
            for item in conversation_data["conversation_history"]
        ])
        
        # Step 1: Evaluate comprehension, authenticity and other skills
        prompt_part1 = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template(
                self.prompt_part1_templates.get(language, self.prompt_part1_templates["Español"])
            )
        ])
        
        chain_part1 = LLMChain(llm=self.llm, prompt=prompt_part1)
        try:
            evaluation_part1 = chain_part1.run(
                assignment_text=assignment_text,
                submission_text=submission_text,
                conversation_summary=conversation_data["summary"],
                response_times=response_times_text
            )
        except Exception as e:
            logging.error(f"Error en evaluación parte 1: {e}")
            evaluation_part1 = "Error en evaluación de comprensión y autenticidad."

        
        # Step 2: Evaluate learning objectives
        learning_obj_text = "\n".join([f"- {obj}" for obj in learning_objectives])
        
        prompt_part2 = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template(
                self.prompt_part2_templates.get(language, self.prompt_part2_templates["Español"])
            )
        ])
        
        chain_part2 = LLMChain(llm=self.llm, prompt=prompt_part2)
        evaluation_part2 = chain_part2.run(
            assignment_text=assignment_text,
            learning_objectives=learning_obj_text,
            submission_text=submission_text,
            conversation_summary=conversation_data["summary"],
            conversation_details=conversation_details
        )
        
        # Step 3: Evaluate overall quality
        prompt_part3 = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template(
                self.prompt_part3_templates.get(language, self.prompt_part3_templates["Español"])
            )
        ])
        
        chain_part3 = LLMChain(llm=self.llm, prompt=prompt_part3)
        evaluation_part3 = chain_part3.run(
            assignment_text=assignment_text,
            submission_text=submission_text,
            conversation_details=conversation_details
        )
        
        # Get section headers based on language
        headers = self.section_headers.get(language, self.section_headers["Español"])
        
        # Combine all evaluations
        evaluation = (
            f"{headers['comprehension']}\n" + evaluation_part1 + 
            f"\n\n{headers['objectives']}\n" + evaluation_part2 +
            f"\n\n{headers['overall']}\n" + evaluation_part3
        )
        
        
        
        # Generate a structured evaluation result
        prompt_structured_templates = {
            "English": "Evaluation:\n{evaluation}\n\n"
                     "Convert this into a JSON structure with the following keys:\n"
                     "- comprehension: {{score: (number 0-100), examples: (text with examples), feedback: (constructive feedback)}}\n"
                     "- authenticity: {{score: (number 0-100), examples: (text with examples), feedback: (constructive feedback)}}\n"
                     "- relational_skills: {{score: (number 0-100), examples: (text with examples), feedback: (constructive feedback)}}\n"
                     "- argumentation: {{score: (number 0-100), examples: (text with examples), feedback: (constructive feedback)}}\n"
                     "- bibliography_use: {{score: (number 0-100), examples: (text with examples), feedback: (constructive feedback)}}\n"
                     "- learning_objectives: [{{objective: (text of objective), score: (number 0-100), examples: (text with examples), feedback: (constructive feedback)}}]\n"
                     "- overall_quality: {{score: (number 0-100), examples: (text with examples), feedback: (constructive feedback)}}\n"
                     "- plagiarism_detected: (boolean true/false)\n"
                     "- plagiarism_evidence: (text explaining evidence of plagiarism if detected)\n"
                     "- response_time_analysis: (text analyzing if response times are consistent with content)\n"
                     "- summary: (A brief summary of the evaluation)",
                     
            "Español": "Evaluación:\n{evaluation}\n\n"
                      "Convierte esto en una estructura JSON con las siguientes claves:\n"
                      "- comprehension: {{score: (número 0-100), examples: (texto con ejemplos), feedback: (retroalimentación constructiva)}}\n"
                      "- authenticity: {{score: (número 0-100), examples: (texto con ejemplos), feedback: (retroalimentación constructiva)}}\n"
                      "- relational_skills: {{score: (número 0-100), examples: (texto con ejemplos), feedback: (retroalimentación constructiva)}}\n"
                      "- argumentation: {{score: (número 0-100), examples: (texto con ejemplos), feedback: (retroalimentación constructiva)}}\n"
                      "- bibliography_use: {{score: (número 0-100), examples: (texto con ejemplos), feedback: (retroalimentación constructiva)}}\n"
                      "- learning_objectives: [{{objective: (texto del objetivo), score: (número 0-100), examples: (texto con ejemplos), feedback: (retroalimentación constructiva)}}]\n"
                      "- overall_quality: {{score: (número 0-100), examples: (texto con ejemplos), feedback: (retroalimentación constructiva)}}\n"
                      "- plagiarism_detected: (booleano true/false)\n"
                      "- plagiarism_evidence: (texto explicando evidencia de plagio si se detectó)\n"
                      "- response_time_analysis: (texto analizando si los tiempos de respuesta son consistentes con el contenido)\n"
                      "- summary: (Un breve resumen de la evaluación)"
        }
        
        system_prompt_structured = {
            "English": "You are an AI assistant that structures evaluation data. Convert the following evaluation into a structured JSON format with the exact keys expected.",
            "Español": "Eres un asistente de IA que estructura datos de evaluación. Convierte la siguiente evaluación en un formato JSON estructurado con las claves exactas esperadas."
        }
        
        prompt_structured = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                system_prompt_structured.get(language, system_prompt_structured["Español"])
            ),
            HumanMessagePromptTemplate.from_template(
                prompt_structured_templates.get(language, prompt_structured_templates["Español"])
            )
        ])
        
        chain_structured = LLMChain(llm=self.llm, prompt=prompt_structured)
        structured_evaluation = chain_structured.run(evaluation=evaluation)
        
        # Try to parse the JSON from the response
        try:
            # Sometimes the response might include markdown code blocks, try to extract just the JSON
            json_text = structured_evaluation
            
            # If the response includes a code block with json, extract just the JSON
            if "```json" in structured_evaluation:
                json_blocks = structured_evaluation.split("```json")
                if len(json_blocks) > 1:
                    json_content = json_blocks[1].split("```")[0].strip()
                    json_text = json_content
            elif "```" in structured_evaluation:
                json_blocks = structured_evaluation.split("```")
                if len(json_blocks) > 1:
                    json_content = json_blocks[1].strip()
                    json_text = json_content
            
            structured_data = json.loads(json_text)
            
            # Ensure the required keys exist
            required_keys = ["comprehension", "authenticity", "relational_skills", "argumentation", 
                          "bibliography_use", "learning_objectives", "overall_quality", 
                          "plagiarism_detected", "plagiarism_evidence", "response_time_analysis", "summary"]
            
            for key in required_keys:
                if key not in structured_data:
                    if key in ["plagiarism_detected"]:
                        structured_data[key] = False
                    elif key in ["plagiarism_evidence", "response_time_analysis", "summary"]:
                        structured_data[key] = "No disponible"
                    else:
                        structured_data[key] = {"score": 50, "examples": "No disponible", "feedback": "No disponible"}
                    
            # Ensure each objective has required fields
            for obj in structured_data.get("learning_objectives", []):
                for field in ["objective", "score", "examples", "feedback"]:
                    if field not in obj:
                        obj[field] = "No disponible" if field != "score" else 50
                        
        except json.JSONDecodeError:
            # If parsing fails, create a simpler structure
            structured_data = {
                "raw_evaluation": evaluation,
                "comprehension": {"score": 50, "examples": "Error de formato de evaluación", "feedback": "Error de formato de evaluación"},
                "authenticity": {"score": 50, "examples": "Error de formato de evaluación", "feedback": "Error de formato de evaluación"},
                "relational_skills": {"score": 50, "examples": "Error de formato de evaluación", "feedback": "Error de formato de evaluación"},
                "argumentation": {"score": 50, "examples": "Error de formato de evaluación", "feedback": "Error de formato de evaluación"},
                "bibliography_use": {"score": 50, "examples": "Error de formato de evaluación", "feedback": "Error de formato de evaluación"},
                "learning_objectives": [{"objective": obj, "score": 50, "examples": "Error de formato de evaluación", "feedback": "Error de formato de evaluación"} for obj in learning_objectives],
                "overall_quality": {"score": 50, "examples": "Error de formato de evaluación", "feedback": "Error de formato de evaluación"},
                "plagiarism_detected": False,
                "plagiarism_evidence": "No se pudo evaluar el plagio debido a un error en el formato",
                "response_time_analysis": "No se pudo analizar los tiempos de respuesta debido a un error en el formato",
                "summary": "Hubo un error en el formato de los resultados de la evaluación."
            }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "raw_evaluation": evaluation,
            "structured_evaluation": structured_data,
            "assignment_id": os.path.basename(assignment_file_path),
            "learning_objectives": learning_objectives,
            "conversation_data": conversation_data
        }

class ReportGenerator:
    """Agent that generates a comprehensive report based on the evaluation"""
    
    def __init__(self, llm):
        self.llm = llm
        self.system_prompts = {
            "English": """You are an expert educational report generator.
            Your task is to create clear, comprehensive, and constructive reports based on student evaluations.
            Focus on providing actionable feedback that will help the student improve.""",
            
            "Español": """Eres un experto generador de informes educativos.
            Tu tarea es crear informes claros, completos y constructivos basados en evaluaciones de estudiantes.
            Concéntrate en proporcionar retroalimentación procesable que ayude al estudiante a mejorar.
            Incluye análisis detallado sobre la originalidad del trabajo, la evidencia de posible plagio, 
            y cómo los tiempos de respuesta se relacionan con la calidad y autenticidad del trabajo."""
        }
        
        self.prompt_templates = {
            "English": "Evaluation Data:\n{evaluation_json}\n\n"
                     "Generate a comprehensive educational assessment report with the following sections:\n"
                     "1. Executive Summary - Brief overview of strengths and areas for improvement\n"
                     "2. Assessment of Learning Objectives - Detailed evaluation for each objective\n"
                     "3. Comprehension Analysis - Evaluation of conceptual understanding\n"
                     "4. Authenticity Assessment - Evaluation of originality and personal engagement\n"
                     "5. Overall Quality - General assessment of the work\n"
                     "6. Recommendations - Specific, actionable suggestions for improvement\n\n"
                     "The report should be professional but encouraging. Use specific examples from the student's work and responses.",
                     
            "Español": "Datos de evaluación:\n{evaluation_json}\n\n"
                      "Genera un informe de evaluación educativa completo con las siguientes secciones:\n"
                      "1. Resumen ejecutivo - Breve descripción de fortalezas y áreas de mejora\n"
                      "2. Evaluación de objetivos de aprendizaje - Evaluación detallada para cada objetivo\n"
                      "3. Análisis de comprensión - Evaluación de la comprensión conceptual\n"
                      "4. Evaluación de autenticidad - Evaluación de originalidad y compromiso personal\n"
                      "5. Análisis de habilidades relacionales - Evaluación de cómo el estudiante conecta ideas\n"
                      "6. Evaluación de argumentación - Calidad de la estructura y fundamentación de argumentos\n"
                      "7. Uso de bibliografía - Evaluación de referencias y fuentes utilizadas\n"
                      "8. Análisis de tiempos de respuesta - Coherencia entre tiempo y calidad de respuestas\n"
                      "9. Detección de plagio - Hallazgos sobre posible contenido no original\n"
                      "10. Calidad general - Evaluación general del trabajo\n"
                      "11. Recomendaciones - Sugerencias específicas y procesables para mejorar\n\n"
                      "El informe debe ser profesional pero alentador. Usa ejemplos específicos del trabajo y las respuestas del estudiante."
        }
        
    def generate_report(self, evaluation_data):
        """Generate a comprehensive report from evaluation data"""
        # Determine language from conversation data
        language = evaluation_data.get("conversation_data", {}).get("language", "Español")
        
        system_prompt = self.system_prompts.get(language, self.system_prompts["Español"])
        prompt_template = self.prompt_templates.get(language, self.prompt_templates["Español"])
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template(prompt_template)
        ])
        
        evaluation_json = json.dumps(evaluation_data["structured_evaluation"], indent=2)
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        try:
            report = chain.run(evaluation_json=evaluation_json)
        except Exception as e:
            logging.error(f"Error generando el informe: {e}")
            report = "Error generando el informe."

        
        return {
            "text_report": report,
            "evaluation_data": evaluation_data,
            "timestamp": datetime.now().isoformat(),
            "language": language
        }

# Initialize session state variables if they don't exist
def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "learning_objectives" not in st.session_state:
        st.session_state.learning_objectives = [""]
    if "current_question_idx" not in st.session_state:
        st.session_state.current_question_idx = 0
    if "conversation_complete" not in st.session_state:
        st.session_state.conversation_complete = False
    if "evaluation_complete" not in st.session_state:
        st.session_state.evaluation_complete = False
    if "questions" not in st.session_state:
        st.session_state.questions = []
    if "student_responses" not in st.session_state:
        st.session_state.student_responses = {}

# Application interface
def run_app():
    setup_directories()
    init_session_state()
    
    # Set Spanish as the default language
    if "interface_language" not in st.session_state:
        st.session_state.interface_language = "Español"
    
    # Fix language to Spanish only
    language = "Español"
    
    st.title(get_text("app_title", language))
    
    # Sidebar for OpenAI API Key
    with st.sidebar:
        openai_api_key = st.text_input(get_text("api_key_label", language), type="password")
        if not openai_api_key:
            st.warning(get_text("api_key_warning", language))
        
        st.subheader(get_text("user_role_label", language))
        user_role = st.radio(
            get_text("user_role_label", language), 
            [get_text("teacher_role", language), get_text("student_role", language)]
        )
    
    if not openai_api_key:
        st.info(get_text("api_key_info", language))
        return
    
    # Initialize LLM
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo-16k",  # Using a model with larger context window
        temperature=0.2,
        openai_api_key=openai_api_key
    )
    
    # Teacher Interface
    if user_role == get_text("teacher_role", language):
        st.header(get_text("teacher_dashboard", language))
        
        tab1, tab2, tab3 = st.tabs([
            get_text("create_tab", language), 
            get_text("view_tab", language), 
            get_text("reports_tab", language)
        ])
        
        with tab1:
            st.subheader(get_text("create_new", language))
            
            # Assignment details
            assignment_name = st.text_input(get_text("assignment_name", language))
            assignment_instructions = st.text_area(get_text("assignment_instructions", language), height=200)
            
            # Number of questions
            num_questions = st.slider(
                get_text("questions_slider", language), 
                min_value=1, 
                max_value=5, 
                value=3, 
                help=get_text("questions_help", language)
            )
            
            # Language selection for assignment
            assignment_language_options = ["English", "Español"]
            assignment_language = st.selectbox(
                get_text("language", language), 
                options=assignment_language_options,
                index=1,  # Default to Spanish
                help="Seleccione el idioma para la interacción con estudiantes",
                key="assignment_language_select"
            )
            
            # Learning objectives
            st.subheader(get_text("learning_obj_title", language))
            st.write(get_text("learning_obj_desc", language))
            
            # Dynamic learning objectives
            for i, objective in enumerate(st.session_state.learning_objectives):
                col1, col2 = st.columns([6, 1])
                with col1:
                    st.session_state.learning_objectives[i] = st.text_input(
                        f"{get_text('objective_label', language)} {i+1}", value=objective, key=f"obj_{i}"
                    )
                with col2:
                    if i > 0:  # Don't allow removing the first objective
                        if st.button(get_text("remove_btn", language), key=f"rem_{i}"):
                            st.session_state.learning_objectives.pop(i)
                            st.rerun()
            
            if st.button(get_text("add_obj_btn", language)):
                st.session_state.learning_objectives.append("")
                st.rerun()
            
            # Upload assignment file (optional)
            uploaded_file = st.file_uploader(get_text("upload_label", language), type=["pdf", "docx", "txt"])
            
            if st.button(get_text("create_btn", language)):
                if not assignment_name or not assignment_instructions or not st.session_state.learning_objectives[0]:
                    st.error(get_text("fields_error", language))
                else:
                    # Create assignment data
                    assignment_id = f"{uuid.uuid4()}"
                    assignment_data = {
                        "id": assignment_id,
                        "name": assignment_name,
                        "instructions": assignment_instructions,
                        "learning_objectives": [obj for obj in st.session_state.learning_objectives if obj],
                        "created_at": datetime.now().isoformat(),
                        "file_path": None,
                        "num_questions": num_questions,
                        "language": assignment_language
                    }
                    
                    # Save uploaded file if provided
                    if uploaded_file:
                        file_path = save_uploaded_file(uploaded_file, "data/assignments")
                        assignment_data["file_path"] = file_path
                    
                    # Save assignment data
                    assignments_file = "data/assignments.json"
                    assignments = load_json(assignments_file)
                    assignments[assignment_id] = assignment_data
                    save_json(assignments, assignments_file)
                    
                    success_msg = get_text("created_success", language).format(name=assignment_name)
                    st.success(success_msg)
                    
                    # Reset form
                    st.session_state.learning_objectives = [""]
        
        with tab2:
            st.subheader(get_text("view_tab", language))
            
            assignments = load_json("data/assignments.json")
            if not assignments:
                st.info(get_text("no_assignments", language))
            else:
                assignment_select = st.selectbox(
                    get_text("select_assignment", language),
                    options=list(assignments.keys()),
                    format_func=lambda x: assignments[x]["name"],
                    key="view_assignments_select"
                )
                
                if assignment_select:
                    assignment = assignments[assignment_select]
                    
                    st.markdown(f"### {assignment['name']}")
                    
                    with st.expander(get_text("instructions_label", language), expanded=True):
                        st.write(assignment["instructions"])
                    
                    with st.expander(get_text("obj_label", language), expanded=True):
                        for i, obj in enumerate(assignment["learning_objectives"]):
                            st.write(f"{i+1}. {obj}")
                    
                    if assignment["file_path"]:
                        with st.expander(get_text("file_label", language), expanded=True):
                            st.write(f"{get_text('file_prefix', language)}{os.path.basename(assignment['file_path'])}")
                    
                    st.markdown(f"#### {get_text('id_label', language)}")
                    st.code(assignment["id"])
                    
                    st.markdown(f"#### {get_text('created_label', language)}")
                    st.write(assignment["created_at"])
                    
                    if st.button(get_text("delete_btn", language)):
                        del assignments[assignment_select]
                        save_json(assignments, "data/assignments.json")
                        st.success(get_text("deleted_success", language))
                        st.rerun()
        
        with tab3:
            st.subheader(get_text("view_evals_title", language))
            
            evaluations = load_json("data/evaluations.json") if os.path.exists("data/evaluations.json") else {}
            if not evaluations:
                st.info(get_text("no_evals", language))
            else:
                # Group evaluations by assignment
                evaluations_by_assignment = {}
                for eval_id, eval_data in evaluations.items():
                    assignment_id = eval_data["evaluation_data"]["assignment_id"]
                    if assignment_id not in evaluations_by_assignment:
                        evaluations_by_assignment[assignment_id] = []
                    evaluations_by_assignment[assignment_id].append((eval_id, eval_data))
                
                # Load assignments for names
                assignments = load_json("data/assignments.json")
                
                # Create a selectbox for assignments with evaluations
                assignment_options = list(evaluations_by_assignment.keys())
                assignment_names = [
                    assignments.get(a_id, {}).get("name", f"Unknown Assignment ({a_id})") 
                    for a_id in assignment_options
                ]
                
                assignment_select = st.selectbox(
                    get_text("select_assignment", language),
                    options=assignment_options,
                    format_func=lambda x: assignments.get(x, {}).get("name", f"Unknown Assignment ({x})"),
                    key="view_reports_assignment_select"
                )
                
                if assignment_select:
                    st.markdown(f"### {get_text('reports_for', language)}{assignments.get(assignment_select, {}).get('name', 'Unknown Assignment')}")
                    
                    # List evaluations for the selected assignment
                    evals_for_assignment = evaluations_by_assignment[assignment_select]
                    eval_options = [e[0] for e in evals_for_assignment]
                    eval_select = st.selectbox(
                        get_text("select_eval", language),
                        options=eval_options,
                        format_func=lambda x: f"{get_text('report_from', language)}{evaluations[x]['timestamp']}",
                        key="view_reports_eval_select"
                    )
                    
                    if eval_select:
                        report_data = evaluations[eval_select]
                        
                        with st.expander(get_text("eval_report_label", language), expanded=True):
                            st.markdown(report_data["text_report"])
                        
                        with st.expander(get_text("detailed_eval_label", language), expanded=False):
                            st.json(report_data["evaluation_data"])
    
    # Student Interface
    else:
        st.header(get_text("student_dashboard", language))
        
        tab1, tab2 = st.tabs([
            get_text("submit_tab", language), 
            get_text("evals_tab", language)
        ])
        
        with tab1:
            # If we're in the middle of a conversation, show the chat interface
            if "conversation_started" in st.session_state and st.session_state.conversation_started:
                st.subheader("Evaluation Conversation")
                
                # Display the conversation history
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.write(message["content"])
                
                # If the conversation is not complete, show the current question
                if not st.session_state.conversation_complete:
                    if st.session_state.current_question_idx < len(st.session_state.questions):
                        # Display the current question from the assistant
                        with st.chat_message("assistant"):
                            current_question = st.session_state.questions[st.session_state.current_question_idx]
                            st.write(current_question)
                            # Add to messages if it's not already there
                            if len(st.session_state.messages) == 0 or st.session_state.messages[-1]["content"] != current_question:
                                st.session_state.messages.append({"role": "assistant", "content": current_question})
                        
                        # Get user response with chat input
                        user_response = st.chat_input("Your response")
                        if user_response:
                            # Add user response to messages
                            st.session_state.messages.append({"role": "user", "content": user_response})
                            
                            # Save the response
                            st.session_state.student_responses[current_question] = user_response
                            
                            # Move to next question
                            st.session_state.current_question_idx += 1
                            
                            # Check if we've reached the end of questions
                            if st.session_state.current_question_idx >= len(st.session_state.questions):
                                st.session_state.conversation_complete = True
                                
                                # Add final message
                                st.session_state.messages.append({
                                    "role": "assistant", 
                                    "content": "Thank you for answering all the questions. I'll now analyze your responses."
                                })
                                
                                # Get conversation data for evaluation
                                conversation_history = []
                                for i, question in enumerate(st.session_state.questions):
                                    if question in st.session_state.student_responses:
                                        conversation_history.append({
                                            "question": question,
                                            "response": st.session_state.student_responses[question]
                                        })
                                
                                # Generate conversation summary
                                conversation_agent = ConversationAgent(llm)
                                conversation_agent.conversation_history = conversation_history
                                conversation_agent.student_responses = st.session_state.student_responses
                                conversation_data = conversation_agent.get_conversation_summary(
                                    language=st.session_state.current_assignment.get("language", "English")
                                )
                                
                                # Start evaluation
                                with st.spinner("Generating evaluation..."):
                                    # Get submission text
                                    submission_text = st.session_state.current_submission["text_submission"]
                                    if st.session_state.current_submission["file_path"]:
                                        try:
                                            file_content = read_file(st.session_state.current_submission["file_path"])
                                            submission_text += f"\n\n[Uploaded File Content]:\n{file_content}"
                                        except:
                                            submission_text += "\n\n[Uploaded File: Could not read content]"
                                    
                                    # Initialize evaluation agent
                                    evaluation_agent = EvaluationAgent(llm)
                                    evaluation_data = evaluation_agent.evaluate_submission(
                                        st.session_state.current_assignment["instructions"],
                                        st.session_state.current_assignment["id"],
                                        submission_text,
                                        st.session_state.current_assignment["learning_objectives"],
                                        conversation_data
                                    )
                                    
                                    # Generate report
                                    report_generator = ReportGenerator(llm)
                                    report_data = report_generator.generate_report(evaluation_data)
                                    
                                    # Save evaluation
                                    evaluation_id = f"{uuid.uuid4()}"
                                    evaluations_file = "data/evaluations.json"
                                    evaluations = load_json(evaluations_file)
                                    evaluations[evaluation_id] = report_data
                                    save_json(evaluations, evaluations_file)
                                    
                                    # Store for display
                                    st.session_state.evaluation_complete = True
                                    st.session_state.evaluation_id = evaluation_id
                                    st.session_state.evaluation_report = report_data
                            
                            # Rerun to update the UI
                            st.rerun()
                
                # Show evaluation results if complete
                if st.session_state.evaluation_complete:
                    st.success("Evaluation complete! Here's your assessment report:")
                    
                    with st.expander("Evaluation Report", expanded=True):
                        st.markdown(st.session_state.evaluation_report["text_report"])
                    
                    if st.button("Start a New Submission"):
                        # Reset all conversation and evaluation state
                        for key in ["conversation_started", "conversation_complete", 
                                   "evaluation_complete", "evaluation_id", "current_submission",
                                   "current_assignment", "messages", "questions", 
                                   "student_responses", "current_question_idx",
                                   "evaluation_report"]:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.rerun()
            
            # If not in a conversation, show the submission form
            else:
                st.subheader("Submit Assignment")
                
                # Load available assignments
                assignments = load_json("data/assignments.json")
                if not assignments:
                    st.info("No assignments available for submission.")
                else:
                    # Select assignment
                    assignment_select = st.selectbox(
                        "Select Assignment",
                        options=list(assignments.keys()),
                        format_func=lambda x: assignments[x]["name"]
                    )
                    
                    if assignment_select:
                        assignment = assignments[assignment_select]
                        
                        with st.expander("Assignment Details", expanded=True):
                            st.markdown(f"### {assignment['name']}")
                            
                            st.markdown("#### Instructions")
                            st.write(assignment["instructions"])
                            
                            st.markdown("#### Learning Objectives")
                            for i, obj in enumerate(assignment["learning_objectives"]):
                                st.write(f"{i+1}. {obj}")
                        
                        # Submission form
                        st.subheader("Your Submission")
                        
                        submission_text = st.text_area(
                            "Enter your assignment response here", 
                            height=300,
                            help="Write your response to the assignment here."
                        )
                        
                        uploaded_file = st.file_uploader(
                            "Upload Your Assignment (Optional)", 
                            type=["pdf", "docx", "txt"],
                            help="You can optionally upload a file with your assignment submission."
                        )
                        
                        if st.button("Submit Assignment"):
                            if not submission_text and not uploaded_file:
                                st.error("Please either write your submission or upload a file.")
                            else:
                                # Save submission
                                submission_id = f"{uuid.uuid4()}"
                                submission_data = {
                                    "id": submission_id,
                                    "assignment_id": assignment_select,
                                    "text_submission": submission_text,
                                    "file_path": None,
                                    "submitted_at": datetime.now().isoformat()
                                }
                                
                                # Save uploaded file if provided
                                if uploaded_file:
                                    file_path = save_uploaded_file(uploaded_file, "data/submissions")
                                    submission_data["file_path"] = file_path
                                
                                # Save submission data
                                submissions_file = "data/submissions.json"
                                submissions = load_json(submissions_file)
                                submissions[submission_id] = submission_data
                                save_json(submissions, submissions_file)
                                
                                # Initialize conversation
                                question_generator = QuestionGeneratorAgent(llm)
                                questions = question_generator.generate_questions(
                                    assignment["instructions"],
                                    assignment["learning_objectives"],
                                    num_questions=assignment.get("num_questions", 3),  # Default to 3 if not specified
                                    language=assignment.get("language", "English")  # Use the assignment's language
                                )
                                
                                # Store data in session state
                                st.session_state.current_submission = submission_data
                                st.session_state.current_assignment = assignment
                                st.session_state.conversation_started = True
                                st.session_state.conversation_complete = False
                                st.session_state.evaluation_complete = False
                                st.session_state.questions = questions
                                st.session_state.current_question_idx = 0
                                st.session_state.student_responses = {}
                                
                                # Initialize the first message based on language
                                language = assignment.get("language", "English")
                                intro_messages = {
                                    "English": "I'd like to ask you a few questions about your assignment to understand your thought process better.",
                                    "Español": "Me gustaría hacerte algunas preguntas sobre tu tarea para entender mejor tu proceso de pensamiento."
                                }
                                
                                intro_message = intro_messages.get(language, intro_messages["English"])
                                
                                st.session_state.messages = [
                                    {
                                        "role": "assistant", 
                                        "content": intro_message
                                    }
                                ]
                                
                                st.success("Assignment submitted successfully! Let's begin the evaluation conversation.")
                                st.rerun()
        
        with tab2:
            st.subheader("View Your Evaluations")
            
            # This would normally be filtered by student ID
            # For demo purposes, we'll show all evaluations
            evaluations = load_json("data/evaluations.json") if os.path.exists("data/evaluations.json") else {}
            
            if not evaluations:
                st.info("No evaluations available yet. Submit an assignment to get evaluated.")
            else:
                # Load assignments for names
                assignments = load_json("data/assignments.json")
                
                eval_options = list(evaluations.keys())
                eval_select = st.selectbox(
                    get_text("select_eval", language),
                    options=eval_options,
                    format_func=lambda x: (
                        f"{get_text('report_for', language)}{assignments.get(evaluations[x]['evaluation_data']['assignment_id'], {}).get('name', 'Unknown Assignment')} "
                        f"{get_text('report_from', language)}{evaluations[x]['timestamp']}"
                    ),
                    key="student_view_eval_select"
                )
                
                if eval_select:
                    report_data = evaluations[eval_select]
                    
                    assignment_id = report_data["evaluation_data"]["assignment_id"]
                    assignment_name = assignments.get(assignment_id, {}).get("name", "Unknown Assignment")
                    
                    st.markdown(f"## Evaluation Report for {assignment_name}")
                    
                    with st.expander("Report", expanded=True):
                        st.markdown(report_data["text_report"])
                    
                    with st.expander("Detailed Evaluation Data", expanded=False):
                        st.json(report_data["evaluation_data"])

if __name__ == "__main__":
    run_app()