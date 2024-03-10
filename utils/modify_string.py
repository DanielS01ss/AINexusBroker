

def modify_string(input_string, replacement="_metadata.json"):
    parts = input_string.split('_', 1)
    if len(parts) > 1:
        modified_string = parts[0] + replacement 
        return modified_string
    else:
        return input_string
