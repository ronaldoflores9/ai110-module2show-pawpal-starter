from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Owner:
    name: str
    time_available_minutes: int
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


@dataclass
class Pet:
    name: str
    species: str
    owner: Owner
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet's task list."""
        self.tasks.append(task)

    def get_pending_tasks(self) -> list[Task]:
        """Return all tasks that have not yet been completed."""
        return [t for t in self.tasks if not t.is_completed]


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: Priority
    category: str = ""
    is_required: bool = False
    species: list[str] = field(default_factory=list)  # empty = applies to all species
    frequency: str = "daily"  # e.g. "daily", "weekly", "as_needed"
    is_completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_completed = True


@dataclass
class ScheduledTask:
    task: Task
    start_time: str
    end_time: str
    reason: str


@dataclass
class DailyPlan:
    pet: Pet
    scheduled_tasks: list[ScheduledTask] = field(default_factory=list)
    skipped_tasks: list[Task] = field(default_factory=list)
    total_minutes: int = 0
    summary: str = ""

    @property
    def owner(self) -> Owner:
        """Return the owner of the pet this plan belongs to."""
        return self.pet.owner


class Scheduler:
    def generate_plan(self, pet: Pet, tasks: list[Task], start_time: str = "08:00") -> DailyPlan:
        """Build and return a DailyPlan for a pet from the given task list."""
        filtered = self._filter_by_species(tasks, pet.species)
        sorted_tasks = self._sort_tasks(filtered)
        scheduled, skipped = self._allocate(sorted_tasks, pet.owner.time_available_minutes, start_time)
        plan = DailyPlan(pet=pet, scheduled_tasks=scheduled, skipped_tasks=skipped)
        plan.total_minutes = sum(st.task.duration_minutes for st in scheduled)
        plan.summary = self._build_summary(plan)
        return plan

    def _filter_by_species(self, tasks: list[Task], species: str) -> list[Task]:
        """Remove tasks that do not apply to the given species."""
        return [t for t in tasks if not t.species or species in t.species]

    def _sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks so required and high-priority items come first."""
        order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        return sorted(tasks, key=lambda t: (not t.is_required, order.get(t.priority, 99)))

    def _allocate(self, tasks: list[Task], budget_minutes: int, start_time: str) -> tuple[list[ScheduledTask], list[Task]]:
        """Fit tasks into the time budget, returning scheduled and skipped lists."""
        scheduled: list[ScheduledTask] = []
        skipped: list[Task] = []
        elapsed = 0
        wall = self._parse_time(start_time)

        for task in tasks:
            if elapsed + task.duration_minutes <= budget_minutes:
                end_wall = wall + task.duration_minutes
                scheduled.append(ScheduledTask(
                    task=task,
                    start_time=self._format_time(wall),
                    end_time=self._format_time(end_wall),
                    reason="scheduled within available time",
                ))
                elapsed += task.duration_minutes
                wall = end_wall
            else:
                skipped.append(task)

        return scheduled, skipped

    def _build_summary(self, plan: DailyPlan) -> str:
        """Compose a human-readable summary string for the plan."""
        return (
            f"{plan.pet.name}'s plan: "
            f"{len(plan.scheduled_tasks)} tasks scheduled, "
            f"{len(plan.skipped_tasks)} skipped, "
            f"{plan.total_minutes} minutes total."
        )

    def _parse_time(self, time_str: str) -> int:
        """Convert 'HH:MM' to minutes since midnight."""
        h, m = time_str.split(":")
        return int(h) * 60 + int(m)

    def generate_plans_for_owner(self, owner: Owner, start_time: str = "08:00") -> list[DailyPlan]:
        """Generate a DailyPlan for each pet owned, using that pet's pending tasks."""
        return [
            self.generate_plan(pet, pet.get_pending_tasks(), start_time)
            for pet in owner.pets
        ]

    def _format_time(self, minutes: int) -> str:
        """Convert minutes since midnight to 'HH:MM'."""
        return f"{minutes // 60:02d}:{minutes % 60:02d}"
