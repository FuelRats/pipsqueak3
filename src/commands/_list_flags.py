from dataclasses import dataclass


@dataclass(frozen=True)
class ListFlags:
    """
    Flags used by the !list command, includes a parser.
    """

    filter_active_rescues: bool = False
    filter_inactive_rescues: bool = False
    filter_unassigned_rescues: bool = False
    show_system_names: bool = False
    show_assigned_rats: bool = False
    show_uuids: bool = False
    hide_colors: bool = False

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

        filter_active_rescues = "a" in argument and not "i" in argument
        """
        Only show active rescues
        """
        filter_inactive_rescues = "i" in argument and not "a" in argument
        """
        Only show inactive rescues
        """
        show_assigned_rats = "r" in argument
        """
        Show assigned rats per rescue
        """
        filter_unassigned_rescues = "u" in argument
        """
        Only show rescues without assigned rats
        """
        show_system_names = "s" in argument
        """
        Show system names in the list
        """
        show_uuids = "@" in argument
        """
        Show API UUIDs
        """
        hide_colors = "c" in argument

        return cls(
            filter_active_rescues,
            filter_inactive_rescues,
            filter_unassigned_rescues,
            show_system_names,
            show_assigned_rats,
            show_uuids,
            hide_colors,
        )
