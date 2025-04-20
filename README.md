# RuneScape Tools Web Application

This web application provides various tools for RuneScape players, including profile viewing, highscores, timeline tracking, and player comparison.

## Features

- Player profile viewing
- Highscores lookup
- Timeline tracking for multiple players
- Player comparison tools
- And more!

## Running with Docker Compose

The easiest way to run this application is using Docker Compose:

```bash
# Clone the repository
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name

# Start the application
docker-compose up -d
```

The application will be available at http://localhost:5000

## Development

### Prerequisites

- Python 3.8+
- Docker and Docker Compose (for containerized deployment)

### Container Information

This project's container is automatically built and published to GitHub Container Registry using GitHub Actions. You can pull the latest image with:

```bash
docker pull ghcr.io/yourusername/your-repo-name:latest
```

### Manual Container Build

If you want to build the container manually:

```bash
docker build -t runescape-tools .
docker run -p 5000:5000 runescape-tools
```

## GitHub Actions

This repository uses GitHub Actions to automatically build and push the Docker image to GitHub Container Registry whenever changes are pushed to the main branch.

## License

[Your license information here]
