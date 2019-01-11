class YeetException(Exception):
	pass

from LibMedium.Medium import RemoteCallException

ERROR_MAP = {
	1: YeetException
}


def throw(error: RemoteCallException):
	if(error.error_no in ERROR_MAP):
		raise ERROR_MAP[error.error_no](str(error))
	raise(error)

