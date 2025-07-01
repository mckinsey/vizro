"""Script to test PyCafe docs links using Playwright."""

from pycafe_utils import test_pycafe_link

if __name__ == "__main__":
    import sys

    links = sys.argv[1:]

    # Test the link
    exit_codes = [
        test_pycafe_link(url=link, wait_for_locator="#dashboard-container", wait_for_text=False) for link in links
    ]

    # Exit with appropriate status code
    sys.exit(any(exit_codes))
