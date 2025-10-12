# Project Rebuild: AI & Data Processing Application

## 1. Project Overview

This project is a complete, from-scratch rebuild of a complex, multi-component AI and data processing application. The goal is to create a robust, scalable, and observable system that integrates a powerful local AI compute engine with an interactive desktop user interface.

The application is designed to handle agent-driven workflows, natural language command interpretation, and real-time data processing, with all components built according to strict architectural principles. The full development plan, including a detailed milestone breakdown, is maintained in parallel project documentation.

## 2. Guiding Principles & Core Architecture

All development must strictly adhere to the following foundational principles:

1.  **Strict Four-Layer Architecture:** Respects the separation of concerns (UI → Backend → Profiles/Logic → Database/Compute).
2.  **Observable Spine is Non-Negotiable:** `trace_id` propagation must be implemented from the very beginning.
3.  **Database as the Single Source of Truth:** All state will be persisted to and fetched from PostgreSQL.
4.  **Build for Integration:** Components are not "done" until connected to the larger system via the FastAPI backend.
5.  **Contract-Driven Design:** Boundaries between components must be validated by strict schemas (SQLAlchemy, Pydantic).

## 3. Core Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy
- **Database:** PostgreSQL with PostGIS/vector extension, managed with Alembic
- **Frontend:** Tauri (Desktop App Shell), Svelte (UI Framework)
- **AI / Compute Engine:** `llama-cpp-python`, PyTorch
- **GPU Acceleration:** AMD ROCm on WSL Ubuntu
- **Environment Management:** Docker
- **Data Fetching:** Selenium

## 4. Getting Started

This project is structured as a **monorepo**. All code, including distinct applications and services, will reside in this single Git repository.

Environment and dependency management is handled via **Docker**. Each independent service (e.g., the FastAPI server, the TTS application) will have its own `Dockerfile` to ensure a reproducible and isolated environment. Detailed setup instructions will be located in the directory for each respective service.