# YouTube Get Transcription

A lightweight FastAPI service that extracts transcriptions (subtitles/closed captions) from YouTube videos. It utilizes `yt-dlp` to fetch video metadata and captions, processing them into a clean text format.

## Features

*   **Transcription Extraction**: Fetches subtitles from YouTube videos.
*   **Language Support**: Allows specifying the desired language (defaults to English).
*   **JSON Output**: Returns the video title, URL, and the full transcription text.
*   **FastAPI Powered**: Fast, easy-to-use API with automatic documentation.
*   **Dockerized**: Ready to deploy using Docker and Docker Compose.

## Prerequisites

*   **Docker** & **Docker Compose** (for containerized deployment)
*   **Python 3.11+** & **uv** (for local development)

## Installation & Running

### Option 1: Using Docker Compose (Recommended)

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd youtube-get-transcription
    ```

2.  **Start the service:**
    ```bash
    docker-compose up -d --build
    ```

    The API will be available at `http://localhost:18080`.

### Option 2: Running Locally with uv

1.  **Install `uv`** (if not already installed):
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2.  **Install dependencies:**
    ```bash
    uv sync
    ```

3.  **Run the application:**
    ```bash
    uv run fastapi run main.py --port 8000
    ```

    The API will be available at `http://localhost:8000`.

## API Usage

### Endpoint: `/transcribe`

**Method:** `GET`

**Parameters:**

| Parameter | Type   | Required | Description                                             | Default |
| :-------- | :----- | :------- | :------------------------------------------------------ | :------ |
| `url`     | string | Yes      | The full URL of the YouTube video.                      | N/A     |
| `lang`    | string | No       | The language code for the subtitles (e.g., "en", "vi"). | "en"    |

**Example Request:**

```bash
curl "http://localhost:18080/transcribe?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ&lang=en"
```

**Example Response:**

```json
{
  "title": "Rick Astley - Never Gonna Give You Up (Official Music Video)",
  "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "transcription": "We're no strangers to love You know the rules and so do I..."
}
```

## Project Structure

*   `main.py`: The main FastAPI application logic.
*   `Dockerfile`: Multi-stage Docker build configuration.
*   `docker-compose.yml`: Docker Compose configuration for local deployment.
*   `pyproject.toml`: Python project dependencies and configuration.

## Built With

*   [FastAPI](https://fastapi.tiangolo.com/)
*   [yt-dlp](https://github.com/yt-dlp/yt-dlp)
*   [uv](https://github.com/astral-sh/uv)
