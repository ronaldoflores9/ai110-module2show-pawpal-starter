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


@dataclass
class Pet:
    name: str
    species: str
    owner: Owner


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: Priority
    category: str = ""
    is_required: bool = False
    species: list[str] = field(default_factory=list)  # empty = applies to all species


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
        return self.pet.owner


class Scheduler:
    def generate_plan(self, pet: Pet, tasks: list[Task], start_time: str = "08:00") -> DailyPlan:
        filtered = self._filter_by_species(tasks, pet.species)
        sorted_tasks = self._sort_tasks(filtered)
        scheduled, skipped = self._allocate(sorted_tasks, pet.owner.time_available_minutes, start_time)
        plan = DailyPlan(pet=pet, scheduled_tasks=scheduled, skipped_tasks=skipped)
        plan.total_minutes = sum(st.task.duration_minutes for st in scheduled)
        plan.summary = self._build_summary(plan)
        return plan

    def _filter_by_species(self, tasks: list[Task], species: str) -> list[Task]:
        return [t for t in tasks if not t.species or species in t.species]

    def _sort_tasks(self, tasks: list[Task]) -> list[Task]:
        order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        return sorted(tasks, key=lambda t: (not t.is_required, order.get(t.priority, 99)))

    def _allocate(self, tasks: list[Task], budget_minutes: int, start_time: str) -> tuple[list[ScheduledTask], list[Task]]:
        scheduled: list[ScheduledTask] = []
        skipped: list[Task] = []
        current = self._parse_time(start_time)

        for task in tasks:
            if current + task.duration_minutes <= budget_minutes:
                end = current + task.duration_minutes
                scheduled.append(ScheduledTask(
                    task=task,
                    start_time=self._format_time(current),
                    end_time=self._format_time(end),
                    reason="scheduled within available time",
                ))
                current = end
            else:
                skipped.append(task)

        return scheduled, skipped

    def _build_summary(self, plan: DailyPlan) -> str:
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

    def _format_time(self, minutes: int) -> str:
        """Convert minutes since midnight to 'HH:MM'."""
        return f"{minutes // 60:02d}:{minutes % 60:02d}"
