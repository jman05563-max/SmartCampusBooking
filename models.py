class User:
    """Base class for all system users."""

    def __init__(self, full_name, username, password):
        self.__full_name = full_name
        self.__username = username
        self.__password = password

    def get_full_name(self):
        return self.__full_name

    def get_username(self):
        return self.__username

    def check_password(self, password):
        return self.__password == password


class Lecturer(User):
    """Represents a lecturer who can book campus resources."""

    def __init__(self, full_name, username, password):
        super().__init__(full_name, username, password)
        self.role = "Lecturer"


class CampusAdministrator(User):
    """Represents an administrator who manages campus resources."""

    def __init__(self, full_name, username, password):
        super().__init__(full_name, username, password)
        self.role = "Campus Administrator"


class SystemOperator(User):
    """Represents an operator with system-wide access."""

    def __init__(self, full_name, username, password):
        super().__init__(full_name, username, password)
        self.role = "System Operator"


class Campus:
    """Represents a campus and its booking policy."""

    def __init__(self, name, max_duration, opening_time, closing_time):
        self.name = name
        self.max_duration = max_duration
        self.opening_time = opening_time
        self.closing_time = closing_time


class Resource:
    """Represents a bookable campus resource."""

    def __init__(self, resource_name, resource_type, campus_id):
        self.resource_name = resource_name
        self.resource_type = resource_type
        self.campus_id = campus_id


class Booking:
    """Represents a resource booking."""

    def __init__(
        self,
        user_id,
        resource_id,
        campus_id,
        booking_date,
        start_time,
        duration
    ):
        self.user_id = user_id
        self.resource_id = resource_id
        self.campus_id = campus_id
        self.booking_date = booking_date
        self.start_time = start_time
        self.duration = duration
        self.status = "Active"