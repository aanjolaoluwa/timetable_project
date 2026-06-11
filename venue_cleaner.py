import pandas as pd
import re


def clean_venue(name):

    # =====================================
    # HANDLE EMPTY VALUES
    # =====================================

    if pd.isna(name):
        return "UNKNOWN"

    # =====================================
    # BASIC CLEANING
    # =====================================

    name = str(name).upper().strip()

    # Replace separators
    name = (
        name
        .replace(",", " ")
        .replace("_", " ")
        .replace("-", " ")
    )

    # Remove duplicate spaces
    name = " ".join(name.split())

    # =====================================
    # REMOVE BUILDING PREFIXES
    # =====================================

    prefixes = [

        "CST ",
        "CST, ",

        "CLDS/CMSS ",
        "CLDS/CMSS, ",

        "CLDS/ CMSS ",

        "CMSS ",

    ]

    for prefix in prefixes:

        if name.startswith(prefix):

            name = name.replace(
                prefix,
                "",
                1
            )

    # =====================================
    # STANDARDIZE HALLS
    # =====================================

    hall_match = re.search(
        r"HALL\s*(\d+)",
        name
    )

    if hall_match:

        hall_number = hall_match.group(1)

        # ---------------------------------
        # SPECIAL CHEM LABS
        # ---------------------------------

        if hall_number == "111":
            return "CHEM LAB (HALL111)"

        if hall_number == "112":
            return "CHEMLAB(HALL 112)"

        if hall_number == "113":
            return "CHEM LAB (HALL113)"

        # ---------------------------------
        # SPECIAL PHY LABS
        # ---------------------------------

        if hall_number == "105":
            return "HALL105(PHY LAB)"

        if hall_number == "213":
            return "HALL213(PHY LAB)"

        if hall_number == "302":
            return "HALL302(PHY LAB)"

        # ---------------------------------
        # PHYSICS LABS
        # ---------------------------------

        if "PHY" in name or "PHYSICS" in name:

            return f"HALL{hall_number}(PHY LAB)"

        # ---------------------------------
        # CHEMISTRY LABS
        # ---------------------------------

        if "CHEM" in name:

            return f"CHEM LAB (HALL{hall_number})"

        # ---------------------------------
        # MCB LAB
        # ---------------------------------

        if "MCB" in name:

            return "MCB LAB(HALL 212)"

        # ---------------------------------
        # NORMAL HALLS
        # ---------------------------------

        return f"HALL{hall_number}"

    # =====================================
    # STUDIOS
    # =====================================

    studio_match = re.search(
        r"STUDIO\s*(\d+)",
        name
    )

    if studio_match:

        studio_number = studio_match.group(1)

        return f"STUDIO {studio_number}"

    # =====================================
    # STANDARD REPLACEMENTS
    # =====================================

    name = name.replace(
        "CENTER CLASS",
        "CENTRE CLASS"
    )

    replacements = {

        # =================================
        # LABS
        # =================================

        "BIO LAB": "BIOLAB",

        "ARGUS LAB": "COMPUTER LAB",

        "COMPUTER LAB": "COMPUTER LAB",

        "LANG LAB": "LANG LAB",

        "PSY LAB": "PSY LAB",

        "BCH LAB": "BCH LAB",

        # =================================
        # MASS COMM
        # =================================

        "MASS COMM STUDIO": "MASS COMM STUDIO",

        "MASSCOMM STUDIO": "MASSCOM STUDIO",

        "MASSCOM STUDIO": "MASSCOM STUDIO",

        "MASSCOM NEWSROOM": "MASSCOM NEWSROOM",

        # =================================
        # SEMINAR
        # =================================

        "SEMINAR ROOM": "CENTRE CLASS",

        "SEMINAR RM": "CENTRE CLASS",

        "CST SEMINAR ROOM": "CENTRE CLASS",

        # =================================
        # SQL
        # =================================

        "SQL(NEW HORIZON)": "SQL NEW HORIZON",

        "CST SQL(NEW HORIZON)": "SQL NEW HORIZON",

        # =================================
        # CEDS
        # =================================

        "CEDS MKT LAB": "CEDS/MKT LAB",

        "CLDS/CMSS MKT LAB": "CEDS/MKT LAB",

        # =================================
        # ENGINEERING
        # =================================

        "CHE CENTER CLASS": "CENTRE CLASS CHE",

        "CHE CENTRE CLASS": "CENTRE CLASS CHE",

        "CHEMICAL ENGINEERING BUILDING CENTRE CLASS":
            "CENTRE CLASS CHE",

        "CHEMICAL ENGINEERING BUILDING 300LV":
            "CHE 300LH",

        "CHEMICAL ENGINEERING BUILDING 400LV":
            "CHE 400LH",

        "CHEMICAL ENGINEERING BUILDING 500LV":
            "CHE 500LH",

        "CHEMICAL ENGINEERING BUILDING LAB":
            "LAB",

        # =================================
        # EIE
        # =================================

        "EIE CEN500LH": "CEN500LH",

        "EIE EIE500LH": "EIE500LH",

        "EIE ICE500LH": "ICE500LH",

        "EIE 500LH": "EIE500LH",

        "ICE 500LH": "ICE500LH",

        "EIE ICE 500LH": "ICE500LH",

        "EIE LAB": "EIE LAB",

        "EIE LARGELH": "LARGELH",

        # =================================
        # MCE
        # =================================

        "MCE FLUID LAB": "FLUID LAB",

        "MCE LAB": "MCE WORKSHOP",

        "MCE LA": "MCE WORKSHOP",

        "MCE WORKSHOP": "MCE WORKSHOP",

        # =================================
        # WORKSHOP
        # =================================

        "WORKSHOP": "WORKSHOP",

        # =================================
        # ENGINEERING HALLS
        # =================================

        "CHE 200LH": "CHE 200LH",
        "CHE 300LH": "CHE 300LH",
        "CHE 400LH": "CHE 400LH",
        "CHE 500LH": "CHE 500LH",

        "CVE 200LH": "CVE 200LH",
        "CVE 300LH": "CVE 300LH",
        "CVE 400LH": "CVE 400LH",
        "CVE 500LH": "CVE 500LH",

        "MCE 300LH": "MCE 300LH",
        "MCE 400LH": "MCE 400LH",
        "MCE 500LH": "MCE 500LH",

        "PTE 300LH": "PTE 300LH",
        "PTE 500LH": "PTE 500LH",

        "PET 300LH": "PET 300LH",

        # =================================
        # REMAINING LABS / HALLS
        # =================================

        "CHEM LAB (HALL112)": "CHEMLAB(HALL 112)",

        "HALL112": "CHEMLAB(HALL 112)",

        "HALL313": "HALL307",

        # =================================
        # FINAL UNKNOWN FIXES
        # =================================

        "HALL313": "HALL307",

        "STUDIO 500": "STUDIO 400",

        "STUDIO 22": "STUDIO 200",

        "PSY LAB": "PSY LAB",

        "MASSCOM NEWSROOM": "MASSCOM NEWSROOM",

        "MCE WORKSHOP": "WORKSHOP",

        "UNKNOWN": "UNKNOWN",


        # =================================
        # CMSS / GENERAL ROOMS
        # =================================

        "(H301)": "H301",

        "F301/G201": "F301",

        "CLDS/CMSSE401B": "E401B",

        # =================================
        # STUDIO
        # =================================

        "STUDIO 500": "STUDIO 400",

        "STUDIO 22": "STUDIO 200",

        # =================================
        # NAN
        # =================================

        "NAN": "UNKNOWN"

    }

    # =====================================
    # FINAL CLEANING
    # =====================================

    name = name.strip()

    name = " ".join(name.split())

    return replacements.get(name, name)