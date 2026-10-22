class BookingRule:
    """Base class for campus booking rules."""

    def __init__(self, campus_name, max_duration, opening_time, closing_time):
        self.campus_name = campus_name
        self.max_duration = max_duration
        self.opening_time = opening_time
        self.closing_time = closing_time

    def is_duration_valid(self, duration):
        return duration <= self.max_duration

    def is_time_valid(self, start_time):
        return self.opening_time <= start_time < self.closing_time

    def get_policy(self):
        return (
            f"{self.campus_name}: Maximum booking duration = "
            f"{self.max_duration} hours, "
            f"Booking hours = {self.opening_time} - {self.closing_time}"
        )


class PretoriaBookingRule(BookingRule):
    def __init__(self):
        super().__init__(
            "Richfield Pretoria Campus",
            2,
            "08:00",
            "17:00"
        )


class NewTownBookingRule(BookingRule):
    def __init__(self):
        super().__init__(
            "Richfield NewTown Campus",
            3,
            "07:00",
            "18:00"
        )


class CenturionBookingRule(BookingRule):
    def __init__(self):
        super().__init__(
            "Richfield Centurion Campus",
            1,
            "09:00",
            "16:00"
        )


def get_booking_rule(campus_name):
    """Return the appropriate booking rule for a campus."""

    rules = {
        "Richfield Pretoria Campus": PretoriaBookingRule(),
        "Richfield NewTown Campus": NewTownBookingRule(),
        "Richfield Centurion Campus": CenturionBookingRule()
    }

    return rules.get(campus_name)