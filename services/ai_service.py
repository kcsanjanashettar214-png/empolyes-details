# Services - Business logic for AI and security
from pathlib import Path
from typing import Dict, List, Optional
import csv
import re
from config import COMPANY_DATA
from services.ml_model import DATA_FILE
from services.dataset_generator import CompanyDatasetGenerator, EMPLOYEE_DATA_FILE
from services.chat_model import chat_model

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = DATA_FILE
company_dataset_generator = CompanyDatasetGenerator()

class AIService:
    """Mock AI service that processes queries"""

    dataset_rows: List[Dict] = None

    @classmethod
    def _load_dataset(cls, limit: int = 50) -> List[Dict]:
        if cls.dataset_rows is not None:
            return cls.dataset_rows

        rows: List[Dict] = []
        if DATA_PATH.exists() and DATA_PATH.name == 'data.csv':
            rows = cls._parse_flat_dataset(DATA_PATH, limit)
        elif DATA_PATH.exists():
            try:
                with open(DATA_PATH, 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        if not row:
                            continue
                        rows.append(row)
                        if len(rows) >= limit:
                            break
            except Exception:
                rows = []

        cls.dataset_rows = rows
        return rows

    @staticmethod
    def _parse_flat_dataset(filepath: Path, limit: int = 50) -> List[Dict]:
        text = filepath.read_text(encoding='utf-8')
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        timestamp_re = re.compile(r'^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$')
        start_index = next((idx for idx, line in enumerate(lines) if timestamp_re.match(line)), None)
        if start_index is None:
            return []

        records: List[Dict] = []
        field_order = [
            'timestamp', 'src_ip', 'dst_ip', 'src_port', 'dst_port',
            'protocol', 'bytes_sent', 'bytes_received', 'user_agent', 'url'
        ]
        i = start_index
        while i + len(field_order) <= len(lines) and len(records) < limit:
            chunk = lines[i:i + len(field_order)]
            if not timestamp_re.match(chunk[0]):
                i += 1
                continue
            record = dict(zip(field_order, chunk))
            record['src_port'] = int(re.sub(r'[^0-9]', '', str(record.get('src_port', '')))) if re.sub(r'[^0-9]', '', str(record.get('src_port', ''))) else record.get('src_port')
            record['dst_port'] = int(re.sub(r'[^0-9]', '', str(record.get('dst_port', '')))) if re.sub(r'[^0-9]', '', str(record.get('dst_port', ''))) else record.get('dst_port')
            record['bytes_sent'] = int(re.sub(r'[^0-9]', '', str(record.get('bytes_sent', '')))) if re.sub(r'[^0-9]', '', str(record.get('bytes_sent', ''))) else 0
            record['bytes_received'] = int(re.sub(r'[^0-9]', '', str(record.get('bytes_received', '')))) if re.sub(r'[^0-9]', '', str(record.get('bytes_received', ''))) else 0
            records.append(record)
            i += len(field_order)

        return records

    @staticmethod
    def _summarize_dataset(rows: List[Dict]) -> str:
        if not rows:
            return 'No dataset rows available.'

        suspicious_keywords = [
            'admin', 'phpmyadmin', '.env', 'backup', 'wp-login', 'shell', 'config', 'login', 'test.php', 'api/v1/users'
        ]
        suspicious = [
            row for row in rows
            if any(keyword in str(row.get('url', '')).lower() for keyword in suspicious_keywords)
            or int(row.get('dst_port', 0)) in {22, 23, 445, 1433, 3306, 3389}
        ]
        top = suspicious[0] if suspicious else rows[0]
        sample = (
            f"{top.get('timestamp')} {top.get('src_ip')} -> {top.get('dst_ip')} "
            f"proto={top.get('protocol')} dst_port={top.get('dst_port')}"
        )
        return (
            f"Dataset loaded from {DATA_PATH.name}. "
            f"Found {len(rows)} records and {len(suspicious)} suspicious events. "
            f"Example event: {sample}."
        )

    @staticmethod
    def _load_company_dataset(limit: Optional[int] = None) -> List[Dict]:
        rows: List[Dict] = []
        company_file = EMPLOYEE_DATA_FILE

        if company_file.exists():
            with open(company_file, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if not row:
                        continue
                    rows.append(row)
                    if limit is not None and len(rows) >= limit:
                        break
        return rows

    @staticmethod
    def _summarize_company_dataset(rows: List[Dict]) -> str:
        if not rows:
            return 'No company dataset rows available.'

        totals = len(rows)
        counts = {'admin': 0, 'manager': 0, 'employee': 0}
        departments = {}

        for row in rows:
            role_type = str(row.get('role_type', '')).lower()
            if role_type in counts:
                counts[role_type] += 1
            department = row.get('department', 'Unknown')
            departments[department] = departments.get(department, 0) + 1

        top_department = max(departments.items(), key=lambda item: item[1])[0] if departments else 'Unknown'
        sample = rows[0]

        return (
            f"Company dataset loaded with {totals} employees. "
            f"Admins: {counts['admin']}, Managers: {counts['manager']}, Employees: {counts['employee']}. "
            f"Top department: {top_department}. "
            f"Sample employee: {sample.get('name')} ({sample.get('role')}) in {sample.get('department')}.")

    @staticmethod
    def process_query(query: str, user_role: str, user_department: str = None) -> Dict:
        """
        Process user query and return mock AI response
        """
        query_lower = query.lower()

        greeting_keywords = [
            'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening',
            'greetings', 'what\'s up', 'how are you', 'nice to meet you'
        ]
        if any(keyword in query_lower for keyword in greeting_keywords):
            return {
                'response': chat_model.respond(query),
                'data_type': 'greeting',
                'sensitive': False
            }

        company_dataset_keywords = [
            'employee dataset', 'company dataset', 'employee data', 'company data',
            'employee list', 'company report', 'all employees'
        ]
        if any(keyword in query_lower for keyword in company_dataset_keywords):
            rows = AIService._load_company_dataset()
            summary = AIService._summarize_company_dataset(rows)
            return {
                'response': summary,
                'data_type': 'company_dataset',
                'sensitive': False
            }

        dataset_keywords = [
            'data.csv', 'network dataset', 'threat dataset', 'suspicious events',
            'network traffic', 'malicious events', 'dataset summary', 'csv summary',
            'sample events'
        ]
        if any(keyword in query_lower for keyword in dataset_keywords):
            rows = AIService._load_dataset(limit=50)
            summary = AIService._summarize_dataset(rows)
            return {
                'response': summary,
                'data_type': 'dataset',
                'sensitive': False
            }

        # Employee queries
        if "attendance" in query_lower or "my attendance" in query_lower:
            return {
                "response": "Your attendance record: 95% (38/40 days present)",
                "data_type": "personal",
                "sensitive": False
            }
        
        if "my salary" in query_lower:
            return {
                "response": "Your current salary information is confidential. Please contact HR.",
                "data_type": "salary",
                "sensitive": True
            }
        
        # Manager queries
        if "department performance" in query_lower or "my department" in query_lower:
            dept_data = COMPANY_DATA["departments"].get(user_department, {})
            response = f"Department: {user_department}\n"
            response += f"Performance: {dept_data.get('performance', 'N/A')}\n"
            response += f"Budget: ${dept_data.get('budget', 0)}\n"
            response += f"Head Count: {dept_data.get('head_count', 0)}"
            return {
                "response": response,
                "data_type": "department",
                "sensitive": False
            }
        
        if "team analytics" in query_lower or "team performance" in query_lower:
            return {
                "response": "Team Performance Report:\n- Sales: 92%\n- Efficiency: 88%\n- Customer Satisfaction: 94%",
                "data_type": "analytics",
                "sensitive": False
            }
        
        if "system logs" in query_lower or "audit logs" in query_lower:
            return {
                "response": "System audit logs retrieved (admin only)",
                "data_type": "system",
                "sensitive": True
            }
        
        # Default response
        return {
            "response": "Query processed successfully. No specific data matched.",
            "data_type": "general",
            "sensitive": False
        }
