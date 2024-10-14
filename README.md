# Codeboard

**Codeboard** is an open-source project under the CCS Coding Community, an initiative by the Creative Computing Society, TIET. This project maintains a list of coders and ranks them based on their LeetCode performance by scraping their profiles.

## Project Structure

The project has two main directories:

- `server`: Contains backend code built with Django and Celery.
- `client`: Contains frontend code built with React.

## Getting Started

Follow these instructions to set up a local version of Codeboard for development and testing.

### Prerequisites

Ensure you have the following installed:

- Python 3.x
- Node.js
- Docker (required for the Django backend and to properly run Celery with Redis)
- Django
- Celery
- Redis (for Celery backend)
- PostgreSQL (or your preferred database)

### Server Setup

1. **Clone the backend repository:**
    ```bash
    git clone -b dev-backend https://github.com/creative-computing-society/codeboard.git codeboard-backend
    ```

2. **Set up a Python virtual environment:**
    ```bash
    cd codeboard-backend
    python3 -m venv .venv
    ```
    For Linux/MacOS:
    ```bash
    source .venv/bin/activate
    ```
    For Windows:
    ```bash
    .venv\Scripts\activate
    ```

3. **Install project dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Configure environment variables:**
   Create a `.env` file at the root of the backend project (`codeboard-backend/.env`) and include the following variables:
    ```plaintext
    SECRET_KEY=''  # Django secret key
    DB_NAME=''
    DB_USER=''
    DB_PASS=''
    DB_HOST=''
    DB_PORT=''
    CLIENT_SECRET=''  # CCS Auth Client Secret
    ```
   Create a database and update these variables with your database credentials.

5. **Apply database migrations:**
    ```bash
    python manage.py migrate
    ```

6. **Start the backend services:**
   Use Docker to start Redis, Celery, and the Django server:
    ```bash
    docker-compose up --build
    ```
   The server runs on port 4881 by default. You can change this in `docker-compose.yml` if necessary.

### Client Setup

1. **Clone the frontend repository:**
    ```bash
    git clone -b dev-frontend https://github.com/creative-computing-society/codeboard-frontend.git codeboard-frontend
    ```

2. **Install frontend dependencies:**
    ```bash
    cd codeboard-frontend
    npm install
    ```

3. **Set the server URL (for local development):**
   If you’re running the backend locally, navigate to `config.js` in the `src` directory and set `SERVER_URL`:
    ```javascript
    SERVER_URL = "http://127.0.0.1:4881/"
    ```

4. **Set the callback URL for authentication:**
   In `Login.js` under the `Components` folder, update the callback URL:
    ```plaintext
    http://localhost:3000/authVerify
    ```

5. **Start the frontend server:**
    ```bash
    npm start
    ```

After following these steps, the application should be running locally.

## Usage

Visit the live application at [https://codeboard.ccstiet.com/](https://codeboard.ccstiet.com/) to view coder rankings.

## Contributing

We welcome contributions! Please refer to our [CONTRIBUTION.md](CONTRIBUTION.md) for guidelines on contributing and submitting pull requests.

## Maintainers

- [@ishan-xy](https://github.com/ishan-xy)
- [@kaurmanjot20](https://github.com/kaurmanjot20)

## Moderators

- [@akarsh911](https://github.com/akarsh911)
- [@saini128](https://github.com/saini128)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
