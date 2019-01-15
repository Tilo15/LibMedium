from LibMedium.Medium import RemoteCallException

ERROR_MAP = {
}


def throw(error: RemoteCallException):
	if(error.error_no in ERROR_MAP):
		raise ERROR_MAP[error.error_no](str(error))
	raise(error)

REV_ERROR_MAP = {
}


