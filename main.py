from pawpal_system import Owner, Pet, Task, Priority, Scheduler

# --- Setup ---
owner = Owner(name="Jordan", time_available_minutes=120)

# Tasks added deliberately OUT OF ORDER to demonstrate sort_by_time():
#   Morning walk  08:00  ← added first
#   Breakfast     07:30  ← earlier time, added second
#   Fetch         (none) ← no time hint, added third
#   Medication    06:45  ← earliest time, added fourth
#   Brush coat    (none) ← weekly, no time
#   Vet appt      08:00  ← deliberate same-time conflict with Morning walk
mochi = Pet(name="Mochi", species="dog", owner=owner)
mochi.add_task(Task("Morning walk",      duration_minutes=30, priority=Priority.HIGH,   is_required=True,  frequency="daily",     scheduled_time="08:00"))
mochi.add_task(Task("Breakfast feeding", duration_minutes=10, priority=Priority.HIGH,   frequency="daily",                         scheduled_time="07:30"))
mochi.add_task(Task("Fetch / playtime",  duration_minutes=20, priority=Priority.MEDIUM, frequency="daily"))
mochi.add_task(Task("Medication",        duration_minutes=5,  priority=Priority.HIGH,   frequency="daily",                         scheduled_time="06:45"))
mochi.add_task(Task("Brush coat",        duration_minutes=15, priority=Priority.LOW,    frequency="weekly"))
# Deliberate same-pet conflict: Vet appointment overlaps Morning walk (both at 08:00)
mochi.add_task(Task("Vet appointment",   duration_minutes=20, priority=Priority.HIGH,   frequency="as_needed",                     scheduled_time="08:00"))

luna = Pet(name="Luna", species="cat", owner=owner)
luna.add_task(Task("Breakfast feeding",  duration_minutes=5,  priority=Priority.HIGH,   is_required=True,  frequency="daily",  species=["cat"], scheduled_time="07:30"))
luna.add_task(Task("Litter box clean",   duration_minutes=10, priority=Priority.HIGH,   frequency="daily",  species=["cat"]))
luna.add_task(Task("Interactive play",   duration_minutes=15, priority=Priority.MEDIUM, frequency="daily"))
luna.add_task(Task("Eye drops",          duration_minutes=5,  priority=Priority.HIGH,   frequency="daily",                      scheduled_time="06:30"))
luna.add_task(Task("Nail trim",          duration_minutes=20, priority=Priority.LOW,    frequency="weekly"))

owner.add_pet(mochi)
owner.add_pet(luna)

scheduler = Scheduler()

# --- Pre-schedule conflict check (catches same-pet overlaps before allocation) ---
print("=" * 60)
print("  Pre-Schedule Conflict Check")
print("=" * 60)
pre_warnings = scheduler.check_time_hint_conflicts(owner)
if pre_warnings:
    for w in pre_warnings:
        print(f"  WARNING: {w}")
else:
    print("  No pre-schedule conflicts found.")

# Mark one recurring task complete through Scheduler.
# This also creates the next pending occurrence for daily/weekly tasks.
next_occurrence = scheduler.mark_task_complete(mochi, mochi.tasks[2])

# --- Feature 3: Recurring tasks — only due tasks are scheduled ---
today = "2026-03-25"
plans = scheduler.generate_plans_for_owner(owner, start_time="07:30", today=today)

# --- Display per-pet plans ---
print("=" * 60)
print(f"  Today's Schedule  —  Owner: {owner.name}  ({today})")
print("=" * 60)

if next_occurrence:
    print(
        f"Created next recurring task for {mochi.name}: "
        f"{next_occurrence.title} ({next_occurrence.frequency})"
    )

for plan in plans:
    print(f"\n[ {plan.pet.name} ({plan.pet.species}) ]")
    print(f"  Time budget : {owner.time_available_minutes} min")
    print(f"  Time used   : {plan.total_minutes} min")

    if plan.scheduled_tasks:
        print("\n  Scheduled tasks:")
        for st in plan.scheduled_tasks:
            flag = " *" if st.task.is_required else ""
            pin  = f" [pinned {st.task.scheduled_time}]" if st.task.scheduled_time else ""
            print(f"    {st.start_time} - {st.end_time}  {st.task.title}{flag}{pin}  ({st.task.priority.value}, {st.task.frequency})")

    if plan.skipped_tasks:
        print("\n  Skipped tasks (over time budget or not due today):")
        for t in plan.skipped_tasks:
            print(f"    - {t.title} ({t.duration_minutes} min, {t.frequency})")

    print(f"\n  Summary: {plan.summary}")

# --- Feature 5: Shared time budget guard ---
total_used = sum(plan.total_minutes for plan in plans)
print("\n" + "=" * 60)

