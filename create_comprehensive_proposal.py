#!/usr/bin/env python3
"""
Create a comprehensive project proposal document following academic guidelines
"""
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

def set_para_format(para, font_size=12, alignment=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=6, line_spacing=1.5):
    """Apply standard formatting to paragraph"""
    for run in para.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(font_size)
    para.alignment = alignment
    para.paragraph_format.line_spacing = line_spacing
    para.paragraph_format.space_after = Pt(space_after)

doc = Document()

# Set margins:  Top, Bottom, Right – 1 inch; Left – 1.5 inches
sections = doc.sections
for section in sections:
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1.5)
    section.right_margin = Inches(1)

# ============== COVER PAGE ==============
p = doc.add_paragraph('MULTIMEDIA UNIVERSITY OF KENYA')
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = True
p.paragraph_format.line_spacing = 1.5
p.paragraph_format.space_after = Pt(6)

p = doc.add_paragraph('FACULTY OF COMPUTING & INFORMATION TECHNOLOGY')
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = True
p.paragraph_format.line_spacing = 1.5
p.paragraph_format.space_after = Pt(6)

for _ in range(3):
    doc.add_paragraph()

p = doc.add_paragraph('STUDENT STUDY PLANNER:\nAn Intelligent Academic Task Management and Automated Reminder System')
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(14)
    run.bold = True
p.paragraph_format.line_spacing = 1.5
p.paragraph_format.space_after = Pt(6)

for _ in range(3):
    doc.add_paragraph()

p = doc.add_paragraph('BY')
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
p.paragraph_format.line_spacing = 1.5

p = doc.add_paragraph('NAME: _________________________________\n\nREG. No: ____________________________')
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
p.paragraph_format.line_spacing = 1.5

p = doc.add_paragraph('SUPERVISOR: Yvette Otukana')
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
p.paragraph_format.line_spacing = 1.5

for _ in range(4):
    doc.add_paragraph()

p = doc.add_paragraph('APRIL 2026')
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = True
p.paragraph_format.line_spacing = 1.5

# Page break
doc.add_page_break()

# ============== DECLARATION PAGE ==============
p = doc.add_paragraph('DECLARATION')
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = True
p.paragraph_format.line_spacing = 1.5

doc.add_paragraph()

p = doc.add_paragraph('I hereby declare that this Project Proposal is my own work and has, to the best of my knowledge, not been submitted to any other institution of higher learning.')
set_para_format(p)

doc.add_paragraph()

p = doc.add_paragraph('Student:                                       Registration Number:')
set_para_format(p, alignment=WD_ALIGN_PARAGRAPH.LEFT)

p = doc.add_paragraph('_' * 35 + '          ' + '_' * 35)
set_para_format(p, alignment=WD_ALIGN_PARAGRAPH.LEFT)

doc.add_paragraph()

p = doc.add_paragraph('Signature: ' + '_' * 40 + '    Date: ' + '_' * 20)
set_para_format(p, alignment=WD_ALIGN_PARAGRAPH.LEFT)

doc.add_paragraph()
doc.add_paragraph()

p = doc.add_paragraph('This Project Proposal has been submitted as a partial fulfillment of requirements for the Bachelor of Science in Computer/Information Technology of Multimedia University of Kenya with my approval as the University supervisor.')
set_para_format(p)

doc.add_paragraph()

p = doc.add_paragraph('Supervisor: _________________________')
set_para_format(p, alignment=WD_ALIGN_PARAGRAPH.LEFT)

p = doc.add_paragraph('Signature: ' + '_' * 40 + '    Date: ' + '_' * 20)
set_para_format(p, alignment=WD_ALIGN_PARAGRAPH.LEFT)

doc.add_page_break()

# ============== ACKNOWLEDGEMENTS ==============
p = doc.add_paragraph('ACKNOWLEDGEMENTS')
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = True
p.paragraph_format.line_spacing = 1.5

doc.add_paragraph()

