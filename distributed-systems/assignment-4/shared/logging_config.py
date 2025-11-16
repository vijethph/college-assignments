"""Shared Logging Configuration."""

import structlog


def configure_logging(service_name: str) -> None:
    """
    Configure structured logging for a service.

    :param service_name: Name of the service
    :type service_name: str
    """
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(min_level=20),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(service=service_name)


def get_logger():
    """
    Get a structured logger instance.

    :return: Logger instance
    :rtype: structlog.BoundLogger
    """
    return structlog.get_logger()
