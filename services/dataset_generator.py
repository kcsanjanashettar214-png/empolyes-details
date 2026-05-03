import csv
import random
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
EMPLOYEE_DATA_FILE = DATA_DIR / 'employee_data.csv'
GENERAL_CHAT_DATA_FILE = DATA_DIR / 'general_chat_data.csv'

DEPARTMENTS = [
    'Operations', 'Sales', 'IT', 'HR', 'Finance', 'Customer Success', 'Engineering', 'Marketing'
]

ROLE_TYPE_MAP = {
    'admin': ['IT Administrator', 'Security Admin', 'Infrastructure Admin', 'System Admin'],
    'manager': ['Sales Manager', 'Operations Manager', 'HR Manager', 'Finance Manager', 'Product Manager'],
    'employee': ['Engineer', 'Analyst', 'Coordinator', 'Support Specialist', 'Technician']
}

FIRST_NAMES = [
    'Alex', 'Jordan', 'Taylor', 'Morgan', 'Casey', 'Drew', 'Riley', 'Jamie', 'Robin', 'Avery',
    'Sam', 'Charlie', 'Kris', 'Skyler', 'Quinn', 'Reese', 'Dana', 'Andy', 'Cameron', 'Jesse'
]

LAST_NAMES = [
    'Patel', 'Lopez', 'Kim', 'Murphy', 'Singh', 'Bennett', 'Nguyen', 'Cooper', 'Reed', 'Brooks',
    'Bell', 'Watson', 'Price', 'Murphy', 'Jenkins', 'Rivera', 'Young', 'Clark', 'Lewis', 'Walker'
]

GREETING_TEMPLATES = [
    'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening',
    'how are you', 'nice to meet you', 'greetings', 'what\'s up',
    'hello there', 'hi there', 'hey there', 'good day', 'morning', 'afternoon', 'evening'
]

SMALLTALK_TEMPLATES = [
    'how is it going', 'how are you doing', 'how are things',
    'tell me something', 'what can you do', 'can you help', 'what is your name',
    'what do you know', 'are you there', 'can you assist me'
]

THANK_YOU_TEMPLATES = [
    'thank you', 'thanks', 'thanks a lot', 'thank you very much', 'appreciate it',
    'thanks for your help', 'thanks for that'
]

FOLLOW_UP_TEMPLATES = [
    'i need help with security', 'i need help with my department',
    'can you show me the employee list', 'what is the company status',
    'tell me about the company', 'show me the employee data',
    'what are the latest threats', 'what is the security status'
]

class CompanyDatasetGenerator:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not EMPLOYEE_DATA_FILE.exists():
            self.generate_employee_dataset(1000)

    def generate_employee_dataset(self, count: int = 1000):
        with open(EMPLOYEE_DATA_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'id', 'name', 'role_type', 'role', 'department',
                'manager', 'salary', 'attendance', 'email', 'hire_date'
            ])

            admin_count = max(10, count // 50)
            manager_count = max(80, count // 12)
            employee_count = count - admin_count - manager_count

            roles = []
            roles.extend([('admin', random.choice(ROLE_TYPE_MAP['admin'])) for _ in range(admin_count)])
            roles.extend([('manager', random.choice(ROLE_TYPE_MAP['manager'])) for _ in range(manager_count)])
            roles.extend([('employee', random.choice(ROLE_TYPE_MAP['employee'])) for _ in range(employee_count)])
            random.shuffle(roles)

            manager_names = []
            next_id = 1
            for role_type, role_text in roles:
                first = random.choice(FIRST_NAMES)
                last = random.choice(LAST_NAMES)
                name = f"{first} {last}"
                department = random.choice(DEPARTMENTS)
                salary = random.randint(50000, 180000) if role_type == 'employee' else random.randint(90000, 220000)
                attendance = f"{random.randint(85, 100)}%"
                email = f"{first.lower()}.{last.lower()}@examplecorp.com"
                hire_year = random.randint(2015, 2025)
                hire_month = random.randint(1, 12)
                hire_day = random.randint(1, 28)
                hire_date = f"{hire_year}-{hire_month:02d}-{hire_day:02d}"
                if role_type == 'admin':
                    manager = 'Executive Board'
                elif role_type == 'manager':
                    manager = 'Executive Board'
                    manager_names.append(name)
                else:
                    manager = random.choice(manager_names) if manager_names else 'Senior Manager'

                writer.writerow([
                    next_id,
                    name,
                    role_type,
                    role_text,
                    department,
                    manager,
                    salary,
                    attendance,
                    email,
                    hire_date
                ])
                next_id += 1

class GeneralChatModel:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not GENERAL_CHAT_DATA_FILE.exists():
            self._generate_general_chat_dataset(200)
        self.entries = self._load_dataset()

    def _generate_general_chat_dataset(self, count: int = 200):
        greetings = []
        suffixes = ['', ' please', '!', ' today', '?', ' for help', ' for assistance']
        base_phrases = GREETING_TEMPLATES + SMALLTALK_TEMPLATES + THANK_YOU_TEMPLATES + FOLLOW_UP_TEMPLATES

        while len(greetings) < count:
            base = random.choice(base_phrases)
            suffix = random.choice(suffixes)
            phrase = (base + suffix).strip()
            if phrase not in greetings:
                greetings.append(phrase)

        with open(GENERAL_CHAT_DATA_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['pattern', 'response', 'category'])
            for pattern in greetings:
                if any(pattern.startswith(token) for token in THANK_YOU_TEMPLATES):
                    response = 'You\'re welcome! Let me know if there\'s anything else I can help with.'
                    category = 'thanks'
                elif any(pattern.startswith(token) for token in FOLLOW_UP_TEMPLATES):
                    response = 'I can help with company data, security checks, or employee-related questions. What would you like to do next?'
                    category = 'follow_up'
                elif any(pattern.startswith(token) for token in SMALLTALK_TEMPLATES):
                    response = 'I\'m a secure assistant trained to help with company and security-related queries. How can I assist you?'
                    category = 'smalltalk'
                else:
                    response = 'Hello! I\'m here to help with your company, employee, and security questions.'
                    category = 'greeting'
                writer.writerow([pattern, response, category])

    def _load_dataset(self) -> List[Dict[str, str]]:
        rows: List[Dict[str, str]] = []
        with open(GENERAL_CHAT_DATA_FILE, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row:
                    rows.append(row)
        return rows

    def respond(self, prompt: str) -> str:
        normalized = prompt.lower().strip()
        best_match = None
        best_score = 0

        for entry in self.entries:
            pattern = entry['pattern'].lower()
            score = self._match_score(normalized, pattern)
            if score > best_score:
                best_score = score
                best_match = entry

        if best_match and best_score >= 0.35:
            return best_match['response']

        fallback = (
            'I\'m here to help with company information, employee data, or security questions. '
            'Please tell me more about what you need.'
        )
        return fallback

    @staticmethod
    def _match_score(prompt: str, pattern: str) -> float:
        prompt_tokens = set(prompt.split())
        pattern_tokens = set(pattern.split())
        if not prompt_tokens or not pattern_tokens:
            return 0.0
        common = prompt_tokens.intersection(pattern_tokens)
        return len(common) / max(len(pattern_tokens), 1)
