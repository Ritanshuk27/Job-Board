-- job-board/schema.sql
-- Drop tables if they exist to allow re-initialization without errors
DROP TABLE IF EXISTS applications;
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS users; -- NEW: Drop users table

-- Create the users table to store user credentials for login
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL, -- Username must be unique
    password TEXT NOT NULL        -- Hashed password
);

-- Create the jobs table to store job postings
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT NOT NULL,
    salary TEXT,
    description TEXT NOT NULL,
    type TEXT DEFAULT 'Full-time',
    date_posted TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the applications table to store job applications
CREATE TABLE applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL,
    applicant_name TEXT NOT NULL,
    email TEXT NOT NULL,
    resume_path TEXT,
    message TEXT,
    application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE CASCADE
);

-- Optional: Insert some initial dummy job data for testing and demonstration
INSERT INTO jobs (title, company, location, salary, description, type) VALUES
('Senior Software Engineer', 'InnovateTech Solutions', 'San Francisco, CA', '$140,000 - $180,000', 'We are looking for a highly skilled Senior Software Engineer to join our core development team. You will be responsible for designing, developing, and maintaining scalable and robust software applications. Proficiency in Python, Django/Flask, and AWS is essential.', 'Full-time'),
('Product Manager (AI/ML)', 'Quantum Innovations', 'New York, NY (Hybrid)', '$130,000 - $170,000', 'Seeking an experienced Product Manager with a strong background in AI/ML products. You will define product vision, strategy, and roadmap, working closely with engineering, design, and sales teams.', 'Full-time'),
('UI/UX Designer', 'Creative Hub Studio', 'Remote', '$90,000 - $110,000', 'Craft intuitive and visually stunning user interfaces and experiences for our web and mobile applications. You will conduct user research, create wireframes, prototypes, and high-fidelity designs using tools like Figma or Sketch.', 'Full-time'),
('Marketing Specialist', 'GrowthMark LLC', 'Austin, TX', '$60,000 - $80,000', 'Develop and execute marketing campaigns across various channels, including digital, social media, and content marketing. Analyze performance metrics and optimize strategies to drive growth.', 'Full-time'),
('Part-time Content Writer', 'Wordsmith Collective', 'Remote', '$30 - $45/hour', 'We need a talented and versatile content writer for a part-time role. You will create engaging articles, blog posts, website content, and marketing copy for diverse clients. Strong research and excellent writing skills are a must.', 'Part-time'),
('DevOps Engineer', 'CloudOps Global', 'Seattle, WA', '$150,000 - $190,000', 'Join our DevOps team to build and maintain robust, scalable, and secure cloud infrastructure. Experience with AWS, Kubernetes, Docker, and CI/CD pipelines is required. Strong scripting skills (Python/Bash) are a plus.', 'Full-time'),
('Frontend Developer', 'WebCraft Studios', 'London, UK', '£50,000 - £70,000', 'A passionate Frontend Developer needed to build highly interactive and responsive web applications. Must have strong skills in HTML, CSS, JavaScript, and modern frontend frameworks (e.g., React, Vue).', 'Full-time'),
('Customer Support Representative', 'ConnectCare Services', 'Dallas, TX', '$45,000 - $55,000', 'Provide exceptional customer service and support to our clients via phone, email, and chat. Resolve inquiries, troubleshoot issues, and ensure customer satisfaction. Excellent communication skills are essential.', 'Full-time'),
('Contract Web Developer', 'Freelance Innovations', 'Remote', '$70 - $90/hour', 'Seeking a contract web developer for a 6-month project. You will work on various client projects, including website development, e-commerce solutions, and custom web applications. Strong full-stack skills are preferred.', 'Contract'),
('Intern - Data Analyst', 'Insightful Data Co.', 'Boston, MA', '$20/hour', 'An exciting internship opportunity for a budding Data Analyst. You will assist in collecting, cleaning, and analyzing data, creating reports, and contributing to data-driven decision-making. Proficiency in Excel and basic SQL is a plus.', 'Internship');