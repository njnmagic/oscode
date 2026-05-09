import random


DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

PERIODS_PER_DAY = int(input("Enter periods per day: "))

# ---------------------------------------------------
# INPUT
# ---------------------------------------------------

num_classes = int(input("Enter number of classes: "))
class_names = [input(f"Enter class {i+1} name: ") for i in range(num_classes)]

num_subjects = int(input("\nEnter number of subjects: "))

subjects_data = {}
subject_teachers = {}
special_subjects = {}

for i in range(num_subjects):

    subject = input(f"\nEnter subject {i+1} name: ")
    subjects_data[subject] = int(input(f"Weekly periods for {subject}: "))

    subject_teachers[subject] = [
        t.strip() for t in input(
            f"Teachers for {subject} (comma separated): "
        ).split(",")
    ]

    special_subjects[subject] = int(
        input(f"Consecutive periods needed for {subject}: ")
    )

# ---------------------------------------------------
# FIX: one teacher per subject
# ---------------------------------------------------

subject_teacher_map = {
    subject: random.choice(subject_teachers[subject])
    for subject in subjects_data
}

# ---------------------------------------------------
# TEACHER SCHEDULE
# ---------------------------------------------------

teacher_schedule = {}

for teachers in subject_teachers.values():
    for teacher in teachers:

        if teacher not in teacher_schedule:
            teacher_schedule[teacher] = {}

            for day in DAYS:
                teacher_schedule[teacher][day] = [False] * PERIODS_PER_DAY

# ---------------------------------------------------
# CHECK
# ---------------------------------------------------

def is_teacher_free(teacher, day, start, length):

    return all(
        not teacher_schedule[teacher][day][p]
        for p in range(start, start + length)
    )

# ---------------------------------------------------
# GENERATE TIMETABLE
# ---------------------------------------------------

def generate_timetable(class_name):

    remaining = subjects_data.copy()

    timetable = {day: [""] * PERIODS_PER_DAY for day in DAYS}
    teacher_map = {day: [""] * PERIODS_PER_DAY for day in DAYS}

    special_day = {
        subject: random.choice(DAYS)
        for subject in subjects_data
    }

    # ------------------------------------------------
    # STEP 1: PLACE CONSECUTIVE BLOCKS
    # ------------------------------------------------
    for subject in subjects_data:

        block = special_subjects[subject]
        teacher = subject_teacher_map[subject]
        day = special_day[subject]

        for p in range(PERIODS_PER_DAY - block + 1):

            if is_teacher_free(teacher, day, p, block):

                for i in range(block):

                    timetable[day][p + i] = subject
                    teacher_map[day][p + i] = teacher
                    teacher_schedule[teacher][day][p + i] = True

                remaining[subject] -= block
                break

    # ------------------------------------------------
    # STEP 2: FILL REMAINING SUBJECTS (NO GAPS)
    # ------------------------------------------------
    for subject, count in remaining.items():

        teacher = subject_teacher_map[subject]

        while count > 0:

            days = DAYS.copy()
            random.shuffle(days)

            placed = False

            for day in days:

                empty_slots = [
                    p for p in range(PERIODS_PER_DAY)
                    if timetable[day][p] == ""
                ]

                if not empty_slots:
                    continue

                p = random.choice(empty_slots)

                if is_teacher_free(teacher, day, p, 1):

                    timetable[day][p] = subject
                    teacher_map[day][p] = teacher
                    teacher_schedule[teacher][day][p] = True

                    count -= 1
                    placed = True
                    break

            if not placed:
                break
    # ------------------------------------------------
    # STEP 3: PACK (FREE AT START + END) + MIN 3 PERIODS
    # ------------------------------------------------
    for day in DAYS:
    
        filled = [
            (timetable[day][p], teacher_map[day][p])
            for p in range(PERIODS_PER_DAY)
            if timetable[day][p] != ""
        ]
    
        free = PERIODS_PER_DAY - len(filled)
    
        # ----------------------------
        # ENSURE MINIMUM 3 PERIODS
        # ----------------------------
        subjects = list(subjects_data.keys())
    
        while len(filled) < 3:
    
            placed = False
            random.shuffle(subjects)
    
            for subject in subjects:
    
                teacher = subject_teacher_map[subject]
    
                for p in range(PERIODS_PER_DAY):
    
                    if timetable[day][p] != "":
                        continue
    
                    if is_teacher_free(teacher, day, p, 1):
    
                        filled.append((subject, teacher))
                        teacher_schedule[teacher][day][p] = True
    
                        placed = True
                        break
    
                if placed:
                    break
    
            if not placed:
                break
    
        # ----------------------------
        # PACKING (FREE BOTH SIDES)
        # ----------------------------
        free = PERIODS_PER_DAY - len(filled)
    
        start_free = random.randint(0, free)
        end_free = free - start_free
    
        packed = [("", "")] * start_free + filled + [("", "")] * end_free
    
        for p in range(PERIODS_PER_DAY):
    
            if p < len(packed):
                timetable[day][p] = packed[p][0]
                teacher_map[day][p] = packed[p][1]
            else:
                timetable[day][p] = ""
                teacher_map[day][p] = ""

# ---------------------------------------------------
# DISPLAY
# ---------------------------------------------------

def display_timetable(class_name, timetable, teacher_map):

    print("\n")
    print("=" * 80)
    print(f"{class_name} TIMETABLE")
    print("=" * 80)

    for day in DAYS:

        print(f"\n{day}")
        print("-" * 60)

        for p in range(PERIODS_PER_DAY):

            subject = timetable[day][p]
            teacher = teacher_map[day][p]

            if subject == "":
                print(f"Period {p+1}: --- (Free)")
            else:
                print(f"Period {p+1}: {subject} ({teacher})")

# ---------------------------------------------------
# MAIN
# ---------------------------------------------------

for class_name in class_names:

    timetable, teacher_map = generate_timetable(class_name)

    display_timetable(class_name, timetable, teacher_map)

    print("\nSUCCESS: Timetable generated!")
