"""Enumerations shared across models, schemas and the solver."""

from enum import StrEnum


class RoomType(StrEnum):
    CLASSROOM = "classroom"
    GYM = "gym"
    MUSIC = "music"
    COMPUTER_LAB = "computer_lab"
    OTHER = "other"


class ScheduleStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class UserRole(StrEnum):
    ADMIN = "admin"
    HEAD_OF_STUDIES = "head_of_studies"
    TEACHER = "teacher"
