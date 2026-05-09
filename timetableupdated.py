import random

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

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
# FIX: assign one teacher per subject
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
            teacher_schedule[teacher] = {
                day: [] for day in DAYS
            }

# ---------------------------------------------------
# CHECK FUNCTION
# ---------------------------------------------------

def is_teacher_free(teacher, day, start, length):

    if teacher not in teacher_schedule:
        return True

    return all(
        not teacher_schedule[teacher].get(day, [False]*100)[p]
        for p in range(start, start + length)
        if p < len(teacher_schedule[teacher][day])
    )

# ---------------------------------------------------
# GENERATE TIMETABLE
# ---------------------------------------------------

def generate_timetable(class_name, periods_per_day=8):

    timetable = {day: [""] * periods_per_day for day in DAYS}
    teacher_map = {day: [""] * periods_per_day for day in DAYS}

    remaining = subjects_data.copy()

    # ------------------------------------------------
    # STEP 1: ONE CONSECUTIVE BLOCK
    # ------------------------------------------------
    for subject in subjects_data:

        block = special_subjects[subject]
        teacher = subject_teacher_map[subject]

        placed = False

        for _ in range(50):

            day = random.choice(DAYS)

            for p in range(periods_per_day - block + 1):

                if is_teacher_free(teacher, day, p, block):

                    for i in range(block):
                        timetable[day][p + i] = subject
                        teacher_map[day][p + i] = teacher

                        if len(teacher_schedule[teacher][day]) <= p + i:
                            teacher_schedule[teacher][day].extend(
                                [False] * (p + i - len(teacher_schedule[teacher][day]) + 1)
                            )

                        teacher_schedule[teacher][day][p + i] = True

                    placed = True
                    break

            if placed:
                break

    for subject in subjects_data:
        remaining[subject] -= special_subjects[subject]

    # ------------------------------------------------
    # STEP 2: SINGLE PERIOD FILL
    # ------------------------------------------------
    for subject, count in remaining.items():

        teacher = subject_teacher_map[subject]

        while count > 0:

            days = DAYS.copy()
            random.shuffle(days)

            placed = False

            for day in days:

                for p in range(periods_per_day):

                    if timetable[day][p] != "":
                        continue

                    if is_teacher_free(teacher, day, p, 1):

                        timetable[day][p] = subject
                        teacher_map[day][p] = teacher

                        if len(teacher_schedule[teacher][day]) <= p:
                            teacher_schedule[teacher][day].extend(
                                [False] * (p - len(teacher_schedule[teacher][day]) + 1)
                            )

                        teacher_schedule[teacher][day][p] = True

                        count -= 1
                        placed = True
                        break

                if placed:
                    break

            if not placed:
                break

    # ------------------------------------------------
    # STEP 3: MINIMUM 3 PERIODS PER DAY
    # ------------------------------------------------
    for day in DAYS:

        while sum(1 for p in timetable[day] if p != "") < 3:

            subjects = list(subjects_data.keys())
            random.shuffle(subjects)

            placed = False

            for subject in subjects:

                teacher = subject_teacher_map[subject]

                for p in range(periods_per_day):

                    if timetable[day][p] != "":
                        continue

                    if is_teacher_free(teacher, day, p, 1):

                        timetable[day][p] = subject
                        teacher_map[day][p] = teacher

                        placed = True
                        break

                if placed:
                    break

            if not placed:
                break

    # ------------------------------------------------
    # STEP 4: NO MIDDLE FREE PERIODS (PACKING)
    # ------------------------------------------------
    for day in DAYS:

        filled = [
            (timetable[day][p], teacher_map[day][p])
            for p in range(periods_per_day)
            if timetable[day][p] != ""
        ]

        free = periods_per_day - len(filled)

        start_free = random.randint(0, free)
        end_free = free - start_free

        packed = (
            [("", "")] * start_free +
            filled +
            [("", "")] * end_free
        )

        for p in range(periods_per_day):

            if p < len(packed):
                timetable[day][p] = packed[p][0]
                teacher_map[day][p] = packed[p][1]
            else:
                timetable[day][p] = ""
                teacher_map[day][p] = ""

    return timetable, teacher_map

# ---------------------------------------------------
# DISPLAY
# ---------------------------------------------------

def display_timetable(class_name, timetable, teacher_map, periods_per_day=8):

    print("\n")
    print("=" * 80)
    print(f"{class_name} TIMETABLE")
    print("=" * 80)

    for day in DAYS:

        print(f"\n{day}")
        print("-" * 60)

        for p in range(periods_per_day):

            subject = timetable[day][p]
            teacher = teacher_map[day][p]

            if subject == "":
                print(f"Period {p+1}: --- (Free)")
            else:
                print(f"Period {p+1}: {subject} ({teacher})")

# ---------------------------------------------------
# MAIN
# ---------------------------------------------------

periods_per_day = int(input("\nEnter periods per day: "))

for class_name in class_names:

    timetable, teacher_map = generate_timetable(class_name, periods_per_day)

    display_timetable(class_name, timetable, teacher_map, periods_per_day)

    print("\nSUCCESS: Timetable generated!")

