from uuid import UUID


class RatBoard(object):
    """
    A rescue board
    """

    def __init__(self, handler=None):
        """
        Create a new Rescue Board.

        Args:
            handler ():
        """
        self.handler = handler
        # handler.my_board = self

    def from_api(self, api_id: UUID, create: bool = True, **kwargs) -> None:
        """
        Handles Rescue events from the API handler

        Args:
            api_id(UUID): API ID of modified rescue
            create(bool): Create a new case if it is not found
            **kwargs (dict):

        Returns:
            None
        """
        pass