p = doc.add_paragraph(
    'I wish to extend my sincere gratitude to my supervisor, Yvette Otukana, for her invaluable guidance, constructive feedback, and continuous support throughout the development of this project proposal. Her expertise and mentorship have been instrumental in shaping the direction and scope of this work.\n\n'
    'I would like to acknowledge the Faculty of Computing & Information Technology at Multimedia University of Kenya for providing the necessary resources and infrastructure to conduct this project.\n\n'
    'Special thanks to the Django community and open-source contributors whose frameworks and libraries have made this project possible.\n\n'
    'Finally, I appreciate the support of my peers and colleagues who have provided valuable insights and feedback during the development process.'
)
set_para_format(p)

doc.add_page_break()

# ============== ABSTRACT ==============
p = doc.add_paragraph('ABSTRACT')
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = True
p.paragraph_format.line_spacing = 1.5

doc.add_paragraph()

p = doc.add_paragraph(
    'University students face significant challenges in managing multiple academic commitments including assignments, continuous assessment tests, class schedules, and deadlines. Traditional planning methods lack integration and automation, resulting in missed deadlines and forgotten classes. This project proposes the development of the Student Study Planner, a comprehensive Django-based web application designed to address these challenges. The system combines intelligent task management with automated email reminders, AI-powered PDF timetable extraction, and a personalized dashboard. Built using Python 3.13, Django 5.2.7, and modern web technologies, the application will support task tracking across multiple courses, automated timezone-aware notifications via Gmail SMTP, and user authentication with profile customization. The system architecture follows MVC principles with modular applications for accounts, tasks, timetables, and notifications. Implementation employs APScheduler for background task scheduling without requiring external services like Celery or Redis. Expected outcomes include improved deadline adherence, reduced manual scheduling effort, and a scalable platform demonstrating proficiency in full-stack web development, database design, email automation, and user experience design.'
)
set_para_format(p)

doc.add_page_break()

# ============== TABLE OF CONTENTS ==============
p = doc.add_paragraph('TABLE OF CONTENTS')
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = True
p.paragraph_format.line_spacing = 1.5

doc.add_paragraph()

toc_items = [
    'ACKNOWLEDGEMENTS',
    'ABSTRACT',
    'LIST OF ABBREVIATIONS',
    'CHAPTER 1: INTRODUCTION',
    '    1.1 Background of Study',
    '    1.2 Problem Statement',
    '    1.3 Aim of the Study',
    '    1.4 Significance/Justification of the Study',
    '    1.5 Scope',
    '    1.6 Assumptions',
    '    1.7 Limitations',
    'CHAPTER 2: LITERATURE REVIEW',
    '    2.1 Introduction',
    '    2.2 Related Systems and Technologies',
    '    2.3 Limitations and Weaknesses',
    '    2.4 How Proposed Solution Addresses Weaknesses',
    'CHAPTER 3: METHODOLOGY',
    '    3.1 Introduction',
    '    3.2 Development Methodology',
    '    3.3 Data Collection Methods',
    '    3.4 Project Resources',
    '    3.5 Project Schedule',
    '    3.6 Project Budget',
    'REFERENCES'
]

for item in toc_items:
    p = doc.add_paragraph(item if not item.startswith('    ') else item[4:])
    if item.startswith('    '):
        p.paragraph_format.left_indent = Inches(0.5)
    for run in p.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(3)

doc.add_page_break()

# ============== LIST OF ABBREVIATIONS ==============
p = doc.add_paragraph('LIST OF ABBREVIATIONS')
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = True
p.paragraph_format.line_spacing = 1.5

doc.add_paragraph()

