"""
Sheet formatting and styling operations.

This module contains the SheetFormatter class responsible for
creating formatting requests for Google Sheets based on update results.
"""


from ..config.constants import (
    COL_AA,
    COL_AB,
    COL_AC,
    COL_AD,
    COL_AE,
    COL_AG,
    COL_E,
    COL_F,
    COL_G,
    COL_H,
    COL_I,
    COL_J,
    COL_K,
    COL_L,
    COL_N,
    COL_O,
    COL_P,
    COL_Q,
    COL_R,
    COL_S,
    COL_V,
    COL_W,
    COL_Y,
    COL_Z,
    COLOR_BLACK,
    COLOR_BLUE,
    COLOR_DARK_CORNFLOWER_BLUE_2,
    COLOR_DARK_GREEN_2,
    COLOR_DARK_PURPLE_2,
    COLOR_DARK_RED_2,
    COLOR_GRAY,
    COLOR_GREEN,
    COLOR_LIGHT_CYAN_3,
    COLOR_LIGHT_GREEN_3,
    COLOR_LIGHT_MAGENTA_2,
    COLOR_LIGHT_RED_1,
    COLOR_LIGHT_YELLOW_2,
    COLOR_NOAH_FILL,
    COLOR_RED,
    COLOR_WHITE,
    LAST_STOCK_CHECK_COL,
    PRICE_COL,
    PRODUCT_ID_COL,
    VA_NOTES_COL,
)
from ..scraping_utils import create_color_request
from ..utils.sheets import create_text_format_request
from .data_models import PriceUpdateResult


