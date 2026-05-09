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

periods_per_day = int(input("\nEnter periods per day: "))


# ---------------------------------------------------
# GENERATE
# ---------------------------------------------------

def generate_timetable(class_name, periods_per_day):

    timetable = {d: [""] * periods_per_day for d in DAYS}
    teacher_map = {d: [""] * periods_per_day for d in DAYS}

    teacher_schedule = {
        t: {d: [False] * periods_per_day for d in DAYS}
        for teachers in subject_teachers.values()
        for t in teachers
    }

    reserved = set()

    subject_teacher_map = {
        s: random.choice(subject_teachers[s])
        for s in subjects_data
    }

    block_day_used = {}  # subject → fixed block day

    # ---------------------------------------------------
    # HELPERS
    # ---------------------------------------------------

    def teacher_free(teacher, day, start, length):
        return all(
            not teacher_schedule[teacher][day][p]
            for p in range(start, start + length)
        )

    def can_place(subject, teacher, day, start, length):

        if timetable[day][start:start+length] != [""] * length:
            return False

        if any((day, start+i) in reserved for i in range(length)):
            return False

        if not teacher_free(teacher, day, start, length):
            return False

        return True

    def place(subject, teacher, day, start, length):

        for i in range(length):
            timetable[day][start + i] = subject
            teacher_map[day][start + i] = teacher
            teacher_schedule[teacher][day][start + i] = True
            reserved.add((day, start + i))

        return True

    # ---------------------------------------------------
    # STEP 1: CREATE STRUCTURE (BLOCK + SINGLES)
    # ---------------------------------------------------

    schedule = []

    for subject, total in subjects_data.items():

        teacher = subject_teacher_map[subject]
        block = special_subjects[subject]

        # BLOCK (only once)
        if block > 1 and total >= block:
            schedule.append((subject, teacher, block, "BLOCK"))
            total -= block

        # SINGLES
        for _ in range(total):
            schedule.append((subject, teacher, 1, "SINGLE"))

    random.shuffle(schedule)

    # ---------------------------------------------------
    # STEP 2: PLACE BLOCKS FIRST (FIXED DAY)
    # ---------------------------------------------------

    for subject, teacher, length, mode in schedule:

        placed = False

        # BLOCK RULE
        if mode == "BLOCK":

            if subject in block_day_used:
                day = block_day_used[subject]
            else:
                day = random.choice(DAYS)
                block_day_used[subject] = day

            for _ in range(200):
                start = random.randint(0, periods_per_day - length)

                if can_place(subject, teacher, day, start, length):
                    place(subject, teacher, day, start, length)
                    placed = True
                    break

        schedule[schedule.index((subject, teacher, length, mode))] = schedule[schedule.index((subject, teacher, length, mode))] if placed else schedule[schedule.index((subject, teacher, length, mode))]

    # ---------------------------------------------------
    # STEP 3: PLACE SINGLE PERIODS (SPREAD ACROSS DAYS)
    # ---------------------------------------------------

    for subject, teacher, length, mode in schedule:

        if mode != "SINGLE":
            continue

        placed = False

        for _ in range(200):

            days = DAYS.copy()
            random.shuffle(days)

            for day in days:

                # avoid block day for same subject
                if day == block_day_used.get(subject, None):
                    continue

                for p in range(periods_per_day):

                    if can_place(subject, teacher, day, p, 1):

                        place(subject, teacher, day, p, 1)
                        placed = True
                        break

                if placed:
                    break

            if placed:
                break

    # ---------------------------------------------------
    # VALIDATION (STRICT CHECK)
    # ---------------------------------------------------

    count = {s: 0 for s in subjects_data}

    for d in DAYS:
        for p in range(periods_per_day):
            if timetable[d][p]:
                count[timetable[d][p]] += 1

    for s in subjects_data:
        if count[s] != subjects_data[s]:
            print(f"\nERROR: {s} mismatch!")
            print("Expected:", subjects_data[s], "Got:", count[s])
            return

    # ---------------------------------------------------
    # DISPLAY
    # ---------------------------------------------------

    print("\n")
    print("=" * 80)
    print(f"{class_name} TIMETABLE (FINAL RULE BASED)")
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

for class_name in class_names:
    generate_timetable(class_name, periods_per_day)
    print("\nSUCCESS: Timetable generated!")
