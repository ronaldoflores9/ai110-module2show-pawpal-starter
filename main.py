from pawpal_system import Owner, Pet, Task, Priority, Scheduler

# --- Setup ---
owner = Owner(name="Jordan", time_available_minutes=120)

mochi = Pet(name="Mochi", species="dog", owner=owner)
mochi.add_task(Task("Morning walk",     duration_minutes=30, priority=Priority.HIGH,   is_required=True))
mochi.add_task(Task("Breakfast feeding", duration_minutes=10, priority=Priority.HIGH,   frequency="daily"))
mochi.add_task(Task("Fetch / playtime", duration_minutes=20, priority=Priority.MEDIUM, frequency="daily"))
mochi.add_task(Task("Brush coat",       duration_minutes=15, priority=Priority.LOW,    frequency="weekly"))

luna = Pet(name="Luna", species="cat", owner=owner)
luna.add_task(Task("Breakfast feeding", duration_minutes=5,  priority=Priority.HIGH,   is_required=True, species=["cat"]))
luna.add_task(Task("Litter box clean",  duration_minutes=10, priority=Priority.HIGH,   frequency="daily", species=["cat"]))
luna.add_task(Task("Interactive play",  duration_minutes=15, priority=Priority.MEDIUM, frequency="daily"))
luna.add_task(Task("Nail trim",         duration_minutes=20, priority=Priority.LOW,    frequency="weekly"))

owner.add_pet(mochi)
owner.add_pet(luna)

# --- Generate plans ---
scheduler = Scheduler()
plans = scheduler.generate_plans_for_owner(owner)

# --- Display ---
print("=" * 50)
print(f"  Today's Schedule  —  Owner: {owner.name}")
print("=" * 50)

for plan in plans:
    print(f"\n[ {plan.pet.name} ({plan.pet.species}) ]")
    print(f"  Time budget : {owner.time_available_minutes} min")
    print(f"  Time used   : {plan.total_minutes} min")
    print()

    if plan.scheduled_tasks:
        print("  Scheduled tasks:")
        for st in plan.scheduled_tasks:
            flag = " *" if st.task.is_required else ""
            print(f"    {st.start_time} - {st.end_time}  {st.task.title}{flag}  ({st.task.priority.value} priority)")

    if plan.skipped_tasks:
        print("\n  Skipped tasks (over time budget):")
        for t in plan.skipped_tasks:
            print(f"    - {t.title} ({t.duration_minutes} min)")

    print(f"\n  Summary: {plan.summary}")

print("\n" + "=" * 50)
