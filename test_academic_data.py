from academic_data import (
    get_department,
    get_all_lecturers,
    get_course_codes
)

print("ACCOUNTING:", len(get_department("ACCOUNTING")))
print("CIS:", len(get_department("COMPUTER_AND_INFORMATION_SCIENCES")))
print("ALL LECTURERS:", len(get_all_lecturers()))