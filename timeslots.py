# =========================================================
# COVENANT UNIVERSITY TIMESLOTS
# =========================================================

def create_timeslots():

    timetable = {}

    # =====================================================
    # NORMAL DAYS
    # =====================================================

    normal_hours = [

        "8-9",
        "9-10",
        "10-11",
        "11-12",
        "12-1",
        "1-2",

        # 2-3 BREAK

        "3-4",
        "4-5",
        "5-6",
        "6-7"

    ]

    # =====================================================
    # FRIDAY HOURS
    # =====================================================

    friday_hours = [

        "8-9",
        "9-10",
        "10-11",
        "11-12",
        "12-1",
        "1-2"

    ]

    # =====================================================
    # MONDAY - THURSDAY
    # =====================================================

    for day in [

        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday"

    ]:

        timetable[day] = normal_hours.copy()

    # =====================================================
    # FRIDAY
    # =====================================================

    timetable["Friday"] = friday_hours.copy()

    return timetable


# =========================================================
# FLATTEN TIMESLOTS
# =========================================================

def flatten_timeslots():

    slots = []

    timetable = create_timeslots()

    for day, hours in timetable.items():

        for hour in hours:

            slots.append(
                f"{day}_{hour}"
            )

    return slots