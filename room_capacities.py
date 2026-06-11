ROOM_CAPACITY = {

    # =====================================
    # MEGA LECTURE THEATRES
    # =====================================

    "LT1": 2500,
    "LT2": 1400,
    "LARGELH": 1000,

    # =====================================
    # CHAPEL / LIBRARY
    # =====================================

    "CHAPEL": 1200,
    "LIBRARY": 500,

    # =====================================
    # CEDS
    # =====================================

    "CEDS BUILDING": 200,
    "CEDS HALL": 150,
    "CEDS/MKT LAB": 120,
    "MKT LAB": 120,

    # =====================================
    # CLDS / CMSS GENERAL ROOMS
    # =====================================

    "A201": 220,

    "B301": 200,

    "C301": 220,
    "C401": 180,

    "E101": 250,
    "E201": 250,
    "E202": 250,
    "E301": 220,

    "E401A": 180,
    "E401B": 180,

    "F301": 220,
    "F401": 180,

    "G201": 220,
    "G301": 200,

    "H301": 220,
    "H401": 180,

    # =====================================
    # SPECIALIZED CMSS/CLDS SPACES
    # =====================================

    "LANG LAB": 120,
    "PSY LAB": 100,

    "COMPUTER LAB": 250,

    "MASS COMM STUDIO": 120,
    "MASSCOM STUDIO": 120,

    "MASSCOM NEWSROOM": 100,

    # =====================================
    # CST HALLS
    # =====================================

    "HALL107": 280,
    "HALL108": 240,

    "HALL201": 260,
    "HALL202": 260,
    "HALL203": 220,
    "HALL204": 200,

    "HALL306": 180,
    "HALL307": 180,
    "HALL308": 240,

    # =====================================
    # SCIENCE LABS
    # =====================================

    "BCH LAB": 180,
    "BIOLAB": 140,

    "CHEM LAB (HALL111)": 160,
    "CHEM LAB (HALL113)": 160,
    "CHEMLAB(HALL 112)": 150,

    "MCB LAB(HALL 212)": 180,

    "HALL105(PHY LAB)": 140,
    "HALL213(PHY LAB)": 130,
    "HALL302(PHY LAB)": 220,

    # =====================================
    # STUDIOS
    # =====================================

    "STUDIO 100": 280,
    "STUDIO 200": 240,
    "STUDIO 300": 180,
    "STUDIO 400": 120,

    # =====================================
    # ENGINEERING - CHE
    # =====================================

    "CHE 200LH": 250,
    "CHE 300LH": 220,
    "CHE 400LH": 180,
    "CHE 500LH": 150,

    "CENTRE CLASS CHE": 200,

    "CHEMICAL ENGINEERING BUILDING": 250,

    # =====================================
    # ENGINEERING - CVE
    # =====================================

    "CVE 200LH": 250,
    "CVE 300LH": 220,
    "CVE 400LH": 180,
    "CVE 500LH": 150,

    "CENTRE CLASS CVE": 200,

    # =====================================
    # ENGINEERING - EIE
    # =====================================

    "EIE500LH": 180,
    "CEN500LH": 180,
    "ICE500LH": 180,

    "EIE LAB": 120,

    # =====================================
    # ENGINEERING - MCE
    # =====================================

    "MCE 300LH": 220,
    "MCE 400LH": 180,
    "MCE 500LH": 150,

    "MCE WORKSHOP": 100,
    "FLUID LAB": 120,

    # =====================================
    # ENGINEERING - PTE / PET
    # =====================================

    "PTE 300LH": 220,
    "PTE 500LH": 150,

    "PET 300LH": 220,

    "WORKSHOP": 100,

    # =====================================
    # OTHER SPECIAL ROOMS
    # =====================================

    "LAB": 150,
    "LAB PTE": 120,
    "LAB LT1": 200,
    "LAB LT2": 200,

    "CENTRE CLASS": 180,

    "SQL NEW HORIZON": 180,

    "GBL": 180,
    "PSY LAB": 100,

    "MASSCOM NEWSROOM": 100,

    "WORKSHOP": 100,
    
    # =====================================
    # FALLBACK
    # =====================================

    "UNKNOWN": 100
}

ROOM_TYPE = {

    # GENERAL
    "A201": "GENERAL",
    "B301": "GENERAL",
    "C301": "GENERAL",

    # LABS
    "LANG LAB": "LAB",
    "PSY LAB": "LAB",
    "BCH LAB": "LAB",
    "MCB LAB(HALL 212)": "LAB",

    # COMPUTER
    "COMPUTER LAB": "COMPUTER",

    # STUDIO
    "MASS COMM STUDIO": "STUDIO",
    "STUDIO 100": "STUDIO",

    # WORKSHOP
    "MCE WORKSHOP": "WORKSHOP",

    # MEGA
    "LT1": "MEGA",
    "LT2": "MEGA",
    "CHAPEL": "MEGA"
}