import attr


@attr.dataclass(frozen=True)
class RescueRenderFlags:
    """
    Flags that control how a rescue is rendered.
    """

    show_inactive: bool = False
    filter_unassigned_rescues: bool = False
    show_assigned_rats: bool = False
    show_unidentified_rats: bool = False
    show_uuids: bool = False
    show_quotes: bool = False

    @classmethod
    def from_word(cls, argument: str):
        """
        construct an object from a given argument word

        Args:
            argument(str): flags word

        Returns:
            ListFlags instance
        """
        argument = argument.casefold()

        show_inactive = "i" in argument
        """
        Show inactive rescues
        """
        show_assigned_rats = "r" in argument
        """
        Show assigned rats per rescue
        """
        filter_unassigned_rescues = "u" in argument
        """
        only show rescues without assigned rats
        """
        show_uuids = "@" in argument
        """
        show API UUIDs
        """
        show_unidentified = "d" in argument

        return cls(
            show_unidentified_rats=show_unidentified,
            filter_unassigned_rescues=filter_unassigned_rescues,
            show_assigned_rats=show_assigned_rats,
            show_inactive=show_inactive,
            show_uuids=show_uuids,
        )
