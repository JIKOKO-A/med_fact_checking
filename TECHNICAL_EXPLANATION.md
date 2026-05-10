# VerifyAI: Medical Fact-Checking System - Technical Explanation

This document provides a detailed overview of the VerifyAI platform, explaining its architecture, AI components, and how each part functions to ensure medical truth in social media content.

---

## 🏗️ System Architecture

The application is built using a **Modular Agentic Architecture**, where different specialized "agents" handle specific parts of the pipeline.

### 1. Frontend (The User Interface)
- **Tech Stack**: React, Next.js, Vanilla CSS.
- **Function**: Provides a premium, glassmorphic dashboard for users to submit video URLs or text claims. It handles real-time status updates and displays side-by-side transcriptions and translations.

### 2. Backend (The Orchestrator)
- **Tech Stack**: FastAPI (Python), PostgreSQL, Redis.
- **Function**: 
    - **API Layer**: Manages user requests and data storage.
    - **Task Queue**: Uses Redis to handle long-running video processing tasks.
    - **Service Orchestrator**: Coordinates between the Video Fetcher and the ML/NLP agents.

### 3. ML/NLP Pipeline (The Intelligence)
This is the core of the app, divided into several specialized layers:

#### A. Transcription Agent (Audio Processing)
- **Model**: **OpenAI Whisper** (Local Model).
- **Task**: Converts spoken Moroccan Darija/Arabic audio from videos into raw text.
- **Why?**: Whisper is state-of-the-art for multilingual speech recognition.

#### B. Translation Agent (Language Layer)
- **Model**: **Helsinki-NLP/opus-mt-ar-en** (Local Model).
- **Task**: Translates the Darija/Arabic transcription into English for global medical reviewers.
- **Why?**: It allows experts who might not speak Darija to verify the medical claims.

#### C. Darija Expert Agent (Quality Control)
- **Logic**: Rule-based linguistic refinement (Simulating an Expert).
- **Task**: Fixes common phonetic errors made by Whisper and ensures medical terminology is translated accurately. This is called the "5th Agent" in the system.

#### D. RAG Verifier (Fact-Checking)
- **Logic**: Retrieval-Augmented Generation.
- **Task**: Compares the extracted medical claims against a trusted knowledge base (Medical Journals, WHO guidelines, etc.).
- **Status**: Currently implemented as a high-performance placeholder (Mock) ready for full medical database integration.

---

## 🤖 AI & Models: APIs vs. Local Models

### Do we use APIs or our own models?
VerifyAI primarily uses **its own local models** (hosted within the system's infrastructure) rather than external APIs (like GPT-4 or Gemini) for the heavy lifting:
- **Transcription**: Local Whisper model.
- **Translation**: Local Transformer models.

**Advantages of Local Models:**
1. **Privacy**: Sensitive medical data never leaves your server.
2. **Speed**: No latency from external network requests.
3. **Cost**: No "per-token" or "per-minute" fees to Big Tech companies.

### Why didn't we do a "Training Phase"?
We utilized **Pre-trained Models** and **Transfer Learning**. 
- **Training from scratch**: Training a model like Whisper costs millions of dollars in compute and requires petabytes of data.
- **Inference/Fine-tuning**: We take these "super-intelligent" base models and use them for our specific task. We haven't needed a custom training phase yet because these open-source models already excel at Arabic/Darija when correctly prompted.

---

## ⏱️ Result "Currency" (Freshness)

The **Currency** (relevance/freshness) of the results depends on two factors:

1. **Linguistic Models**: (Whisper/Helsinki) These are trained on historic data up to their release date. However, since language doesn't change daily, they remain highly accurate.
2. **Verification Data**: In a production RAG setup, the "currency" is **Real-time**. The system is designed to fetch the latest medical news or search a live database of medical papers. This means a claim about a new virus (e.g., COVID-24) can be verified even if the model itself was trained years ago.

---

## 📁 File Structure Overview

- `/frontend`: User interface components and styling.
- `/backend`: API endpoints, database schemas, and service logic.
- `/ml_nlp`: The core AI pipelines (transcription, translation, and verification).
- `/devops`: Docker configuration for deploying the whole system.
- `docker-compose.yml`: Scripts to launch the entire environment with one command.
