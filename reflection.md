# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The initial UML design for PawPal+ includes 6 classes organized around the core concept of generating a personalized daily care schedule for a pet.

| Class | Responsibilities |
|---|---|
| **Owner** | Stores the owner's name, available time (in minutes), and scheduling preferences |
| **Pet** | Represents the animal being cared for — holds its name, species, and a reference to its owner |
| **Task** | Defines a single care activity with a title, duration, priority, category, and whether it's required |
| **ScheduledTask** | Wraps a `Task` with a concrete start/end time and a reason for its placement in the schedule |
| **DailyPlan** | Aggregates the full schedule for a pet — holds the list of scheduled and skipped tasks, total time used, and a summary |
| **Scheduler** | The logic class — takes a pet and a list of tasks and produces a `DailyPlan` via `generate_plan()` |

Key relationships:
- An `Owner` owns one `Pet`
- A `Task` becomes a `ScheduledTask` when placed in the plan
- A `DailyPlan` contains many `ScheduledTask`s and tracks skipped `Task`s
- The `Scheduler` uses the `Pet` (and its owner's constraints) to produce the `DailyPlan`

The design separates data (Owner, Pet, Task) from scheduling logic (Scheduler) and output structure (ScheduledTask, DailyPlan), following a clean single-responsibility pattern.

**b. Design changes**

Yes, the design evolved after reviewing AI feedback on the initial skeleton. The following changes were made:

1. **Converted classes to Python dataclasses** — `Owner`, `Pet`, `Task`, `ScheduledTask`, and `DailyPlan` were refactored from manual `__init__` methods to `@dataclass` decorators. This eliminated boilerplate and made the field definitions cleaner and easier to read. `field(default_factory=list)` was used for mutable defaults like `preferences`, `scheduled_tasks`, and `skipped_tasks`.

2. **Added a `Priority` enum** — The `priority` field on `Task` was originally a plain string (`"low"`, `"medium"`, `"high"`) with no validation. AI feedback flagged this as a potential source of silent bugs when sorting. A `Priority(str, Enum)` class was added to enforce valid values at the type level.

3. **Split `Scheduler.generate_plan()` into private helper stubs** — AI feedback identified that putting all scheduling logic into one method would become a bottleneck and be hard to test. The method was decomposed into `_sort_tasks()` and `_allocate()` stubs to keep responsibilities separated and make future testing easier.

4. **Added `Task.species` field** — The original `Task` had no way to indicate which pet species it applied to. AI feedback flagged that the scheduler had no basis to filter tasks by pet type. A `species: list[str]` field was added; an empty list means the task applies to all species, and `_filter_by_species()` in the `Scheduler` handles the filtering.

5. **Added `DailyPlan.owner` property** — The original design required chaining `plan.pet.owner` to access owner constraints. A `@property` was added to `DailyPlan` to expose the owner directly, making the relationship explicit and access cleaner.

6. **Added time parsing helpers to `Scheduler`** — `start_time` was a plain string with no parsing logic anywhere. AI feedback flagged this as a likely source of bugs. Two private methods, `_parse_time()` and `_format_time()`, were added to centralize all `"HH:MM"` arithmetic in one place.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
