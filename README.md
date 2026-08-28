# 🤖 AI-Powered CRM Assistant

An AI-powered CRM chatbot that allows sales teams to interact with customer and deal information using **natural language**.

## 📌 Overview

The AI CRM Assistant helps users access CRM information without manually searching through customer or deal records.

Users can simply ask questions such as:

> "What deal does John Smith have?"

The AI understands the user's request, selects the appropriate CRM operation, retrieves the required information, and provides a natural-language response.

## 🚀 Key Features

1. **Customer Search** – Find customer information using natural language.
2. **Deal Information** – Retrieve customer deal details and status.
3. **Customer History** – View customer interactions and history.
4. **Lead Status Analysis** – Check and understand lead status.
5. **At-Risk Deal Identification** – Identify deals that may require attention.
6. **Deal Status Updates** – Update deal information through the assistant.
7. **Customer Notes** – Add and manage customer notes.
8. **Natural-Language Interaction** – Communicate with CRM data using simple questions.

## 🏗️ Architecture

```text
User
  ↓
CRM Chatbot
  ↓
FastAPI
  ↓
Gemini AI Agent
  ↓
CRM Tools
  ↓
CRM Data
  ↓
Natural-Language Response
```

## 🛠️ Tech Stack

1. **Python** – Backend development
2. **FastAPI** – API and backend services
3. **Gemini AI** – AI agent and natural-language understanding
4. **CRM Tools** – Customer and deal operations
5. **CRM Data** – Customer, lead, deal, and interaction information

## ▶️ How It Works

1. The user sends a question through the CRM chatbot.
2. The request is received by the FastAPI backend.
3. The Gemini AI agent understands the user's intent.
4. The agent selects the required CRM tool.
5. The tool retrieves or updates the required CRM data.
6. The result is returned to the user in a clear natural-language response.

## 🎯 Project Objective

The main objective of this project is to simplify CRM operations by allowing sales teams to **search, analyze, and manage CRM information through an AI-powered conversational interface**.

## 📌 Example

**User:**

> "Show me John's current deal status."

**Assistant:**

> "John Smith's current deal is in the Negotiation stage."
