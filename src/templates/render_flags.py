import attr


@attr.dataclass(frozen=True)
class RescueRenderFlags:
    """
    Flags that control how a rescue is rendered.
    """

    filter_active_rescues: bool = False
    filter_inactive_rescues: bool = False
    filter_unassigned_rescues: bool = False
    show_system_names: bool = False
    show_assigned_rats: bool = False
    show_unidentified_rats: bool = False
    show_uuids: bool = False
    show_quotes: bool = False
    hide_colors: bool = False
    show_help_message: bool = False
    unused_flags: str = ""

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
        unused_flags = argument.lstrip("-")

        # Only show active (a) or inactive (i) rescues
        filter_active_rescues = "a" in argument and "i" not in argument
        filter_inactive_rescues = "i" in argument and "a" not in argument
        unused_flags = unused_flags.replace('a', '')
        unused_flags = unused_flags.replace('i', '')

        # Show assigned rats per rescue
        show_assigned_rats = "r" in argument
        unused_flags = unused_flags.replace('r', '')

        # Only show rescues without assigned rats
        filter_unassigned_rescues = "u" in argument
        unused_flags = unused_flags.replace('u', '')

        # Show system names in the list
        show_system_names = "s" in argument
        unused_flags = unused_flags.replace('s', '')

        # Show API UUIDs
        show_uuids = "@" in argument
        unused_flags = unused_flags.replace('@', '')

        # Show unidentified rats
        show_unidentified = "d" in argument
        unused_flags = unused_flags.replace('d', '')

        # Hide colors and markup from the output
        hide_colors = "c" in argument
        unused_flags = unused_flags.replace('c', '')

        # Show the help message for correct usage
        show_help_message = "h" in argument
        unused_flags = unused_flags.replace('h', '')

        return cls(
            show_unidentified_rats=show_unidentified,
            filter_unassigned_rescues=filter_unassigned_rescues,
            show_assigned_rats=show_assigned_rats,
            filter_active_rescues=filter_active_rescues,
            filter_inactive_rescues=filter_inactive_rescues,
            show_system_names=show_system_names,
            show_uuids=show_uuids,
            hide_colors=hide_colors,
            show_help_message=show_help_message,
            unused_flags=unused_flags,
        )
