def get_experience_score(driver_profile):
    """
    Placeholder.

    Experience should come from verified
    driving experience, hours, years,
    or another approved external source.
    """

    value = driver_profile.get(
        "experience_score"
    )

    return value


def get_health_score(driver_profile):
    """
    Placeholder.

    Do not infer health from EAR/PERCLOS.
    Health/fitness is a separate profile input.
    """

    value = driver_profile.get(
        "health_score"
    )

    return value