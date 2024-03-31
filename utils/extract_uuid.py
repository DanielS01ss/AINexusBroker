def extract_uuid_for_model(input_string):
    # Split the string on the underscore character
    parts = input_string.split("_")
    # Return the first part, which is the UUID
    return parts[0]