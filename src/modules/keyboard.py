#!/usr/bin/python3
"""
Fixes Hardcoded tray icons in Linux.

Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : Andreas Angerer, Joshua Fogg
Version : 3.8
Website : https://github.com/bil-elmoussaoui/Hardcode-Tray
Licence : The script is released under GPL, uses a modified script
     form Chromium project released under BSD license
This file is part of Hardcode-Tray.
Hardcode-Tray is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
Hardcode-Tray is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with Hardcode-Tray. If not, see <http://www.gnu.org/licenses/>.
"""


class KeyboardInput:
    """Make the interaction between Hardcode-Tray & keyboard easier."""
    QUIT_ACTIONS = ["q", "quit", "exit"]

    def __init__(self):
        self._choices = []

    @property
    def choices(self):
        """Choices to choose from."""
        return self._choices

    @choices.setter
    def choices(self, choices):
        """Choices to choose from."""
        self._choices = choices

    def select(self, message):
        """Ask the user to select one of the possible choices."""
        have_chosen = False
        stopped = False
        self._display_choices()
        while not have_chosen and not stopped:
            try:
                selected = input(message).strip().lower()
                if selected in KeyboardInput.QUIT_ACTIONS:
                    stopped = True
                selected = int(selected)
                if 1 <= selected <= len(self.choices):
                    have_chosen = True
                    return selected
            except ValueError:
                print("Please choose a valid value")
            except KeyboardInterrupt:
                exit("\n")
        return None

    def _display_choices(self):
        """Show the different choices."""
        i = 1
        for choice in self.choices:
            print("{0}) {1}".format(str(i), choice))
            i += 1
        print("(Q)uit to cancel")