abbrevs = [
    ('API', 'Application Programming Interface'),
    ('SMTP', 'Simple Mail Transfer Protocol'),
    ('HTML', 'HyperText Markup Language'),
    ('CSS', 'Cascading Style Sheets'),
    ('MVC', 'Model-View-Controller'),
    ('PDF', 'Portable Document Format'),
    ('NLP', 'Natural Language Processing'),
    ('ML', 'Machine Learning'),
    ('SQLite', 'Structured Query Language Lite'),
    ('ORM', 'Object-Relational Mapping'),
    ('APScheduler', 'Advanced Python Scheduler'),
    ('CAT', 'Continuous Assessment Test'),
    ('UI', 'User Interface'),
    ('UX', 'User Experience'),
]

table = doc.add_table(rows=len(abbrevs) + 1, cols=2)
table.style = 'Light Grid Accent 1'

header = table.rows[0].cells
header[0].text = 'Abbreviation'
header[1].text = 'Full Meaning'

for i, (abbr, meaning) in enumerate(abbrevs, 1):
    row = table.rows[i].cells
    row[0].text = abbr
    row[1].text = meaning

doc.add_page_break()

# ============== CHAPTER 1 ==============
p = doc.add_paragraph('CHAPTER 1: INTRODUCTION')
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = True
p.paragraph_format.line_spacing = 1.5

doc.add_paragraph()

# 1.1 Background
p = doc.add_paragraph('1.1 Background of Study')
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = True
set_para_format(p, alignment=WD_ALIGN_PARAGRAPH.LEFT)

p = doc.add_paragraph(
    'The advancement of digital technology has significantly transformed educational systems globally. Universities have increasingly adopted various technologies and tools to support student learning, administrative efficiency, and communication. However, despite these advancements, many students continue to struggle with organizing and managing their academic workload effectively.'
)
set_para_format(p)

p = doc.add_paragraph(
    'Student life presents multiple concurrent demands: attending lectures, completing assignments, preparing for continuous assessment tests (CATs), and managing group projects. These responsibilities are often scattered across different platforms, communication channels, and physical locations. The complexity of juggling multiple courses, each with varying assessment schedules and timing requirements, creates significant cognitive load on students.'
)
set_para_format(p)

p = doc.add_paragraph(
    'Traditional academic planning methods—such as printed timetables, paper planners, and basic calendar applications—lack the integration and automation capabilities necessary for modern student life. Many students resort to manual tracking across multiple tools, leading to inconsistencies, missed reminders, and inefficient time management. The absence of automated notifications and unified task tracking often results in missed deadlines, forgotten classes, and academic performance deterioration.'
)
set_para_format(p)

p = doc.add_paragraph(
    'Recent developments in web technologies, including mobile-responsive design, cloud computing, and automated task scheduling, present opportunities to develop comprehensive solutions that integrate multiple academic management functions into a single coherent system.'
)
set_para_format(p)

doc.add_paragraph()

# 1.2 Problem Statement
p = doc.add_paragraph('1.2 Problem Statement')
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = True
set_para_format(p, alignment=WD_ALIGN_PARAGRAPH.LEFT)

p = doc.add_paragraph('University students face critical challenges in managing their academic responsibilities efficiently. Specifically:')
set_para_format(p)

problems = [
    'Multiple courses with independent task, assignment, and test schedules are difficult to track in a unified manner',
    'Task deadlines and class schedules are often scattered across different platforms and sources',
    'Manual effort is required to organize class timetables from various documents',
    'Students frequently miss deadlines and forget about scheduled classes',
    'Notification systems are not integrated with academic management tools',
    'Students in different timezones face challenges with scheduling systems',
]

for prob in problems:
    p = doc.add_paragraph(prob, style='List Bullet')
    for run in p.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(6)

p = doc.add_paragraph('These challenges collectively result in poor academic planning and suboptimal time management. There is a clear need for an integrated, automated solution.')
set_para_format(p)

doc.add_paragraph()

# 1.3 Aim
p = doc.add_paragraph('1.3 Aim of the Study')
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = True
set_para_format(p, alignment=WD_ALIGN_PARAGRAPH.LEFT)

