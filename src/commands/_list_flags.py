from dataclasses import dataclass


@dataclass(frozen=True)
class ListFlags:
    """
    Flags used by the !list command, includes a parser.
    """

    show_inactive: bool = False
    filter_unassigned_rescues: bool = False
    show_assigned_rats: bool = False
    show_uuids: bool = False

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
        return cls(
            show_inactive, filter_unassigned_rescues, show_assigned_rats, show_uuids
        )
