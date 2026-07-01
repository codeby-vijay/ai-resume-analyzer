"""Curated skill taxonomy used for extraction and matching.
In production this would live in the `skill_database` table and be
editable via the admin dashboard; it is seeded from this list on startup.
"""

TECHNICAL_SKILLS = [
    # Programming languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "php", "ruby", "swift", "kotlin", "scala", "r", "matlab", "sql",
    # Web
    "react", "angular", "vue", "next.js", "node.js", "express", "django",
    "flask", "fastapi", "spring boot", "html", "css", "tailwind css",
    "bootstrap", "graphql", "rest api", "webpack",
    # Data / ML
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "tensorflow", "pytorch", "keras", "scikit-learn",
    "pandas", "numpy", "data analysis", "data visualization", "tableau",
    "power bi", "statistics", "a/b testing", "feature engineering",
    "model deployment", "mlops", "hugging face", "llm", "generative ai",
    "prompt engineering", "reinforcement learning",
    # Cloud / DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins",
    "ci/cd", "linux", "bash", "git", "github actions", "ansible",
    "microservices", "serverless",
    # Database
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "sqlite",
    "oracle", "dynamodb", "cassandra",
    # Other
    "agile", "scrum", "jira", "system design", "api design",
    "unit testing", "test driven development", "object oriented programming",
    "data structures", "algorithms",
]

SOFT_SKILLS = [
    "communication", "leadership", "teamwork", "problem solving",
    "critical thinking", "time management", "adaptability", "creativity",
    "collaboration", "project management", "mentoring", "public speaking",
    "negotiation", "conflict resolution", "decision making",
    "attention to detail", "analytical thinking", "emotional intelligence",
    "stakeholder management", "presentation skills",
]

ALL_SKILLS = TECHNICAL_SKILLS + SOFT_SKILLS

CERTIFICATION_MAP = {
    "aws": ["AWS Certified Solutions Architect – Associate", "AWS Certified Cloud Practitioner"],
    "azure": ["Microsoft Certified: Azure Fundamentals (AZ-900)", "Azure Administrator Associate (AZ-104)"],
    "gcp": ["Google Cloud Associate Cloud Engineer"],
    "machine learning": ["Coursera Machine Learning Specialization (Andrew Ng)", "AWS Certified Machine Learning – Specialty"],
    "deep learning": ["DeepLearning.AI Deep Learning Specialization"],
    "data analysis": ["Google Data Analytics Professional Certificate"],
    "kubernetes": ["Certified Kubernetes Administrator (CKA)"],
    "docker": ["Docker Certified Associate"],
    "project management": ["PMP – Project Management Professional", "Certified ScrumMaster (CSM)"],
    "sql": ["Microsoft SQL Server Certification", "Kaggle SQL Micro-course"],
    "react": ["Meta Front-End Developer Professional Certificate"],
    "cybersecurity": ["CompTIA Security+", "Certified Ethical Hacker (CEH)"],
    "nlp": ["Hugging Face NLP Course", "Stanford CS224N (self-paced)"],
    "tensorflow": ["TensorFlow Developer Certificate"],
    "scrum": ["Certified ScrumMaster (CSM)"],
}

EDUCATION_KEYWORDS = [
    "bachelor", "b.tech", "b.e.", "bsc", "b.sc", "master", "m.tech", "msc",
    "m.sc", "mba", "phd", "doctorate", "associate degree", "diploma",
    "university", "college", "institute of technology",
]

EXPERIENCE_KEYWORDS = [
    "years of experience", "years experience", "worked as", "internship",
    "employed", "professional experience", "work history",
]