p = doc.add_paragraph('The primary aim is to develop a comprehensive, intelligent web-based academic management system that enables students to efficiently organize their academic work and receive automated reminders.')
set_para_format(p)

doc.add_paragraph()

# 1.3.1 Objectives
p = doc.add_paragraph('1.3.1 Research Objectives')
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = True
set_para_format(p, alignment=WD_ALIGN_PARAGRAPH.LEFT)

objectives = [
    'To develop a centralized digital platform for task, assignment, and class schedule management',
    'To implement an intelligent timetable system that can extract class information from PDF documents',
    'To create an automated reminder system that sends timely email notifications',
    'To design a responsive user interface across desktop, tablet, and mobile devices',
    'To implement secure user authentication and customizable notification preferences',
    'To support timezone-aware scheduling for international students',
    'To demonstrate best practices in full-stack web development',
    'To create a scalable architecture supporting multiple universities',
]

for obj in objectives:
    p = doc.add_paragraph(obj, style='List Bullet')
    for run in p.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(6)

doc.add_page_break()

# 1.4 Significance
p = doc.add_paragraph('1.4 Significance and Justification of the Study')
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = True
set_para_format(p, alignment=WD_ALIGN_PARAGRAPH.LEFT)

p = doc.add_paragraph('This project addresses a significant gap in the academic technology landscape. While individual tools exist for task management, few integrated solutions specifically target the holistic academic management needs of university students.')
set_para_format(p)

p = doc.add_paragraph('For Students: The system provides improved deadline adherence, reduced cognitive load, and better time allocation. For Universities: The system can support student success initiatives and retention programs. For Software Engineering: This project demonstrates proficiency in Django development, database design, email integration, and responsive web design.')
set_para_format(p)

doc.add_paragraph()

# 1.5 Scope
p = doc.add_paragraph('1.5 Scope')
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = True
set_para_format(p, alignment=WD_ALIGN_PARAGRAPH.LEFT)

p = doc.add_paragraph('In Scope:')
p.runs[0].bold = True
set_para_format(p)

in_scope_items = [
    'User registration, authentication, and profile management',
    'Task management system with multiple task types',
    'Timetable management with PDF upload and AI extraction',
    'Automated email reminder system with timezone support',
    'Responsive web interface',
    'Database design supporting scalability',
]

for item in in_scope_items:
    p = doc.add_paragraph(item, style='List Bullet')
    for run in p.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(6)

p = doc.add_paragraph('Out of Scope:')
p.runs[0].bold = True
set_para_format(p)

out_scope_items = [
    'Native mobile applications',
    'Third-party calendar integration',
    'Multi-language support',
    'Video streaming or multimedia content',
]

for item in out_scope_items:
    p = doc.add_paragraph(item, style='List Bullet')
    for run in p.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(6)

doc.add_paragraph()

# 1.6 Assumptions
p = doc.add_paragraph('1.6 Assumptions')
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = True
set_para_format(p, alignment=WD_ALIGN_PARAGRAPH.LEFT)

assumptions = [
    'Students have regular internet connectivity and email access',
    'PDF timetables follow standard text-based formats',
    'Email SMTP remains available and stable',
    'Users utilize modern web browsers',
]

for assumption in assumptions:
    p = doc.add_paragraph(assumption, style='List Bullet')
    for run in p.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(6)

doc.add_paragraph()

# 1.7 Limitations
p = doc.add_paragraph('1.7 Limitations')
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = True
set_para_format(p, alignment=WD_ALIGN_PARAGRAPH.LEFT)

limitations = [
    'PDF extraction may fail on poor quality scanned documents; manual entry provided as fallback',
    'Email delivery depends on SMTP availability; reminder logs stored for audit trail',
    'While 9 timezones supported, system can be extended to support more',
    'SQLite suitable for development; PostgreSQL required for production scale',
    'System effectiveness depends on consistent user adoption',
]

for limitation in limitations:
    p = doc.add_paragraph(limitation, style='List Bullet')
    for run in p.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(6)

