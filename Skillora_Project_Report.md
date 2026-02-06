
# JSPM’s RAJARSHI SHAHU COLLEGE OF ENGINEERING, TATHAWADE, PUNE-33
**(An Autonomous Institute Affiliated to Savitribai Phule Pune University, Pune)**
**Department of Information Technology**

---

### 4. Problem Statement

In the current highly competitive job market, both job seekers and recruiters face significant challenges in efficiently connecting with the right opportunities and candidates. Traditional job portals often rely on keyword-based matching which leads to irrelevant results, and they lack personalized guidance for candidates to improve their profiles or prepare for interviews. Furthermore, manual resume screening is time-consuming and prone to bias. There is a critical need for an intelligent system that not only matches candidates to jobs using advanced natural language understanding but also provides actionable feedback and interview preparation to enhance employability. Existing systems often function as simple listing directories without leveraging AI to understand the semantic context of skills and job requirements.

### 5. Objectives of the Project

The primary objectives of the **Skillora - AI-Powered Job Recommendation and Career Assistance Platform** are:

*   **To analyze and extract insights** from candidate resumes using Natural Language Processing (NLP) for accurate skill profiling.
*   **To design and implement an intelligent recommendation engine** that matches candidates to job openings based on semantic similarity (using TF-IDF/Cosine Similarity) rather than just keyword matching.
*   **To develop an AI-driven mock interview system** that generates context-aware questions and provides feedback to help candidates prepare.
*   **To create a transparent and explainable system** that informs users why a specific job was recommended to them.

### 6. Scope of the Project

The scope of this project includes the development of a web-based application serving two main user groups: **Job Seekers** and **Recruiters**.

*   **Included:**
    *   **User Modules:** Registration, Profile Management, and Role-based access (Job Seeker/Recruiter).
    *   **Resume Processing:** Parsing PDF/DOCX resumes to extract skills, education, and experience.
    *   **Job Module:** Posting jobs, Searching with filters, and "Apply" functionality.
    *   **Recommendation System:** Algorithms to rank and recommend jobs based on profile-job similarity.
    *   **Interview Module:** automated interview sessions with AI-generated questions and feedback.
    *   **Web Interface:** A responsive frontend for accessing all features.

*   **Excluded:**
    *   Native mobile applications (Android/iOS) are currently out of scope.
    *   Complex HR Management System (HRMS) features like payroll or deep background verification.
    *   Video-conferencing integration for live human interviews (focus is on AI mock interviews).

### 7. Proposed Methodology

The project follows a modular development approach integration Machine Learning models with a robust web architecture.

**Workflow Overview:**

1.  **Data Inquest:** Users upload resumes or post job descriptions.
2.  **Preprocessing & Parsing:** The NLP module (spaCy) cleans text and extracts entities (Skills, Org, Dates).
3.  **Vectorization:** Text data is converted into numerical vectors using TF-IDF.
4.  **Matching Engine:** Cosine similarity is calculated between Candidate Vectors and Job Vectors.
5.  **Recommendation:** Top matches are ranked and presented to the user.
6.  **Interaction:** Users can trigger the AI Interview module which queries the LLM (OpenAI GPT) to generate dynamic questions based on the resume.

*(Note: Please insert a Flowchart/Block Diagram here representing: User -> Frontend -> Flask API -> NLP/ML Engine -> Database)*

### 8. Tools and Technologies

*   **Programming Languages:**
    *   Python (Backend logic, ML, NLP)
    *   JavaScript (Frontend interactivity)
    *   HTML5 / CSS3 (Structure and Styling)

*   **Software / Frameworks:**
    *   **Flask:** Lightweight Python web framework for RESTful APIs.
    *   **spCy:** Advanced Natural Language Processing library for resume parsing.
    *   **scikit-learn:** Machine learning library for vectorization and similarity metrics.
    *   **PostgreSQL:** Relational database for structured user and job data.
    *   **MongoDB:** NoSQL database for flexible document storage (resumes/logs).
    *   **OpenAI API (GPT-4):** For generating interview questions and feedback.

*   **Hardware:**
    *   Standard Development Workstations (Windows/Linux/Mac).
    *   Cloud Hosting Server (e.g., AWS/Heroku/Render) for deployment.

### 9. Expected Outcomes

*   **Enhanced Matching Accuracy:** A significant improvement in the relevance of job recommendations compared to keyword searches.
*   **Automated Resume Screening:** Reduction in time-to-shortlist for recruiters by automatically scoring resumes against job descriptions.
*   **Candidate Preparedness:** Users will gain confidence and improve interview performance through the AI mock interview practice.
*   **User-Centric design:** A responsive and intuitive interface accessible on desktop and mobile browsers.

### 10. Applications / Use Cases

*   **Recruitment Agencies:** Automating the initial screening of thousands of resumes.
*   **University Placement Cells:** Helping students identify suitable companies and practice for campus drives.
*   **Career Counseling:** Identifying skill gaps (Skill Gap Analysis) and recommending learning paths.
*   **Freelance Marketplaces:** Matching freelancers to projects based on portfolio analysis.

### 11. References

1.  D. Jurafsky and J. H. Martin, "Speech and Language Processing," 3rd ed. draft, 2023.
2.  F. Ricci, L. Rokach, and B. Shapira, "Recommender Systems Handbook," Springer, 2015.
3.  T. Mikolov et al., "Efficient Estimation of Word Representations in Vector Space," *arXiv preprint arXiv:1301.3781*, 2013.
4.  S. K. Shaukat et al., "Job Recommendation System based on convert skill set query," *International Journal of Computer Applications*, vol. 154, no. 11, 2016.
5.  Flask Documentation. Available: https://flask.palletsprojects.com/
6.  spaCy Usage Guide. Available: https://spacy.io/usage
7.  OpenAI API Documentation. Available: https://platform.openai.com/docs/
