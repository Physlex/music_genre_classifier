"""
This file defines the entry point to the application.
"""

from app import App

if __name__ == "__main__":
    app = App()

    app.init()
    while app.run():
        continue

    if app.error_encountered:
        print(f"Application encountered an unexpected error: {app.error}")
    pass