doc.add_page_break()

# ==============CHAPTER 2 ==============
p = doc.add_paragraph('CHAPTER 2: LITERATURE REVIEW')
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = True
p.paragraph_format.line_spacing = 1.5

doc.add_paragraph()

# 2.1
p = doc.add_paragraph('2.1 Introduction')
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = True
set_para_format(p, alignment=WD_ALIGN_PARAGRAPH.LEFT)

p = doc.add_paragraph('This chapter presents a comprehensive review of existing technologies, solutions, and systems related to academic task management and automated reminders. It examines related systems, analyzes their limitations, and demonstrates how the proposed solution addresses identified gaps.')
set_para_format(p)

doc.add_paragraph()

# 2.2
p = doc.add_paragraph('2.2 Related Systems and Technologies')
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = True
set_para_format(p, alignment=WD_ALIGN_PARAGRAPH.LEFT)

p = doc.add_paragraph('2.2.1 Google Calendar and Microsoft Outlook')
p.runs[0].bold = True
set_para_format(p)

p = doc.add_paragraph('Google Calendar and Outlook are widely-used calendar and task management applications providing robust scheduling, recurring events, and email integration. However, they lack academic-specific features such as automatic timetable extraction, course-specific task categorization, or academic deadline-focused reminders.')
set_para_format(p)

p = doc.add_paragraph('2.2.2 Learning Management Systems (Canvas, Blackboard)')
p.runs[0].bold = True
set_para_format(p)

p = doc.add_paragraph('Canvas and Blackboard are comprehensive LMS platforms used by universities. They provide course management, assignment submission, and grade tracking. However, they are institution-specific and often lack convenient personal task management and integrated reminder systems for student use outside the formal LMS.')
set_para_format(p)

p = doc.add_paragraph('2.2.3 General Task Management (Todoist, Asana)')
p.runs[0].bold = True
set_para_format(p)

p = doc.add_paragraph('Todoist and Asana offer powerful task organization and team collaboration. However, they lack academic-specific features and require manual entry of all academic commitments.')
set_para_format(p)

p = doc.add_paragraph('2.2.4 Student Planner Applications')
p.runs[0].bold = True
set_para_format(p)

p = doc.add_paragraph('Applications like My Study Life and Timetable2000 focus on timetable and task tracking but lack sophisticated features such as automated PDF extraction, intelligent reminders, timezone awareness, or scalable architectures.')
set_para_format(p)

doc.add_paragraph()

# 2.3
p = doc.add_paragraph('2.3 Limitations and Weaknesses of Existing Systems')
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = True
set_para_format(p, alignment=WD_ALIGN_PARAGRAPH.LEFT)

weaknesses = [
    'Fragmented Ecosystem: Students use multiple separate tools, creating information silos',
    'Limited Academic Features: Lack of CAT tracking, course organization, academic deadline focus',
    'Manual Data Entry: Require students to manually enter all academic information',
    'Weak Automation: Few provide truly intelligent, automated reminders',
    'Limited Timezone Support: Problematic for international students',
    'Scalability Issues: Not architected for institutional scale',
    'Complex Interfaces: Some systems suffer from feature overload',
]

for weakness in weaknesses:
    p = doc.add_paragraph(weakness, style='List Bullet')
    for run in p.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(6)

doc.add_paragraph()

# 2.4
p = doc.add_paragraph('2.4 How the Proposed Solution Addresses These Weaknesses')
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = True
set_para_format(p, alignment=WD_ALIGN_PARAGRAPH.LEFT)

solutions = [
    'Unified Platform: Integrates tasks, classes, reminders into a single system',
    'Academic-Focused: Purpose-built for student academic management',
    'Intelligent Extraction: AI-powered PDF parsing reduces manual entry',
    'Sophisticated Automation: Timezone-aware reminder scheduling',
    'Robust Timezone Support: Extensible to any timezone',
    'Scalable Architecture: Modular Django applications supporting growth',
    'User-Centric Design: Clean interface focusing on essential tasks',
]

