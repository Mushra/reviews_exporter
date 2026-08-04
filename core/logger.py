from datetime import datetime



class Logger:


    listeners = []



    def __init__(
        self,
        name=None,
        enabled=True
    ):

        self.name = name

        self.enabled = enabled



    @classmethod
    def add_listener(
        cls,
        callback
    ):

        if callback not in cls.listeners:

            cls.listeners.append(
                callback
            )



    @classmethod
    def remove_listener(
        cls,
        callback
    ):

        if callback in cls.listeners:

            cls.listeners.remove(
                callback
            )



    def _write(
        self,
        level,
        message
    ):


        if not self.enabled:

            return



        timestamp = datetime.now().strftime(
            "%H:%M:%S"
        )


        formatted = (
            f"[{timestamp}] [{level}] {message}"
        )


        print(
            formatted
        )


        for listener in self.listeners:

            try:

                listener(
                    formatted
                )

            except Exception:

                pass




    def info(
        self,
        message
    ):

        self._write(
            "INFO",
            message
        )



    def warning(
        self,
        message
    ):

        self._write(
            "WARN",
            message
        )



    def error(
        self,
        message
    ):

        self._write(
            "ERROR",
            message
        )



    def success(
        self,
        message
    ):

        self._write(
            "OK",
            message
        )