import csv
import json
import math
import os
import random
import re
from pathlib import Path
from typing import Dict, List, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
MODEL_DIR = BASE_DIR / 'models'
DATA_FILE = DATA_DIR / 'demo_threat_data.csv'
MODEL_FILE = MODEL_DIR / 'threat_model.json'

FEATURE_COLUMNS = [
    'protocol_tcp',
    'protocol_udp',
    'protocol_icmp',
    'dst_port_risk',
    'src_port_risk',
    'url_suspicious',
    'agent_suspicious',
    'bytes_sent_high',
    'bytes_received_high'
]

SUSPICIOUS_URL_KEYWORDS = [
    'phpmyadmin', 'admin', 'login', 'shell', 'config', 'backup', '.env', 'wp-login', 'test.php', '/api/v1/users', 'dashboard?id='
]
SUSPICIOUS_AGENT_KEYWORDS = ['curl', 'sqlmap', 'python-urllib', 'scanner', 'bot', 'masscan', 'nmap']
HIGH_RISK_PORTS = {22, 23, 445, 1433, 3306, 3389, 8080, 8443}


class ThreatModel:
    def __init__(self):
        self.weights = [0.0] * len(FEATURE_COLUMNS)
        self.bias = 0.0
        self.threshold = 0.5
        self.sample_events = []
        self._prepare_environment()
        self._load_or_train()

    def _prepare_environment(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        MODEL_DIR.mkdir(parents=True, exist_ok=True)

    def _load_or_train(self):
        if not DATA_FILE.exists() or self._dataset_size() < 1000:
            self._generate_demo_dataset(1000)
        if MODEL_FILE.exists():
            self._load_model()
        else:
            X, y = self._load_dataset(populate_samples=False)
            self._train(X, y)
            self._save_model()
            self._load_dataset(populate_samples=True)

    def _dataset_size(self) -> int:
        if not DATA_FILE.exists():
            return 0
        with open(DATA_FILE, 'r', encoding='utf-8') as csvfile:
            return sum(1 for _ in csvfile) - 1

    def _generate_demo_dataset(self, count: int):
        urls_benign = [
            'https://portal.example.org/dashboard',
            'https://app.company.in/status',
            'https://intranet.local/home',
            'https://webmail.corp/inbox',
            'https://portal.example.org/api/v1/status',
            'https://app.company.in/assets/logo.png'
        ]
        urls_malicious = [
            'https://webmail.corp/phpmyadmin?id=123',
            'https://internal.bank.local/admin?id=567',
            'https://portal.example.org/.env?id=303',
            'https://api.service.io/backup.sql?id=369',
            'https://app.company.in/wp-login.php?id=492',
            'https://webmail.corp/shell?id=369'
        ]
        agents_benign = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 Safari/605.1.15'
        ]
        agents_malicious = [
            'curl/8.4.0',
            'python-urllib/3.9',
            'sqlmap/1.5',
            'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            'masscan/1.3.0'
        ]

        with open(DATA_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'timestamp', 'src_ip', 'dst_ip', 'src_port', 'dst_port',
                'protocol', 'bytes_sent', 'bytes_received', 'user_agent', 'url', 'label'
            ])

            for i in range(count):
                timestamp = f"2025-10-{random.randint(1,30):02d} {random.randint(0,23):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}"
                src_ip = f"{random.randint(10,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
                dst_ip = f"{random.randint(10,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
                protocol = random.choices(['TCP', 'UDP', 'ICMP'], weights=[70, 20, 10])[0]
                if i % 3 == 0:
                    url = random.choice(urls_malicious)
                    agent = random.choice(agents_malicious)
                    dst_port = random.choice(list(HIGH_RISK_PORTS))
                    bytes_sent = random.randint(20000, 1400000)
                    bytes_received = random.randint(20000, 2200000)
                    label = 'malicious'
                else:
                    url = random.choice(urls_benign)
                    agent = random.choice(agents_benign)
                    dst_port = random.choice([80, 443, 25, 53, 8080, 5900])
                    bytes_sent = random.randint(200, 120000)
                    bytes_received = random.randint(100, 500000)
                    label = 'benign'
                src_port = random.randint(1024, 65535)
                writer.writerow([
                    timestamp, src_ip, dst_ip, src_port, dst_port,
                    protocol, bytes_sent, bytes_received, agent, url, label
                ])

    def _load_dataset(self, populate_samples: bool = True) -> Tuple[List[List[float]], List[int]]:
        X = []
        y = []
        self.sample_events = []
        with open(DATA_FILE, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                features = self._vectorize(row)
                X.append(features)
                y.append(1 if row['label'] == 'malicious' else 0)
                if populate_samples:
                    self.sample_events.append({
                        'timestamp': row['timestamp'],
                        'src_ip': row['src_ip'],
                        'dst_ip': row['dst_ip'],
                        'dst_port': int(row['dst_port']),
                        'protocol': row['protocol'],
                        'user_agent': row['user_agent'],
                        'url': row['url'],
                        'predicted_label': 'MALICIOUS' if self._sigmoid(sum(features[i] * self.weights[i] for i in range(len(features))) + self.bias) >= self.threshold else 'BENIGN'
                    })
        return X, y

    def _save_model(self):
        with open(MODEL_FILE, 'w', encoding='utf-8') as model_file:
            json.dump({
                'weights': self.weights,
                'bias': self.bias,
                'threshold': self.threshold
            }, model_file, indent=2)

    def _load_model(self):
        with open(MODEL_FILE, 'r', encoding='utf-8') as model_file:
            data = json.load(model_file)
            self.weights = data['weights']
            self.bias = data['bias']
            self.threshold = data.get('threshold', 0.5)
        self._load_dataset()  # populate sample_events list

    def _vectorize(self, row: Dict[str, str]) -> List[float]:
        protocol = row['protocol'].upper()
        protocol_tcp = 1.0 if protocol == 'TCP' else 0.0
        protocol_udp = 1.0 if protocol == 'UDP' else 0.0
        protocol_icmp = 1.0 if protocol == 'ICMP' else 0.0
        dst_port_risk = 1.0 if int(row['dst_port']) in HIGH_RISK_PORTS else 0.0
        src_port_risk = 1.0 if int(row['src_port']) in HIGH_RISK_PORTS else 0.0
        url_suspicious = 1.0 if any(keyword in row['url'].lower() for keyword in SUSPICIOUS_URL_KEYWORDS) else 0.0
        agent_suspicious = 1.0 if any(keyword in row['user_agent'].lower() for keyword in SUSPICIOUS_AGENT_KEYWORDS) else 0.0
        bytes_sent_high = 1.0 if int(row['bytes_sent']) > 100000 else 0.0
        bytes_received_high = 1.0 if int(row['bytes_received']) > 200000 else 0.0
        return [
            protocol_tcp,
            protocol_udp,
            protocol_icmp,
            dst_port_risk,
            src_port_risk,
            url_suspicious,
            agent_suspicious,
            bytes_sent_high,
            bytes_received_high
        ]

    def _sigmoid(self, z: float) -> float:
        return 1.0 / (1.0 + math.exp(-max(min(z, 20), -20)))

    def _train(self, X: List[List[float]], y: List[int], epochs: int = 600, lr: float = 0.1):
        n_samples = len(X)
        self.weights = [0.0] * len(FEATURE_COLUMNS)
        self.bias = 0.0

        for _ in range(epochs):
            grad_w = [0.0] * len(self.weights)
            grad_b = 0.0
            for xi, yi in zip(X, y):
                z = sum(self.weights[i] * xi[i] for i in range(len(self.weights))) + self.bias
                pred = self._sigmoid(z)
                error = pred - yi
                for i in range(len(self.weights)):
                    grad_w[i] += error * xi[i]
                grad_b += error
            for i in range(len(self.weights)):
                self.weights[i] -= lr * grad_w[i] / n_samples
            self.bias -= lr * grad_b / n_samples

    def predict_event(self, event: Dict) -> Dict:
        features = self._vectorize(event)
        score = self._sigmoid(sum(self.weights[i] * features[i] for i in range(len(self.weights))) + self.bias)
        label = 'MALICIOUS' if score >= self.threshold else 'BENIGN'
        return {
            'score': round(score, 3),
            'classification': label,
            'threshold': self.threshold,
            'features': dict(zip(FEATURE_COLUMNS, features))
        }

    def predict_from_text(self, text: str) -> Dict:
        # Check for URLs first
        url_match = re.search(r'https?://[^\s\'\"]+', text)
        if url_match:
            url = url_match.group(0)
            event = {
                'protocol': 'TCP',
                'src_port': 40000,
                'dst_port': 443,
                'url': url,
                'user_agent': 'unknown',
                'bytes_sent': 1024,
                'bytes_received': 1024
            }
            result = self.predict_event(event)
            result['url'] = url
            return result

        # Analyze text content for malicious patterns
        text_lower = text.lower()
        # Only high-confidence malicious patterns (full phrases)
        malicious_patterns = [
            'ignore security', 'sql injection', 'select * from', 'password hack',
            'admin access', 'jailbreak', 'drop table', 'sudo', 'disable security',
            'show all data', 'developer mode', 'bypass security', 'override security',
            'reveal secrets', 'system command', 'execute code', 'shell access',
            'delete database', 'alter table', 'union select', 'script injection',
            'cross site', 'xss attack', 'remote code', 'buffer overflow',
            'privilege escalation', 'root access', 'backdoor', 'exploit code',
            'malware', 'virus', 'trojan', 'ransomware', 'phishing', 'ignore all',
            'bypass all', 'hack the', 'crack the', 'break into', 'steal data'
        ]

        # Only strong suspicious patterns that are dangerous in context
        suspicious_patterns = [
            'drop table', 'delete from', 'exec ', 'execute ', 'chmod 777',
            'rm -rf', 'shell>', 'bash -c', 'sudo su', 'root password',
            '&& ', '; ', '| cat', '| grep', 'password123'
        ]

        malicious_score = 0
        for pattern in malicious_patterns:
            if pattern in text_lower:
                malicious_score += 0.4

        for pattern in suspicious_patterns:
            if pattern in text_lower:
                malicious_score += 0.2

        # Length-based scoring (very long prompts might be suspicious)
        if len(text) > 500:
            malicious_score += 0.1
        elif len(text) > 1000:
            malicious_score += 0.2

        # Special character density
        special_chars = sum(1 for c in text if not c.isalnum() and not c.isspace())
        special_ratio = special_chars / len(text) if len(text) > 0 else 0
        if special_ratio > 0.3:
            malicious_score += 0.1

        classification = 'MALICIOUS' if malicious_score >= 0.4 else 'SUSPICIOUS' if malicious_score >= 0.2 else 'BENIGN'

        return {
            'score': min(1.0, malicious_score),
            'classification': classification,
            'threshold': self.threshold,
            'features': {
                'malicious_patterns_found': malicious_score,
                'text_length': len(text),
                'special_char_ratio': special_ratio
            },
            'url': None
        }

    def _mock_user_ip(self, user_role: str) -> str:
        mapping = {
            'admin': '192.168.10.10',
            'manager': '172.16.5.14',
            'employee': '10.0.12.24'
        }
        return mapping.get(user_role, '10.0.0.10')

    def _lookup_location(self, ip: str) -> str:
        if ip.startswith('192.168.'):
            return 'Corporate HQ Network'
        if ip.startswith('172.16.'):
            return 'Regional Office'
        if ip.startswith('10.'):
            return 'Remote Employee VPN'
        return 'Unknown Network'

    def _lookup_network_address(self, ip: str) -> str:
        if ip.startswith('192.168.'):
            return '192.168.10.0/24'
        if ip.startswith('172.16.'):
            return '172.16.0.0/16'
        if ip.startswith('10.'):
            return '10.0.0.0/8'
        return 'Unknown CIDR'

    def _mock_device_profile(self, user_role: str) -> Dict[str, str]:
        profiles = {
            'admin': {
                'browser': 'Chrome 124 on Windows 11',
                'device': 'Corporate Workstation',
                'address': 'Corporate HQ, Data Center Floor 3'
            },
            'manager': {
                'browser': 'Safari 18 on macOS Ventura',
                'device': 'Executive Laptop',
                'address': 'Regional Office, Suite 5'
            },
            'employee': {
                'browser': 'Edge 121 on Windows 10',
                'device': 'Employee Workstation',
                'address': 'Remote VPN Endpoint'
            }
        }
        return profiles.get(user_role, {
            'browser': 'Unknown Browser',
            'device': 'Unknown Device',
            'address': 'Unknown Location'
        })

    def analyze_prompt(self, prompt: str, user_role: str) -> Dict:
        prompt_lower = prompt.lower()
        ml_result = self.predict_from_text(prompt)
        dummy_patterns = [
            'ignore security', 'sql injection', 'select * from', 'password',
            'admin access', 'jailbreak', 'drop table', 'sudo', 'disable security',
            'show all data', 'developer mode', 'bypass security'
        ]
        is_dummy = any(pattern in prompt_lower for pattern in dummy_patterns)

        # Calculate trust score based on ML result and dummy patterns
        base_score = (1.0 - ml_result['score']) * 100
        trust_score = base_score - (25.0 if is_dummy else 0.0)

        # Boost trust score for safe, normal queries
        safe_patterns = [
            'hello', 'hi', 'good morning', 'good afternoon', 'thank you',
            'show my attendance', 'what is my', 'tell me about', 'can you',
            'please show', 'i need help', 'department', 'team', 'analytics'
        ]
        if any(pattern in prompt_lower for pattern in safe_patterns):
            trust_score += 15.0

        trust_score = round(max(0.0, min(100.0, trust_score)), 1)

        real_or_dummy = 'DUMMY' if is_dummy else 'REAL'
        src_ip = self._mock_user_ip(user_role)
        location = self._lookup_location(src_ip)
        network_address = self._lookup_network_address(src_ip)
        device_profile = self._mock_device_profile(user_role)

        fake_probability = round(min(100.0, max(5.0, (100.0 - trust_score) + (15.0 if is_dummy else 0.0))), 1)
        is_fake = fake_probability >= 50.0

        return {
            'classification': ml_result['classification'],
            'ml_score': ml_result['score'],
            'threshold': ml_result.get('threshold', self.threshold),
            'trust_score': trust_score,
            'real_or_dummy': real_or_dummy,
            'src_ip': src_ip,
            'ip_address': src_ip,
            'network_address': network_address,
            'location': location,
            'address': device_profile['address'],
            'browser': device_profile['browser'],
            'device': device_profile['device'],
            'fake_probability': fake_probability,
            'is_fake': is_fake,
            'user_type': user_role,
            'is_threat': ml_result['classification'] == 'MALICIOUS',
            'url': ml_result.get('url'),
            'features': ml_result.get('features', {})
        }

    def get_sample_events(self, limit: int = 10) -> List[Dict]:
        return self.sample_events[-limit:]

    def get_model_info(self) -> Dict:
        return {
            'feature_columns': FEATURE_COLUMNS,
            'weights': self.weights,
            'bias': self.bias,
            'threshold': self.threshold,
            'training_rows': len(self.sample_events)
        }

threat_model = ThreatModel()
