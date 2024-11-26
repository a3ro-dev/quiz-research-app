# Quiz Research App

This is a Streamlit web application designed for users to research quiz questions. Users can fetch quiz questions from the Open Trivia Database (OpenDB) API, review them, and categorize them as accepted or rejected. The app also maintains a history of accepted and rejected questions for each user.

## Features

- Fetch quiz questions from the OpenDB API with customizable parameters.
- Review questions in a slideshow format with navigation controls.
- Accept or reject questions and save the history.
- View history of accepted and rejected questions.
- User authentication with username.
- Dark mode and clean, responsive design.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/a3ro-dev/quiz-research-app.git
    cd quiz-research-app
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv .venv
    .venv\Scripts\activate  # On Windows
    # source .venv/bin/activate  # On macOS/Linux
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

4. Run the Streamlit app:
    ```bash
    streamlit run app.py
    ```

## Usage

1. Open the app in your web browser.
2. Enter your username in the sidebar.
3. Select the quiz parameters (category, difficulty, type, number of questions) and click "Fetch Questions".
4. Review the questions in the main area. Use the navigation buttons to move between questions.
5. Accept or reject questions using the provided buttons.
6. View your history of accepted and rejected questions in the sidebar.

## Database

The app uses an SQLite database to store user information and question history. The database schema includes tables for users and question history.

## API

The app fetches quiz questions from the Open Trivia Database (OpenDB) API. The `OpenDBAPI` class in `utils/api.py` handles the API requests.

## Customization

You can customize the app by modifying the following files:

- `app.py`: Main Streamlit app file.
- `utils/api.py`: API wrapper for the OpenDB API.
- `utils/db.py`: Database management.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License.

## Acknowledgements

- Made with ❤️ by [a3ro-dev](https://github.com/a3ro-dev)
- Powered by [Streamlit](https://streamlit.io/)
- Quiz questions provided by [Open Trivia Database](https://opentdb.com/)
