# AdForge AI: Autonomous Product Commercial Generation

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Microservices-009688.svg)
![ComfyUI](https://img.shields.io/badge/ComfyUI-Cloud_GPU-red.svg)
![AnimateDiff](https://img.shields.io/badge/AnimateDiff-Video_Diffusion-purple.svg)
![Edge-TTS](https://img.shields.io/badge/Edge--TTS-Audio-yellow.svg)

## Overview
AdForge AI is an end-to-end autonomous agentic pipeline designed to instantly generate fully rendered video commercials from a single product URL. 

By orchestrating a multi-stage microservice architecture, the system autonomously handles product data extraction, creative storyboard synthesis, and high-fidelity video diffusion. It is built to minimize human intervention while maximizing output coherence, leveraging cloud GPUs for rapid video synthesis.

## System Architecture & Pipeline

The system is decoupled into independent microservices communicating via FastAPI, allowing for parallel asset generation and modular replacement of specific AI nodes:

1. **Ingestion & Scraping:** Extracts raw product metadata, features, and target audience data directly from a provided e-commerce URL.
2. **LLM Storyboard Synthesis:** An LLM agent processes the scraped data to generate a frame-by-frame storyboard, complete with diffusion prompts and a synchronized voiceover script.
3. **Video Diffusion Engine (ComfyUI + AnimateDiff):** The core synthesis engine. The prompts are queued to a cloud GPU instance running ComfyUI and AnimateDiff to generate smooth, temporally consistent B-roll footage.
4. **Audio Synthesis (Edge-TTS):** Concurrently generates natural-sounding voiceovers based on the LLM script.
5. **Assembly & Post-Processing (MoviePy):** Automatically stitches the diffused video clips, overlays the audio track, and applies final transitions.

## Tech Stack
* **Orchestration & Backend:** Python, FastAPI
* **Generative Video/Image:** ComfyUI, AnimateDiff
* **Audio & Video Processing:** Edge-TTS, MoviePy
* **Data Ingestion:** `[Mention your scraping library, e.g., BeautifulSoup / Selenium]`
