"""
Process entry point. Basically forwards everything to main. Only discoverable part of the
application from the perspective of a program user.
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