for solution in solutions:
    p = doc.add_paragraph(solution, style='List Bullet')
    for run in p.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(6)

doc.add_page_break()

# ============== CHAPTER 3 ==============
p = doc.add_paragraph('CHAPTER 3: METHODOLOGY')
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = True
p.paragraph_format.line_spacing = 1.5

doc.add_paragraph()

# 3.1
p = doc.add_paragraph('3.1 Introduction')
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = True
set_para_format(p, alignment=WD_ALIGN_PARAGRAPH.LEFT)

p = doc.add_paragraph('This chapter outlines the methodology for developing the Student Study Planner. It describes the development approach, technology selection, data collection methods, project resources, schedule, and budget.')
set_para_format(p)

doc.add_paragraph()

# 3.2
p = doc.add_paragraph('3.2 Development Methodology')
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = True
set_para_format(p, alignment=WD_ALIGN_PARAGRAPH.LEFT)

p = doc.add_paragraph('Approach: Agile Iterative Development')
p.runs[0].bold = True
set_para_format(p)

p = doc.add_paragraph('The project employs an iterative agile development approach with waterfall-style phase gates, providing iterative feedback, clear phase delineation, and flexibility for course correction.')
set_para_format(p)

p = doc.add_paragraph('Development Phases:')
p.runs[0].bold = True
set_para_format(p)

phases = [
    'Phase 1: Requirements and Design (weeks 1-2)',
    'Phase 2: Core Backend Development (weeks 3-6)',
    'Phase 3: AI/ML PDF Integration (weeks 7-9)',
    'Phase 4: Automation and Notifications (weeks 10-12)',
    'Phase 5: Frontend Development (weeks 13-15)',
    'Phase 6: Testing and Quality Assurance (weeks 16-17)',
    'Phase 7: Deployment and Documentation (week 18)',
]

for phase in phases:
    p = doc.add_paragraph(phase, style='List Bullet')
    for run in p.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(6)

doc.add_paragraph()

# 3.3
p = doc.add_paragraph('3.3 Data Collection Methods and Tools')
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = True
set_para_format(p, alignment=WD_ALIGN_PARAGRAPH.LEFT)

p = doc.add_paragraph('User Requirements: Semi-structured interviews with target users to understand planning challenges and feature preferences.\n\nSample Data: Creation of representative datasets including PDF timetables, task lists, and student profiles for testing.\n\nPrototyping: Iterative prototyping to verify technical feasibility of PDF extraction and scheduler components.')
set_para_format(p)

doc.add_paragraph()

# 3.4
p = doc.add_paragraph('3.4 Project Resources (Hardware/Software)')
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = True
set_para_format(p, alignment=WD_ALIGN_PARAGRAPH.LEFT)

p = doc.add_paragraph('Hardware: Development workstation (i5+, 8GB RAM, 256GB SSD), testing devices (desktop, tablet, mobile), deployment server.')
set_para_format(p)

p = doc.add_paragraph('Software: Python 3.13, Django 5.2.7, SQLite/PostgreSQL, APScheduler 3.11, Tailwind CSS, HTML5, JavaScript, VS Code, Git.')
set_para_format(p)

doc.add_paragraph()

# 3.5
p = doc.add_paragraph('3.5 Project Schedule')
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = True
set_para_format(p, alignment=WD_ALIGN_PARAGRAPH.LEFT)

p = doc.add_paragraph('Total Duration: 18 weeks (16 weeks development + 2 weeks contingency/buffer)\n\nMajor Milestones:\n• Week 2: Design review and approval\n• Week 6: Backend core functionality complete\n• Week 9: PDF extraction system functional\n• Week 12: Email notification system operational\n• Week 15: User interface complete and responsive\n• Week 17: All testing complete, bugs resolved\n• Week 18: System deployed to production')
set_para_format(p)