class SheetFormatter:
    """Handles Google Sheets formatting and color application."""

    def __init__(self):
        pass

    def create_formatting_requests(self, row_index: int, row: list[str],
                                 update_result: PriceUpdateResult) -> list[dict]:
        """
        Create formatting requests for a row based on update results.

        Args:
            row_index: Zero-based row index
            row: Row data from the sheet
            update_result: Results from product processing

        Returns:
            List of formatting requests for the Google Sheets API
        """
        requests = []

        if update_result.all_blocked:
            # Blocked: don't change row colors, only format VA Notes (Column A)
            requests.append(
                create_color_request(
                    row_index, COLOR_BLUE, col_index=VA_NOTES_COL, text_color=COLOR_WHITE
                )
            )
        elif update_result.best_supplier_url is not None and update_result.best_supplier_in_stock:
            # Item is available and in stock: apply full formatting
            requests.extend(self._create_available_item_formatting(row_index, row, update_result))
        else:
            # Item is unavailable or out of stock: apply out-of-stock formatting
            if not update_result.all_blocked:
                requests.extend(self._create_out_of_stock_formatting(row_index, row, update_result))

        # Column A (VA Notes) formatting for non-blocked items
        if update_result.new_va_note and update_result.new_va_note.strip() and update_result.new_va_note != "Blocked":
            requests.append(
                create_color_request(
                    row_index, COLOR_BLUE, col_index=VA_NOTES_COL, text_color=COLOR_WHITE
                )
            )

        return requests

    def _create_available_item_formatting(self, row_index: int, row: list[str],
                                        update_result: PriceUpdateResult) -> list[dict]:
        """Create formatting requests for available items."""
        requests = []

        # Entire row white background
        requests.append(create_color_request(row_index, COLOR_WHITE))

        # Default formatting for specific columns
        requests.extend([
            create_color_request(row_index, COLOR_BLACK, col_index=COL_AG, text_color=COLOR_BLACK),  # AG: always black text and black fill
            create_color_request(row_index, COLOR_BLUE, col_index=COL_AB, text_color=COLOR_WHITE),
            create_color_request(row_index, COLOR_GREEN, col_index=COL_AE, text_color=COLOR_BLACK)
        ])

        # Apply special formatting if price is less than $299.99
        if update_result.new_price < 299.99:
            requests.extend(self._create_under_299_formatting(row_index, row))

        return requests

    def _create_under_299_formatting(self, row_index: int, row: list[str]) -> list[dict]:
        """Create formatting for items under $299.99."""
        requests = []

        # Price column formatting
        requests.append(
            create_color_request(
                row_index, COLOR_LIGHT_GREEN_3, col_index=PRICE_COL, text_color=COLOR_DARK_RED_2
            )
        )

        # Other column formatting
        requests.extend([
            create_color_request(row_index, COLOR_LIGHT_MAGENTA_2, col_index=COL_Y, text_color=COLOR_BLACK),
            create_color_request(row_index, COLOR_LIGHT_YELLOW_2, col_index=COL_Z, text_color=COLOR_LIGHT_YELLOW_2),
            create_color_request(row_index, COLOR_LIGHT_RED_1, col_index=COL_AA, text_color=COLOR_BLACK),
            create_color_request(row_index, COLOR_BLUE, col_index=COL_AB, text_color=COLOR_BLACK),
            create_color_request(row_index, COLOR_DARK_GREEN_2, col_index=COL_AC, text_color=COLOR_BLACK),
            create_color_request(row_index, COLOR_DARK_GREEN_2, col_index=COL_AD, text_color=COLOR_BLACK)
        ])

        # Column E (RNW) formatting
        col_e_value = row[COL_E] if len(row) > COL_E else ""
        if col_e_value.strip().upper() == "RNW":
            requests.append(
                create_color_request(row_index, COLOR_RED, col_index=COL_E, text_color=COLOR_BLACK)
            )
        else:
            requests.append(
                create_color_request(row_index, COLOR_LIGHT_CYAN_3, col_index=COL_E, text_color=COLOR_BLACK)
            )

        # Gray formatting for columns F-K
        for col_index in [COL_F, COL_G, COL_H, COL_I, COL_J, COL_K]:
            requests.append(
                create_color_request(row_index, COLOR_GRAY, col_index=col_index, text_color=COLOR_GRAY)
            )

        # Column L formatting
        requests.append(
            create_color_request(row_index, COLOR_DARK_GREEN_2, col_index=COL_L, text_color=COLOR_WHITE)
        )

        # Noah supplier highlighting
        requests.extend(self._create_noah_formatting(row_index, row))

        # Standard text color formatting for various columns
        requests.extend(self._create_standard_text_formatting(row_index))

        return requests

    def _create_noah_formatting(self, row_index: int, row: list[str]) -> list[dict]:
        """Create Noah supplier highlighting formatting."""
        requests = []

        # Column N formatting
        col_n_value = row[COL_N] if len(row) > COL_N else ""
        if "noah" in col_n_value.lower() if col_n_value else False:
            requests.append(
                create_color_request(
                    row_index, COLOR_NOAH_FILL, col_index=COL_N, text_color=COLOR_DARK_PURPLE_2
                )
            )
        else:
            requests.append(
                create_color_request(row_index, text_color=COLOR_BLACK, col_index=COL_N)
            )

        # Column O formatting
        col_o_value = row[COL_O] if len(row) > COL_O else ""
        if "noah" in col_o_value.lower() if col_o_value else False:
            requests.append(
                create_color_request(
                    row_index, COLOR_NOAH_FILL, col_index=COL_O, text_color=COLOR_DARK_PURPLE_2
                )
            )
        else:
            requests.append(
                create_color_request(row_index, text_color=COLOR_BLACK, col_index=COL_O)
            )

        return requests

    def _create_standard_text_formatting(self, row_index: int) -> list[dict]:
        """Create standard text color formatting for various columns."""
        requests = [
            create_color_request(row_index, text_color=COLOR_BLACK, col_index=LAST_STOCK_CHECK_COL),
            create_text_format_request(row_index, LAST_STOCK_CHECK_COL),  # Format date column as TEXT
            create_color_request(row_index, text_color=COLOR_BLACK, col_index=COL_P),
            create_color_request(row_index, text_color=COLOR_BLACK, col_index=COL_R),
            create_color_request(row_index, text_color=COLOR_BLACK, col_index=COL_S),
            create_color_request(row_index, text_color=COLOR_BLACK, col_index=COL_V),
            create_color_request(row_index, text_color=COLOR_BLACK, col_index=COL_W),
            create_color_request(row_index, text_color=COLOR_WHITE, col_index=COL_AA),
            create_color_request(row_index, text_color=COLOR_WHITE, col_index=COL_AB),
            create_color_request(row_index, text_color=COLOR_WHITE, col_index=COL_AC),
            create_color_request(row_index, text_color=COLOR_WHITE, col_index=COL_AD),
            create_color_request(row_index, text_color=COLOR_DARK_CORNFLOWER_BLUE_2, col_index=PRODUCT_ID_COL),
            create_color_request(row_index, COLOR_BLACK, col_index=COL_AG, text_color=COLOR_BLACK),  # AG: always black text
            # Supplier columns (AH-AN)
            create_color_request(row_index, text_color=COLOR_DARK_CORNFLOWER_BLUE_2, col_index=33),  # AH
            create_color_request(row_index, text_color=COLOR_DARK_CORNFLOWER_BLUE_2, col_index=34),  # AI
            create_color_request(row_index, text_color=COLOR_DARK_CORNFLOWER_BLUE_2, col_index=35),  # AJ
            create_color_request(row_index, text_color=COLOR_DARK_CORNFLOWER_BLUE_2, col_index=36),  # AK
            create_color_request(row_index, text_color=COLOR_DARK_CORNFLOWER_BLUE_2, col_index=37),  # AL
            create_color_request(row_index, text_color=COLOR_DARK_CORNFLOWER_BLUE_2, col_index=38),  # AM
            create_color_request(row_index, text_color=COLOR_DARK_CORNFLOWER_BLUE_2, col_index=39),  # AN
            create_color_request(row_index, text_color=COLOR_BLACK, col_index=COL_Q),
            create_color_request(row_index, COLOR_LIGHT_MAGENTA_2, col_index=COL_Y)
        ]
        return requests

    def _create_out_of_stock_formatting(self, row_index: int, row: list[str],
                                       update_result: PriceUpdateResult) -> list[dict]:
        """Create formatting requests for out-of-stock/unavailable items."""
        requests = []

        # Entire row red background with white text
        requests.append(create_color_request(row_index, COLOR_RED, text_color=COLOR_WHITE))

        # Columns F, G, H, I, J, K: Red text color (per requirements)
        for col_index in [COL_F, COL_G, COL_H, COL_I, COL_J, COL_K]:
            requests.append(
                create_color_request(row_index, text_color=COLOR_RED, col_index=col_index)
            )

        # Column AG: Always black text and black fill (per requirements)
        requests.append(
            create_color_request(row_index, COLOR_BLACK, col_index=COL_AG, text_color=COLOR_BLACK)
        )

        return requests
