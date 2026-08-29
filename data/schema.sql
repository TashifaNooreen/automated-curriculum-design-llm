-- ============================================
-- Automated Curriculum Design Using LLMs
-- Database Schema (Draft v1)
-- ============================================

-- Users of the system: teachers/educators who configure and review curricula
CREATE TABLE users (
    user_id       SERIAL PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    email         VARCHAR(150) UNIQUE NOT NULL,
    role          VARCHAR(20) DEFAULT 'teacher',  -- teacher / admin
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Courses: the top-level entity a curriculum is generated for
CREATE TABLE courses (
    course_id     SERIAL PRIMARY KEY,
    title         VARCHAR(200) NOT NULL,
    level         VARCHAR(50),          -- Beginner / Intermediate / Advanced
    duration_weeks INT,
    objectives    TEXT,                 -- learning objectives, free text
    created_by    INT REFERENCES users(user_id),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Modules: the LLM-generated breakdown of a course (M2 output)
CREATE TABLE modules (
    module_id     SERIAL PRIMARY KEY,
    course_id     INT REFERENCES courses(course_id),
    module_number INT,
    title         VARCHAR(200),
    topics        TEXT,                 -- JSON or comma-separated topic list
    learning_outcomes TEXT,
    week_number   INT
);

-- Skills: master skill taxonomy (used by both M2 and M3)
CREATE TABLE skills (
    skill_id      SERIAL PRIMARY KEY,
    skill_name    VARCHAR(150) UNIQUE NOT NULL,
    category      VARCHAR(100)          -- e.g. technical / soft skill / tool
);

-- Module <-> Skill mapping (many-to-many)
CREATE TABLE module_skills (
    module_id     INT REFERENCES modules(module_id),
    skill_id      INT REFERENCES skills(skill_id),
    PRIMARY KEY (module_id, skill_id)
);

-- Industry skill demand (M3 output): scraped/aggregated from job postings
CREATE TABLE industry_skill_demand (
    demand_id     SERIAL PRIMARY KEY,
    skill_id      INT REFERENCES skills(skill_id),
    source        VARCHAR(100),         -- LinkedIn / Naukri / Indeed etc.
    demand_score  FLOAT,                -- normalized 0-1 or frequency count
    role_title    VARCHAR(150),
    fetched_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Students: for tracking proficiency (M1)
CREATE TABLE students (
    student_id    SERIAL PRIMARY KEY,
    name          VARCHAR(100),
    email         VARCHAR(150) UNIQUE,
    course_id     INT REFERENCES courses(course_id)
);

-- Assessments: quiz/test results feeding into M1 (knowledge tracing)
CREATE TABLE assessments (
    assessment_id SERIAL PRIMARY KEY,
    student_id    INT REFERENCES students(student_id),
    module_id     INT REFERENCES modules(module_id),
    score         FLOAT,
    attempts      INT,
    time_taken_sec INT,
    taken_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Skill mastery scores: output of M1 per student per skill
CREATE TABLE skill_mastery (
    student_id    INT REFERENCES students(student_id),
    skill_id      INT REFERENCES skills(skill_id),
    mastery_score FLOAT,                -- 0-1 scale
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id, skill_id)
);
