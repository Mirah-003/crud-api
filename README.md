# Task API — Containerized Stack (A3)

A RESTful Task Management API built with FastAPI, PostgreSQL, and Docker Compose.

## Features
- Full CRUD operations (`GET`, `POST`, `PUT`, `DELETE`)
- PostgreSQL database persistence via Docker volume (`taskdata`)
- Health check & stats endpoints
- Orchestrated using Docker Compose

## Prerequisites
- Docker Engine & Docker Compose

## Quick Start (One Command)

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd crud-api