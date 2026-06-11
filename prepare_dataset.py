def clean_level(level):
    if pd.isna(level):
        return 100

    level_str = str(level).strip().replace(" ", "")
    
    # Handle composites like "400&300" or "400/200"
    for separator in ["/", "&"]:
        if separator in level_str:
            level_str = level_str.split(separator)[0]
            
    try:
        val = int(level_str)
        # Handle outliers like "4400" -> "400"
        if val > 600:
            val = int(str(val)[0] + "00")
        return val
    except ValueError:
        return 100