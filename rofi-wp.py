#!/bin/env python
import logging

import rofi_menu

"""
TODO: Change screen with tab or shift-tab
"""

class MarkAsVSFWItem(rofi_menu.Item):
    async def load(self, meta):
        """ TODO: Get current wallpaper and see if its marked """

    async def on_select(self, meta):
        logging.debug("Selected")

        return await super().on_select(meta)

    async def render(self, meta):
        """ TODO: Show mark/unmark depending on if its marked """
        return "Mark as vsfw"

class MainMenu(rofi_menu.Menu):
    prompt = "wallpapers"
    items = [
        MarkAsVSFWItem(),
    ]


if __name__ == "__main__":
    rofi_menu.run(MainMenu())
