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
# GENERATE
# ---------------------------------------------------

def generate_timetable(class_name, periods_per_day):

    timetable = {d: [""] * periods_per_day for d in DAYS}
    teacher_map = {d: [""] * periods_per_day for d in DAYS}

    subject_used = {s: 0 for s in subjects_data}

    subject_teacher_map = {
        s: random.choice(subject_teachers[s])
        for s in subjects_data
    }

    teacher_schedule = {
        t: {d: [False] * periods_per_day for d in DAYS}
        for teachers in subject_teachers.values()
        for t in teachers
    }

    reserved = set()  # 🔒 locks consecutive blocks

    # ---------------------------------------------------
    # HELPERS
    # ---------------------------------------------------

    def remaining(subject):
        return subjects_data[subject] - subject_used[subject]

    def teacher_free(teacher, day, start, length):
        return all(
            not teacher_schedule[teacher][day][p]
            for p in range(start, start + length)
        )

    def place(subject, teacher, day, start, length):

        if remaining(subject) < length:
            return False

        for i in range(length):
            timetable[day][start + i] = subject
            teacher_map[day][start + i] = teacher
            teacher_schedule[teacher][day][start + i] = True

        subject_used[subject] += length
        return True

    # ---------------------------------------------------
    # STEP 1: STRICT CONSECUTIVE BLOCK (FIXED)
    # ---------------------------------------------------

    for subject in subjects_data:

        teacher = subject_teacher_map[subject]
        block = special_subjects[subject]

        placed = False

        for _ in range(100):

            day = random.choice(DAYS)

            for p in range(periods_per_day - block + 1):

                # check availability + reservation
                ok = True

                for i in range(block):
                    if timetable[day][p + i] != "" or (day, p + i) in reserved:
                        ok = False
                        break

                if not ok:
                    continue

                if teacher_free(teacher, day, p, block):

                    for i in range(block):
                        timetable[day][p + i] = subject
                        teacher_map[day][p + i] = teacher
                        teacher_schedule[teacher][day][p + i] = True
                        reserved.add((day, p + i))  # lock

                    subject_used[subject] += block
                    placed = True
                    break

            if placed:
                break

    # ---------------------------------------------------
    # STEP 2: SINGLE PERIOD DISTRIBUTION
    # ---------------------------------------------------

    for subject in subjects_data:

        teacher = subject_teacher_map[subject]

        while remaining(subject) > 0:

            days = DAYS.copy()
            random.shuffle(days)

            placed = False

            for day in days:

                for p in range(periods_per_day):

                    if timetable[day][p] != "" or (day, p) in reserved:
                        continue

                    if teacher_free(teacher, day, p, 1):

                        place(subject, teacher, day, p, 1)
                        placed = True
                        break

                if placed:
                    break

            if not placed:
                break

    # ---------------------------------------------------
    # STEP 3: MIN 3 PERIODS PER DAY (SOFT RULE)
    # ---------------------------------------------------

    for day in DAYS:

        filled = sum(1 for x in timetable[day] if x != "")

        if filled >= 3:
            continue

        needed = 3 - filled

        subjects = list(subjects_data.keys())
        random.shuffle(subjects)

        for subject in subjects:

            if needed <= 0:
                break

            teacher = subject_teacher_map[subject]

            for p in range(periods_per_day):

                if timetable[day][p] == "" and (day, p) not in reserved:

                    if teacher_free(teacher, day, p, 1):

                        place(subject, teacher, day, p, 1)
                        needed -= 1
                        break

    # ---------------------------------------------------
    # STEP 4: FREE ONLY AT START/END (NO MIDDLE FREE)
    # ---------------------------------------------------

    for day in DAYS:

        filled = [
            (timetable[day][p], teacher_map[day][p])
            for p in range(periods_per_day)
            if timetable[day][p] != ""
        ]

        free_slots = periods_per_day - len(filled)

        start_free = random.randint(0, free_slots)
        end_free = free_slots - start_free

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

    # ---------------------------------------------------
    # DISPLAY
    # ---------------------------------------------------

    print("\n")
    print("=" * 80)
    print(f"{class_name} TIMETABLE")
    print("=" * 80)

    for day in DAYS:

        print(f"\n{day}")
        print("-" * 60)

        for p in range(periods_per_day):

            s = timetable[day][p]
            t = teacher_map[day][p]

            if s == "":
                print(f"Period {p+1}: --- (Free)")
            else:
                print(f"Period {p+1}: {s} ({t})")

# ---------------------------------------------------
# MAIN
# ---------------------------------------------------

periods_per_day = int(input("\nEnter periods per day: "))

for class_name in class_names:

    generate_timetable(class_name, periods_per_day)

    print("\nSUCCESS: Timetable generated!")

