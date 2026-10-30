class Comment:

    def __init__(
        self,
        id: int,
        body: str,
        timestamp: str,
    ):
        self.id = id
        self.body = body
        self.timestamp = timestamp

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'body': self.body,
            'timestamp': self.timestamp,
        }
