"""Create a user account from the command line.

This is how a school creates its first administrator: there is no public
registration endpoint, and the development seed must never be run against real
data. The password is prompted for rather than passed as an argument, so it does
not end up in the shell history or in the process list.

    uv run python scripts/create_user.py
"""

import sys
from getpass import getpass

from app.core.db import SessionLocal
from app.core.errors import DomainError
from app.models.enums import UserRole
from app.services.user_service import MINIMUM_PASSWORD_LENGTH, UserService

ROLES = [role.value for role in UserRole]


def ask_role() -> UserRole:
    print("\nRoles:")
    for index, role in enumerate(ROLES, start=1):
        print(f"  {index}) {role}")
    while True:
        answer = input(f"Role [1-{len(ROLES)}, default 1]: ").strip() or "1"
        if answer.isdigit() and 1 <= int(answer) <= len(ROLES):
            return UserRole(ROLES[int(answer) - 1])
        print("Please choose one of the listed numbers.")


def ask_password() -> str:
    while True:
        password = getpass("Password: ")
        if len(password) < MINIMUM_PASSWORD_LENGTH:
            print(f"Too short: at least {MINIMUM_PASSWORD_LENGTH} characters.")
            continue
        if password != getpass("Repeat password: "):
            print("The passwords do not match.")
            continue
        return password


def main() -> int:
    with SessionLocal() as session:
        service = UserService(session)
        if service.count() == 0:
            print("No user exists yet. This account will be the first administrator.")

        email = input("Email: ").strip()
        if not email:
            print("An email is required.", file=sys.stderr)
            return 1

        role = ask_role()
        password = ask_password()

        try:
            user = service.create(email=email, password=password, role=role)
        except DomainError as error:
            print(f"\n{error.message}", file=sys.stderr)
            return 1

        print(f"\nCreated user {user.email} with role {user.role}.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
