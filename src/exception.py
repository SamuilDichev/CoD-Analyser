class CoDTrackerApiException(Exception):
	"""Raised when my.callofduty.com returns a 200 with an error"""
	pass

class CallOfDutyApiException(Exception):
	"""Raised when cod.tracker.gg returns an error"""
	pass