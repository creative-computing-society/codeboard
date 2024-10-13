# Codeboard

Codeboard is an open-source project under the CCS Coding Community an initiative by Creative Computing Society, TIET. It maintains a list of coders and scrapes their LeetCode profiles to rank them based on their performance.

## Project Structure

The project consists of two main folders:

- `server`: Contains the backend code using Django and Celery.
- `client`: Contains the frontend code built with React.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.x
- Node.js
- Django
- Celery
- Redis (for Celery backend)
- PostgreSQL (or any other preferred database)

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/creative-computing-society/codeboard.git
    ```

2. Set up the server:

    ```bash
    cd server
    python3 -m venv env
    source env/bin/activate
    pip install -r requirements.txt
    ```

3. Set up the client:

    ```bash
    cd ../client
    npm install
    npm start
    ```

4. Set up the database:

    Configure your database settings in `server/app/settings.py`.

5. Apply database migrations:

    ```bash
    cd ../server
    python manage.py migrate
    ```

6. Start the Django server:

    ```bash
    python manage.py runserver
    ```

## Usage

Visit the live application at [https://codeboard.ccstiet.com/](http://codeboard.ccstiet.com/) to see the list of coders and their ranks.

## Contributing

We welcome contributions from the community. Please read the [CONTRIBUTION.md](CONTRIBUTION.md) file for details on the code of conduct, and the process for submitting pull requests.

## Maintainers

- @ishan-xy
- @kaurmanjot20

## Moderators

- @akarsh911
- @saini128

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


