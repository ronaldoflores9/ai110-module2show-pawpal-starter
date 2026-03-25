from pawpal_system import Owner, Pet, Task, Priority


def make_owner():
    return Owner(name="Maria", time_available_minutes=60)


def make_pet(owner):
    return Pet(name="Buddy", species="dog", owner=owner)


def make_task():
    return Task(title="Walk", duration_minutes=30, priority=Priority.HIGH)


def test_mark_complete_changes_task_status():
    task = make_task()
    assert task.is_completed is False
    task.mark_complete()
    assert task.is_completed is True


def test_add_task_increases_pet_task_count():
    owner = make_owner()
    pet = make_pet(owner)
    assert len(pet.tasks) == 0
    pet.add_task(make_task())
    assert len(pet.tasks) == 1
