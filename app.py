
import streamlit as st
from constraint import Problem
import random

def generate_data():
    classes = {
        'Math': {'teacher': 'Smith', 'enrollment': 10, 'req': None},
        'Science': {'teacher': 'Jones', 'enrollment': 8, 'req': 'lab'},
        'History': {'teacher': 'Smith', 'enrollment': 12, 'req': None},
        'Art': {'teacher': 'Lee', 'enrollment': 6, 'req': None},
    }
    rooms = {
        'Room101': {'capacity': 15, 'features': []},
        'Lab201': {'capacity': 10, 'features': ['lab']},
        'Room102': {'capacity': 12, 'features': []},
    }
    timeslots = ['MonAM', 'MonPM', 'TueAM', 'TuePM']
    student_enrollments = {
        'Alice': ['Math', 'Science'],
        'Bob': ['Math', 'History'],
        'Carol': ['Art', 'Science'],
        'Dave': ['History', 'Art'],
    }
    return classes, rooms, timeslots, student_enrollments

def solve_schedule(classes, rooms, timeslots, student_enrollments):
    problem = Problem()

    for class_name, details in classes.items():
        class_domain = []
        for timeslot in timeslots:
            for room_name, room_details in rooms.items():
                if details['enrollment'] <= room_details['capacity']:
                    if details['req'] is None or details['req'] in room_details['features']:
                        class_domain.append((timeslot, room_name))
        if class_domain:
            problem.addVariable(class_name, class_domain)

    def teacher_schedule_constraint(c1, c2):
        return c1[0] != c2[0]

    for i, class1_name in enumerate(classes.keys()):
        for j, class2_name in enumerate(classes.keys()):
            if i < j:
                teacher1 = classes[class1_name]['teacher']
                teacher2 = classes[class2_name]['teacher']
                if teacher1 == teacher2:
                    problem.addConstraint(teacher_schedule_constraint, [class1_name, class2_name])

    def room_schedule_constraint(c1, c2):
        return c1 != c2

    for i, class1_name in enumerate(classes.keys()):
        for j, class2_name in enumerate(classes.keys()):
            if i < j:
                problem.addConstraint(room_schedule_constraint, [class1_name, class2_name])

    def student_conflict_constraint(c1_schedule, c2_schedule):
        return c1_schedule[0] != c2_schedule[0]

    for student, enrolled_classes in student_enrollments.items():
        for i, class1_name in enumerate(enrolled_classes):
            for j, class2_name in enumerate(enrolled_classes):
                if i < j:
                    if class1_name in problem._variables and class2_name in problem._variables:
                        problem.addConstraint(student_conflict_constraint, [class1_name, class2_name])
    
    return problem.getSolutions()

st.title("Class Schedule Solver")

st.sidebar.header("Input Parameters")
num_classes = st.sidebar.slider("Number of Classes", 5, 30, 10)
num_rooms = st.sidebar.slider("Number of Rooms", 2, 15, 5)
num_students = st.sidebar.slider("Number of Students", 10, 100, 50)
num_teachers = st.sidebar.slider("Number of Teachers", 2, 10, 5)

if st.sidebar.button("Generate Schedule"):
    classes, rooms, timeslots, student_enrollments = generate_data(num_classes, num_rooms, num_students, num_teachers)
    
    with st.spinner("Finding a valid schedule..."):
        solutions = solve_schedule(classes, rooms, timeslots, student_enrollments)
    
    if not solutions:
        st.error("No possible schedule found that satisfies all constraints. The problem might be over-constrained.")
    else:
        st.success(f"Found {len(solutions)} possible schedules.")
        
        solution_to_display = solutions[0]
        
        st.subheader("Generated Schedule")
        
        schedule_data = []
        sorted_schedule = sorted(solution_to_display.items(), key=lambda item: item[1][0])
        
        for class_name, (timeslot, room) in sorted_schedule:
            teacher = classes[class_name]['teacher']
            schedule_data.append({
                "Class": class_name.replace('_', ' '),
                "Timeslot": timeslot,
                "Room": room,
                "Teacher": teacher
            })
        
        st.table(schedule_data)