# --- Sorting demo ---
# Tasks were added in insertion order (08:00, 07:30, none, 06:45, none, 08:00).
# sort_by_time() uses a lambda key: task.scheduled_time or "99:99"
# so "HH:MM" strings sort lexicographically and tasks with no time go last.
print("  Sorting demo: Mochi tasks sorted by HH:MM scheduled_time")
print("  (original insertion order vs. sorted order)")
print("=" * 60)
print("  BEFORE (insertion order):")
for task in mochi.tasks:
    when = task.scheduled_time if task.scheduled_time else "(no time)"
    print(f"    {when:>10}  {task.title}")

sorted_mochi = scheduler.sort_by_time(mochi.tasks)
print("\n  AFTER  (sorted by lambda key):")
for task in sorted_mochi:
    when = task.scheduled_time if task.scheduled_time else "(no time)"
    print(f"    {when:>10}  {task.title}")

# --- Filtering demo ---
# filter_by_status_or_pet() accepts optional is_completed and pet_name filters.
# Filters are cumulative (AND logic): both conditions must be satisfied.

print("\n" + "=" * 60)
print("  Filtering demo 1: completed tasks for Mochi only")
print("=" * 60)
completed_mochi = scheduler.filter_by_status_or_pet(owner, is_completed=True, pet_name="Mochi")
if completed_mochi:
    for pet, task in completed_mochi:
        print(f"  [{pet.name}] {task.title}  completed={task.is_completed}")
else:
    print("  (no completed tasks for Mochi)")

print("\n" + "=" * 60)
print("  Filtering demo 2: all pending tasks across all pets")
print("=" * 60)
pending_tasks = scheduler.filter_by_status_or_pet(owner, is_completed=False)
for pet, task in pending_tasks:
    print(f"  [{pet.name}] {task.title}  completed={task.is_completed}")

print("\n" + "=" * 60)
print(f"  Total time used across all pets: {total_used} / {owner.time_available_minutes} min")
if total_used > owner.time_available_minutes:
    print("  WARNING: Total scheduled time exceeds owner's available time!")
else:
    print("  OK: Within owner's time budget.")

# --- Feature 4: Post-schedule conflict detection (same-pet + cross-pet) ---
print("\n" + "=" * 60)
print("  Post-Schedule Conflict Warnings")
print("=" * 60)
warnings = scheduler.get_conflict_warnings(plans)
if warnings:
    for w in warnings:
        print(f"  WARNING: {w}")
else:
    print("  No post-schedule conflicts found.")

# --- Feature 2: Filter tasks by pet / status / priority ---
print("\n" + "=" * 60)
print("  Filter demo: all HIGH-priority pending tasks")
print("=" * 60)
filtered = scheduler.filter_tasks(owner, status="pending", priority="high")
for pet, task in filtered:
    print(f"  [{pet.name}] {task.title} — {task.priority.value}, {task.frequency}")

print("\n" + "=" * 60)

# --- Recurring-task fix demo: last_completed_date propagation ---
# mark_task_complete now passes task.last_completed_date (set to today by
# mark_complete()) into the new Task, so is_due_today() sees a recent date
# and correctly skips the new weekly occurrence until 7 days have passed.
print("  Recurring-task fix demo: last_completed_date propagation")
print("=" * 60)

from pawpal_system import is_due_today  # noqa: E402 (local import for demo clarity)

# --- Weekly task: "Brush coat" ---
# Find the original Brush coat task (not yet completed in this demo path).
brush_coat = next(t for t in mochi.tasks if t.title == "Brush coat" and not t.is_completed)
next_weekly = scheduler.mark_task_complete(mochi, brush_coat)

weekly_due = is_due_today(next_weekly)
print(f"\n  Weekly task  : '{next_weekly.title}'")
print(f"  last_completed_date on new task : '{next_weekly.last_completed_date}'")
print(f"  is_due_today()  -> {weekly_due}")
print(f"  Expected        -> False  (just completed; 7 days have not passed)")
assert not weekly_due, "BUG: new weekly occurrence should NOT be due today"
print("  PASS: new weekly occurrence is correctly NOT due today.")

# --- Daily task: demonstrate that daily occurrences are always due ---
demo_daily = Task("Demo daily walk", duration_minutes=10, priority=Priority.LOW, frequency="daily")
mochi.add_task(demo_daily)
next_daily = scheduler.mark_task_complete(mochi, demo_daily)

daily_due = is_due_today(next_daily)
print(f"\n  Daily task   : '{next_daily.title}'")
print(f"  last_completed_date on new task : '{next_daily.last_completed_date}'")
print(f"  is_due_today()  -> {daily_due}")
print(f"  Expected        -> True  (daily tasks are always due)")
assert daily_due, "BUG: new daily occurrence should always be due today"
print("  PASS: new daily occurrence is correctly due today.")

print("\n" + "=" * 60)
