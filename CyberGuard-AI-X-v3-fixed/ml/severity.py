"""
CyberGuard AI X - Severity Analysis Engine
Detects complaint severity based on keyword patterns
"""

import re

# Severity keyword rules
SEVERITY_RULES = {
    'High': {
        'keywords': [
            # Financial
            'stolen', 'theft', 'lost money', 'large amount', 'lakhs', 'crores', 'millions',
            'bank account emptied', 'funds transferred', 'unauthorized transfer',
            # Threats
            'threat', 'blackmail', 'extortion', 'ransom', 'kidnap', 'violence', 'death threat',
            'bomb threat', 'sexual threat', 'nude photos', 'revenge porn',
            # Breaches
            'data breach', 'hacked account', 'account taken over', 'account hijacked',
            'identity stolen', 'credentials stolen', 'complete access', 'root access',
            # Critical malware
            'ransomware', 'critical system', 'infrastructure', 'hospital', 'government system',
        ],
        'patterns': [
            r'\b(\d+)\s*(lakh|crore|million|billion)\b',  # Large money amounts
            r'\bthreat(en(ed|ing)?)?s?\b',
            r'\bblackmail\b',
            r'\bransom(ware)?\b',
        ],
        'weight': 3
    },
    'Medium': {
        'keywords': [
            'suspicious', 'unauthorized access', 'attempted hack', 'phishing email',
            'fake website', 'suspicious link', 'unknown login', 'password changed',
            'account compromised', 'strange activity', 'unusual transaction',
            'small amount', 'minor loss', 'scam attempt', 'fraud attempt',
            'fake call', 'impersonation', 'fake profile', 'harassment',
        ],
        'patterns': [
            r'\bunauthorized\b',
            r'\battempt(ed)?\b',
            r'\bsuspicious\b',
            r'\bcompromised\b',
        ],
        'weight': 2
    },
    'Low': {
        'keywords': [
            'spam', 'junk email', 'unwanted messages', 'minor issue', 'annoying',
            'fake friend request', 'trolling', 'offensive comment', 'rude message',
            'fake news', 'misinformation', 'copyright', 'minor harassment',
        ],
        'patterns': [
            r'\bspam\b',
            r'\bjunk\b',
            r'\bminor\b',
        ],
        'weight': 1
    }
}

DEPARTMENT_MAP = {
    'Phishing': 'Banking Cyber Cell',
    'Financial Fraud': 'Financial Crime Unit',
    'Hacking': 'Cyber Investigation Unit',
    'Malware': 'Digital Forensics Team',
    'Cyberbullying': 'Social Media Monitoring Cell',
    'Online Fraud': 'Economic Offences Wing',
    'Identity Theft': 'Identity Crime Unit',
}


class SeverityAnalyzer:
    def analyze(self, text: str) -> dict:
        """
        Analyze text and return severity level and detected keywords.
        Returns: { 'severity': str, 'confidence': int, 'keywords_detected': list }
        """
        if not text:
            return {'severity': 'Low', 'confidence': 50, 'keywords_detected': []}

        text_lower = text.lower()
        scores = {'High': 0, 'Medium': 0, 'Low': 0}
        detected_keywords = []

        for level, rules in SEVERITY_RULES.items():
            # Check keywords
            for kw in rules['keywords']:
                if kw in text_lower:
                    scores[level] += rules['weight']
                    detected_keywords.append({'keyword': kw, 'severity': level})

            # Check patterns
            for pattern in rules['patterns']:
                matches = re.findall(pattern, text_lower)
                if matches:
                    scores[level] += rules['weight']
                    for match in matches:
                        kw = match if isinstance(match, str) else ' '.join(match)
                        if kw:
                            detected_keywords.append({'keyword': kw, 'severity': level})

        # Determine severity
        if scores['High'] > 0:
            severity = 'High'
            total = max(scores['High'] + scores['Medium'] + scores['Low'], 1)
            confidence = min(int((scores['High'] / total) * 100) + 60, 99)
        elif scores['Medium'] > 0:
            severity = 'Medium'
            total = max(scores['Medium'] + scores['Low'], 1)
            confidence = min(int((scores['Medium'] / total) * 100) + 50, 95)
        else:
            severity = 'Low'
            confidence = 70 if scores['Low'] > 0 else 55

        # Deduplicate keywords
        seen = set()
        unique_keywords = []
        for kw in detected_keywords:
            if kw['keyword'] not in seen:
                seen.add(kw['keyword'])
                unique_keywords.append(kw)

        return {
            'severity': severity,
            'confidence': confidence,
            'keywords_detected': unique_keywords[:10]
        }


class DepartmentRecommender:
    def recommend(self, category: str, severity: str = 'Low') -> dict:
        """Recommend department based on category and severity"""
        department = DEPARTMENT_MAP.get(category, 'General Cyber Crime Cell')

        # Escalation for High severity
        escalation = None
        if severity == 'High':
            escalation = 'National Cyber Crime Reporting Portal (cybercrime.gov.in)'

        return {
            'department': department,
            'escalation': escalation,
            'contact': self._get_contact(department),
            'priority': self._get_priority(severity)
        }

    def _get_contact(self, department: str) -> str:
        contacts = {
            'Banking Cyber Cell': '1930 (Cyber Crime Helpline)',
            'Financial Crime Unit': '1800-11-6090',
            'Cyber Investigation Unit': 'cybercrime.gov.in',
            'Digital Forensics Team': 'cybercrime.gov.in',
            'Social Media Monitoring Cell': '1930',
            'Economic Offences Wing': '1930',
            'Identity Crime Unit': 'cybercrime.gov.in',
        }
        return contacts.get(department, '1930 (National Cyber Crime Helpline)')

    def _get_priority(self, severity: str) -> str:
        priorities = {'High': 'URGENT - 24 hours', 'Medium': 'NORMAL - 72 hours', 'Low': 'STANDARD - 7 days'}
        return priorities.get(severity, 'STANDARD - 7 days')
