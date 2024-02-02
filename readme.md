
# Calorie Tracker


## Feature Branches

- `main` - The main branch of the project
- `feature` - The feature branch in progress of integrating the streamlit app with the server
    - This branch is currently in progress and is not yet merged with the main branch. I have added authentication using flask and aiming to integrate the streamlit app with the server.
    - I have added the feature to add food items and their calories to the database. In progress of adding the feature to view the food items and their calories from the database.
    - New Template to be added are in progress. Namely; home.html and user_info.html

Welcome to the Calorie Tracker project! This project aims to help you keep track of your daily calorie intake. Set your calorie goals, track your daily intake with one capture of what you eat, and view your calorie history.

## Features

- Track your daily calorie intake
- Set calorie goals
- View your calorie history
- Generate reports and statistics

## Installation

1. Clone the repository: `git clone https://github.com/your-username/calorie-tracker.git`
2. Install the dependencies: `pip install -r requirements.txt`

## APIs

- This project uses Google Gemini Vision PRO API to detect food items in the images.
Click images on the go, gemini captures the food you eat and closely predict the amount of calories you have consumed. Furthur, you can follow up with your calorie tracker assistant if you have any queries or questions.
- You can sign up for a free account and get your API key [here](https://www.geminiapi.com/).

## Usage

1. Run the server: `python server.py`
2. Run the streamlit app: `streamlit run app.py`
    - (For now, feature branch in progress of integrating the streamlit app with the server) 
3. Open your web browser and navigate to `http://localhost:8501`
4. Start tracking your calories!

## Contributing

Contributions are welcome! If you'd like to contribute to this project, please follow these steps:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Make your changes and commit them: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a pull request

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

If you have any questions or suggestions, feel free to reach out to us at [dhruv.wappnet@gmail.com](mailto:dhruv.wappnet@gmail.com).
