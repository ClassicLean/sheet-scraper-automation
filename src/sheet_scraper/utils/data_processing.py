"""
Data processing utilities for scraping results.

This module contains functions for processing and comparing
scraped data from multiple suppliers.
"""

from typing import List, Dict, Any, Tuple, Optional

from sheet_scraper.utils.logs_module import debug_print


def process_scraped_results(supplier_results: List[Dict[str, Any]]) -> Tuple[Optional[float], Optional[str], str, Optional[float]]:
    """
    Process scraped results from multiple suppliers to find the best option.

    Args:
        supplier_results: List of supplier result dictionaries containing:
            - name: Supplier name
            - url: Product URL
            - price: Product price (float or None)
            - in_stock: Stock status (bool)
            - shipping_fee: Shipping fee (float or None)

    Returns:
        Tuple containing:
        - base_price: Best base price (without shipping)
        - best_url: URL of the best supplier
        - supplier_name: Name of the best supplier
        - shipping_fee: Shipping fee for the best supplier
    """
    lowest_total_price_found = float("inf")
    best_supplier_url = None
    chosen_supplier_name = "N/A"
    chosen_shipping_fee = None

    for result in supplier_results:
        if result["in_stock"] and result["price"] is not None:
            # Calculate total price including shipping fee
            base_price = result["price"]
            shipping_fee = result.get("shipping_fee", 0) or 0  # Default to 0 if None
            total_price = base_price + shipping_fee

            debug_print(f"DEBUG: Comparing supplier {result['name']}: base_price=${base_price}, shipping=${shipping_fee}, total=${total_price}")

            if total_price < lowest_total_price_found:
                lowest_total_price_found = total_price
                best_supplier_url = result["url"]
                chosen_supplier_name = result["name"]
                chosen_shipping_fee = shipping_fee
                print(f"DEBUG: New best supplier: {chosen_supplier_name} with total price ${total_price}")
            elif total_price == lowest_total_price_found:
                # Tie-breaking: keep the first one encountered (which is implicitly handled by iteration order)
                pass

    # If no valid price was found, return None instead of float("inf")
    if lowest_total_price_found == float("inf"):
        return (
            None,
            None,
            "N/A",
            None,
        )  # Return None for price, URL, supplier name, and shipping fee
    else:
        # Return the base price (without shipping) for the sheet update, but shipping fee separately
        base_price_only = lowest_total_price_found - (chosen_shipping_fee or 0)
        return base_price_only, best_supplier_url, chosen_supplier_name, chosen_shipping_fee
