"""Script to test PyCafe docs links using Playwright."""

from pycafe_utils import test_pycafe_link

if __name__ == "__main__":
    import sys

    links = sys.argv[1:]

    # Test the link
    for link in links:
        success = test_pycafe_link(url=link, wait_for_locator="#dashboard-container", wait_for_text=False)

        # Exit with appropriate status code
        sys.exit(0 if success else 1)
