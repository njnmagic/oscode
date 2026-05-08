import random


DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

# FIX 2: renamed for clarity
PERIODS_PER_DAY = int(
    input("Enter periods per day: ")
)

# ---------------------------------------------------
# USER input
# ---------------------------------------------------

num_classes = int(input("Enter number of classes: "))

class_names = []

for i in range(num_classes):
    class_name = input(f"Enter class {i+1} name: ")
    class_names.append(class_name)

# ---------------------------------------------------
# SUBJECTS
# ---------------------------------------------------

num_subjects = int(input("\nEnter number of subjects: "))

subjects_data = {}
subject_teachers = {}

special_subjects = {}

for i in range(num_subjects):

    subject = input(f"\nEnter subject {i+1} name: ")

    weekly_periods = int(
        input(f"Weekly periods for {subject}: ")
    )

    subjects_data[subject] = weekly_periods

    teachers = input(
        f"Teachers for {subject} (comma separated): "
    ).split(",")

    teachers = [t.strip() for t in teachers]

    subject_teachers[subject] = teachers

    consecutive = int(
        input(
            f"Consecutive periods needed for {subject} (1/2/3): "
        )
    )

    special_subjects[subject] = consecutive

# ---------------------------------------------------
# TEACHER SCHEDULE
# ---------------------------------------------------

teacher_schedule = {}

for teachers in subject_teachers.values():

    for teacher in teachers:

        if teacher not in teacher_schedule:

            teacher_schedule[teacher] = {}

            for day in DAYS:

                teacher_schedule[teacher][day] = (
                    [False] * PERIODS_PER_DAY
                )

# ---------------------------------------------------
# DAILY DISTRIBUTION
# ---------------------------------------------------

def calculate_daily_periods(total_periods):

    base = total_periods // len(DAYS)
    extra = total_periods % len(DAYS)

    distribution = {}

    for i, day in enumerate(DAYS):

        distribution[day] = base

        if i < extra:
            distribution[day] += 1

    return distribution

# ---------------------------------------------------
# AVAILABLE TEACHER
# ---------------------------------------------------

def get_available_teacher(subject, day, start, length):

    for teacher in subject_teachers[subject]:

        free = True

        for p in range(start, start + length):

            if teacher_schedule[teacher][day][p]:
                free = False
                break

        if free:
            return teacher

    return None

# ---------------------------------------------------
# GENERATE TIMETABLE
# ---------------------------------------------------

def generate_timetable(class_name):

    # FIX 1: corrected .cost() → copy()
    remaining = subjects_data.copy()

    total_periods = sum(remaining.values())

    day_periods = calculate_daily_periods(total_periods)

    timetable = {}
    teacher_map = {}

    special_used = {}

    for subject in subjects_data:
        special_used[subject] = False

    for day in DAYS:

        timetable[day] = [""] * day_periods[day]
        teacher_map[day] = [""] * day_periods[day]

    for day in DAYS:

        period = 0

        while period < day_periods[day]:

            assigned = False

            subjects = list(remaining.keys())

            random.shuffle(subjects)

            for subject in subjects:

                if remaining[subject] <= 0:
                    continue

                block_size = special_subjects[subject]

                # SPECIAL BLOCK
                if (
                    block_size > 1
                    and not special_used[subject]
                    and remaining[subject] >= block_size
                    and period + block_size <= day_periods[day]
                ):

                    teacher = get_available_teacher(
                        subject,
                        day,
                        period,
                        block_size
                    )

                    if teacher:

                        for p in range(period, period + block_size):

                            timetable[day][p] = subject
                            teacher_map[day][p] = teacher

                            teacher_schedule[teacher][day][p] = True

                        remaining[subject] -= block_size

                        special_used[subject] = True

                        period += block_size

                        assigned = True

                        break

                # SINGLE PERIOD
                teacher = get_available_teacher(
                    subject,
                    day,
                    period,
                    1
                )

                if teacher:

                    timetable[day][period] = subject
                    teacher_map[day][period] = teacher

                    teacher_schedule[teacher][day][period] = True

                    remaining[subject] -= 1

                    period += 1

                    assigned = True

                    break

            # FALLBACK
            if not assigned:

                timetable[day][period] = "Study Hour"
                teacher_map[day][period] = "Supervisor"

                period += 1

    return timetable, teacher_map, day_periods

# ---------------------------------------------------
# DISPLAY
# ---------------------------------------------------

def display_timetable(
    class_name,
    timetable,
    teacher_map,
    day_periods
):

    print("\n")
    print("=" * 80)
    print(f"{class_name} TIMETABLE")
    print("=" * 80)

    for day in DAYS:

        print(f"\n{day}")
        print("-" * 60)

        for p in range(day_periods[day]):

            subject = timetable[day][p]
            teacher = teacher_map[day][p]

            print(
                f"Period {p+1}: {subject} ({teacher})"
            )

# ---------------------------------------------------
# MAIN
# ---------------------------------------------------

for class_name in class_names:

    timetable, teacher_map, day_periods = (
        generate_timetable(class_name)
    )

    display_timetable(
        class_name,
        timetable,
        teacher_map,
        day_periods
    )

    print("\nSUCCESS: Timetable generated!")
