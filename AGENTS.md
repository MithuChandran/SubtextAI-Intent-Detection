# Subtext AI Agents and Skills

This document outlines the AI capabilities and specialized skills available for the Subtext AI dissonance analyzer project.

## Overview

Subtext AI is a machine learning-powered system that analyzes WhatsApp chat logs to detect dissonance patterns in conversations. The system uses transformer-based models trained on labeled chat data to classify messages by dissonance levels.

## Core Capabilities

### 1. Chat Analysis
- **Purpose**: Analyze WhatsApp .txt exports for dissonance patterns
- **Input**: .txt files containing WhatsApp chat exports
- **Output**: Dissonance scores and classifications per message
- **Models**: Multiple architectures (baseline, weighted, dual-encoder, dissonance-mini)

### 2. Model Training
- **Purpose**: Train new transformer models on dissonance-labeled datasets
- **Frameworks**: Hugging Face Transformers, PyTorch
- **Metrics**: Accuracy, F1-score, precision/recall

### 3. Data Generation
- **Purpose**: Create synthetic chat data for testing and training
- **Formats**: Realistic WhatsApp-style conversations with emoji and timestamps
- **Augmentation**: Text variations, emoji additions, realistic sender patterns

### 4. Parsing and Preprocessing
- **Purpose**: Convert raw WhatsApp exports into structured data
- **Features**: Emoji extraction, timestamp parsing, sender identification
- **Output**: Pandas DataFrames with message metadata

## Antigravity Skills

The following skills are available in `.agent/skills/` for specialized AI assistance:

### chat-dissonance-analyzer
Analyzes uploaded chat files for dissonance patterns using trained ML models.

### model-trainer
Handles ML model training workflows and hyperparameter optimization.

### chat-data-generator
Creates synthetic chat data for testing and model training purposes.

### whatsapp-parser
Parses and preprocesses WhatsApp chat exports into structured format.

### model-inference
Runs inference on trained models for real-time dissonance classification.

## Usage

Skills are automatically loaded on-demand when relevant to user queries. Each skill includes detailed instructions, examples, and supporting scripts for comprehensive assistance with Subtext AI development and usage.

## Development

To extend or modify skills, edit the `SKILL.md` files in their respective directories. Skills follow the Antigravity framework with YAML frontmatter and markdown instructions.