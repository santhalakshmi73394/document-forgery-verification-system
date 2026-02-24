def classify(ela_score, extracted_text, metadata_flag=False):

    suspicious_keywords = [
        "edited",
        "modified",
        "fake",
        "unauthorized",
        "sample"
    ]

    # Text-based detection
    text_flag = any(word.lower() in extracted_text.lower() for word in suspicious_keywords)

    # Base risk score (0 to 1)
    risk_score = 0

    # ELA contribution (weight 50%)
    risk_score += ela_score * 0.5

    # Text contribution (weight 30%)
    if text_flag:
        risk_score += 0.3

    # Metadata contribution (weight 20%)
    if metadata_flag:
        risk_score += 0.2

    # Cap at 1
    risk_score = min(risk_score, 1)

    # Decision thresholds
    if risk_score >= 0.7:
        return "Fake", round(risk_score * 100)
    elif risk_score >= 0.4:
        return "Suspicious", round(risk_score * 100)
    else:
        confidence = round((1 - risk_score) * 100)
        return "Genuine", confidence