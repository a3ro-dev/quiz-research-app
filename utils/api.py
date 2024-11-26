import requests
import html

class OpenDBAPI:
    BASE_URL = "https://opentdb.com/api.php"

    def __init__(self, amount=10, category=None, difficulty=None, question_type=None):
        self.amount = amount
        self.category = category
        self.difficulty = difficulty
        self.question_type = question_type

    def _build_params(self):
        params = {'amount': self.amount}
        if self.category:
            params['category'] = self.category
        if self.difficulty:
            params['difficulty'] = self.difficulty
        if self.question_type:
            params['type'] = self.question_type
        return params

    def fetch_questions(self):
        params = self._build_params()
        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Decode HTML entities in questions and answers
        for question in data['results']:
            question['question'] = html.unescape(question['question'])
            question['correct_answer'] = html.unescape(question['correct_answer'])
            question['incorrect_answers'] = [html.unescape(answer) for answer in question['incorrect_answers']]
        
        return data

# Example usage:
if __name__ == "__main__":
    total_questions = 50  # Adjust this number as needed
    api = OpenDBAPI(amount=total_questions, category=9, difficulty='easy', question_type='multiple')
    questions = api.fetch_questions()
    print(questions)