doc.add_page_break()

# 3.6
p = doc.add_paragraph('3.6 Project Budget')
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = True
set_para_format(p, alignment=WD_ALIGN_PARAGRAPH.LEFT)

table = doc.add_table(rows=10, cols=2)
table.style = 'Light Grid Accent 1'

header = table.rows[0].cells
header[0].text = 'Category/Item'
header[1].text = 'Estimated Cost (KES)'

budget = [
    ('Development Time (160 hours @ 500/hr)', '80,000'),
    ('Software Licenses/Subscriptions', '5,000'),
    ('Cloud Hosting (16 weeks)', '40,000'),
    ('Domain Registration (1 year)', '2,500'),
    ('Email SMTP Service', '3,000'),
    ('Testing and QA Tools', '5,000'),
    ('Documentation Preparation', '8,000'),
    ('Contingency (10%)', '15,350'),
    ('TOTAL ESTIMATED COST', '158,850'),
]

for i, (item, cost) in enumerate(budget, 1):
    row = table.rows[i].cells
    row[0].text = item
    row[1].text = cost
    if item == 'TOTAL ESTIMATED COST':
        row[0].paragraphs[0].runs[0].bold = True
        row[1].paragraphs[0].runs[0].bold = True

doc.add_paragraph()

p = doc.add_paragraph('Note: Most software components are open-source and free. This budget reflects development time, hosting infrastructure, and contingency.')
set_para_format(p, font_size=10)

doc.add_page_break()

# ============== REFERENCES ==============
p = doc.add_paragraph('REFERENCES')
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
for run in p.runs:
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = True
p.paragraph_format.line_spacing = 1.5

doc.add_paragraph()

references = [
    'Django Software Foundation. (2024). Django 5.2 Documentation. Retrieved from https://docs.djangoproject.com/en/5.2/',
    'Martelli, A., Ravenscroft, A., & Holden, S. (2020). Python in a Nutshell: A Desktop Quick Reference (3rd ed.). O\'Reilly Media.',
    'APScheduler Development Team. (2024). Advanced Python Scheduler Documentation. Retrieved from https://apscheduler.readthedocs.io/',
    'Tailwind Labs. (2024). Tailwind CSS Documentation. Retrieved from https://tailwindcss.com/docs',
    'Mozilla Developer Network. (2024). Web Development References. Retrieved from https://developer.mozilla.org/',
    'Fowler, M. (2018). Refactoring: Improving the Design of Existing Code (2nd ed.). Addison-Wesley.',
    'Python Software Foundation. (2024). Python Standard Library - smtplib. Retrieved from https://docs.python.org/3/library/smtplib.html',
    'Pillow Contributors. (2024). Pillow (PIL) Documentation. Retrieved from https://pillow.readthedocs.io/',
    'Sommerville, I. (2015). Software Engineering (10th ed.). Pearson.',
    'Pressman, R., & Maxim, B. (2014). Software Engineering: A Practitioner\'s Approach. McGraw-Hill.',
    'Nielsen, J. (2012). Usability 101: Introduction to Usability. Nielsen Norman Group.',
    'PostgreSQL Global Development Group. (2024). PostgreSQL Documentation. Retrieved from https://www.postgresql.org/docs/',
    'Martin, R. C. (2008). Clean Code: A Handbook of Agile Software Craftsmanship. Prentice Hall.',
]

for ref in references:
    p = doc.add_paragraph(ref)
    p.paragraph_format.left_indent = Inches(0.5)
    p.paragraph_format.first_line_indent = Inches(-0.5)
    for run in p.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(6)

# Save
doc.save('COMPREHENSIVE_PROJECT_PROPOSAL.docx')
print('✓ COMPREHENSIVE PROJECT PROPOSAL CREATED!')
print('✓ File: COMPREHENSIVE_PROJECT_PROPOSAL.docx')
print('✓ All sections included per academic guidelines')
print('✓ Professional formatting applied throughout')
